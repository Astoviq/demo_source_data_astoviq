#!/usr/bin/env python3
"""
Screenshots Documentation Generator
==================================

Generates SCREENSHOTS.md from Jinja2 template using manifest and analysis data.

Usage:
    python3 scripts/utilities/generate_screenshots_doc.py \
        --manifest config/screenshots.yaml \
        --analysis data/metadata/screenshots_analysis.json \
        --template templates/documentation/screenshots.md.j2 \
        --out SCREENSHOTS.md

Following WARP.md principles:
- Configuration-driven: Uses YAML manifest and JSON analysis
- Template-based: Jinja2 templates for maintainable documentation
- Automated: Prevents manual documentation drift
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml
    from jinja2 import Template, Environment, FileSystemLoader
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install: pip install PyYAML Jinja2")
    print(f"Import error: {e}")
    sys.exit(1)


class ScreenshotsDocGenerator:
    """Generates SCREENSHOTS.md from template and data sources."""
    
    def __init__(self, manifest_path: str, analysis_path: str, template_path: str):
        self.manifest_path = Path(manifest_path)
        self.analysis_path = Path(analysis_path)
        self.template_path = Path(template_path)
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load screenshot manifest from YAML file."""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in manifest: {e}")
    
    def load_analysis(self) -> Dict[str, Any]:
        """Load screenshot analysis from JSON file."""
        try:
            with open(self.analysis_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in analysis file: {e}")
    
    def load_template(self) -> Template:
        """Load Jinja2 template."""
        try:
            env = Environment(
                loader=FileSystemLoader(self.template_path.parent),
                trim_blocks=True,
                lstrip_blocks=True
            )
            return env.get_template(self.template_path.name)
        except Exception as e:
            raise ValueError(f"Error loading template {self.template_path}: {e}")
    
    def merge_data(self, manifest: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Merge manifest and analysis data for template rendering."""
        
        # Start with analysis summary
        template_data = {
            "generation_timestamp": datetime.now().isoformat(),
            "manifest_file": str(self.manifest_path),
            "analysis_timestamp": analysis.get("analysis_timestamp", "unknown"),
            "total_screenshots": analysis.get("total_screenshots", 0),
            "valid_files": analysis.get("valid_files", 0),
            "missing_files": analysis.get("missing_files", 0),
            "errors": analysis.get("errors", []),
            "screenshots": []
        }
        
        # Merge screenshot data
        analysis_screenshots = analysis.get("screenshots", {})
        
        for screenshot_config in manifest.get("screenshots", []):
            screenshot_id = screenshot_config.get("id", "unknown")
            analysis_data = analysis_screenshots.get(screenshot_id, {})
            
            # Combine manifest and analysis data
            merged_screenshot = {
                # From manifest
                "id": screenshot_id,
                "file": screenshot_config.get("file", ""),
                "manifest_title": screenshot_config.get("title", ""),
                "alt": screenshot_config.get("alt", ""),
                "caption": screenshot_config.get("caption", ""),
                "description": screenshot_config.get("description", ""),
                "manifest_tags": screenshot_config.get("tags", []),
                "used_in_docs": screenshot_config.get("used_in", []),
                "display_config": screenshot_config.get("display", {}),
                
                # From analysis
                "exists": analysis_data.get("exists", False),
                "file_size_bytes": analysis_data.get("file_size_bytes", 0),
                "file_size_human": analysis_data.get("file_size_human", "0 B"),
                "dimensions": analysis_data.get("dimensions", {"width": 0, "height": 0}),
                "aspect_ratio": analysis_data.get("aspect_ratio", 0.0),
                "format": analysis_data.get("format", "unknown"),
                "mode": analysis_data.get("mode", "unknown"),
                "file_hash": analysis_data.get("file_hash", ""),
                "last_modified": analysis_data.get("last_modified", "unknown"),
                "analysis_status": analysis_data.get("analysis_status", "unknown"),
                "extracted_text": analysis_data.get("extracted_text", None)
            }
            
            template_data["screenshots"].append(merged_screenshot)
        
        # Sort screenshots by category and title
        template_data["screenshots"].sort(key=lambda x: (
            "architecture" if "architecture" in x["manifest_tags"] else 
            "database" if "database" in x["manifest_tags"] else 
            "query" if "query" in x["manifest_tags"] else "zzz",
            x["manifest_title"]
        ))
        
        return template_data
    
    def generate_documentation(self, output_path: str) -> None:
        """Generate SCREENSHOTS.md file."""
        try:
            # Load data sources
            manifest = self.load_manifest()
            analysis = self.load_analysis()
            template = self.load_template()
            
            # Merge data for template
            template_data = self.merge_data(manifest, analysis)
            
            # Render template
            rendered_content = template.render(**template_data)
            
            # Write output file
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            print(f"✅ Generated: {output_file}")
            print(f"📊 Screenshots documented: {template_data['total_screenshots']}")
            print(f"✅ Valid files: {template_data['valid_files']}")
            
            if template_data['missing_files'] > 0:
                print(f"⚠️ Missing files: {template_data['missing_files']}")
            
            if template_data['errors']:
                print(f"❌ Errors: {len(template_data['errors'])}")
                for error in template_data['errors']:
                    print(f"   - {error}")
                    
        except Exception as e:
            print(f"❌ Error generating documentation: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for the documentation generator."""
    parser = argparse.ArgumentParser(
        description="Generate SCREENSHOTS.md from template and data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with default paths
  python3 scripts/utilities/generate_screenshots_doc.py \
    --manifest config/screenshots.yaml \
    --analysis data/metadata/screenshots_analysis.json \
    --template templates/documentation/screenshots.md.j2 \
    --out SCREENSHOTS.md
    
  # Generate with verbose output
  python3 scripts/utilities/generate_screenshots_doc.py \
    --manifest config/screenshots.yaml \
    --analysis data/metadata/screenshots_analysis.json \
    --template templates/documentation/screenshots.md.j2 \
    --out SCREENSHOTS.md --verbose
        """
    )
    
    parser.add_argument(
        '--manifest',
        required=True,
        help='Path to screenshots YAML manifest file'
    )
    
    parser.add_argument(
        '--analysis',
        required=True,
        help='Path to screenshots analysis JSON file'
    )
    
    parser.add_argument(
        '--template',
        required=True,
        help='Path to Jinja2 template file'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Output path for generated documentation'
    )
    
    args = parser.parse_args()
    
    try:
        generator = ScreenshotsDocGenerator(args.manifest, args.analysis, args.template)
        generator.generate_documentation(args.out)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()