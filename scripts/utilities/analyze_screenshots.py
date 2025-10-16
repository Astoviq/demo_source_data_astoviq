#!/usr/bin/env python3
"""
Screenshot Analysis Tool
========================

Analyzes screenshot files referenced in config/screenshots.yaml and generates
metadata including dimensions, file size, checksums, and optional OCR-based
text extraction for caption assistance.

Usage:
    python3 scripts/utilities/analyze_screenshots.py --manifest config/screenshots.yaml --out data/metadata/screenshots_analysis.json

Following WARP.md principles:
- Configuration-driven: Reads from YAML manifest
- No hard-coding: All paths and settings from config
- Validation: Catches missing files before docs updates
"""

import argparse
import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import yaml
    from PIL import Image
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install: pip install PyYAML Pillow")
    print(f"Import error: {e}")
    sys.exit(1)


class ScreenshotAnalyzer:
    """Analyzes screenshot files and extracts metadata."""
    
    def __init__(self, manifest_path: str, project_root: str = "."):
        self.manifest_path = Path(manifest_path)
        self.project_root = Path(project_root)
        self.analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "manifest_file": str(self.manifest_path),
            "total_screenshots": 0,
            "valid_files": 0,
            "missing_files": 0,
            "errors": [],
            "screenshots": {}
        }
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load screenshot manifest from YAML file."""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Screenshot manifest not found: {self.manifest_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in manifest: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for integrity checking."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def analyze_image(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single image file and extract metadata."""
        result = {
            "file_path": str(file_path),
            "exists": False,
            "file_size_bytes": 0,
            "file_size_human": "",
            "dimensions": {"width": 0, "height": 0},
            "aspect_ratio": 0.0,
            "format": "",
            "mode": "",
            "dpi": {"x": 72, "y": 72},
            "file_hash": "",
            "last_modified": "",
            "analysis_status": "pending"
        }
        
        try:
            if not file_path.exists():
                result["analysis_status"] = "missing_file"
                self.analysis_results["errors"].append(f"File not found: {file_path}")
                return result
                
            # File exists
            result["exists"] = True
            
            # File stats
            stat = file_path.stat()
            result["file_size_bytes"] = stat.st_size
            result["file_size_human"] = self._format_file_size(stat.st_size)
            result["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            result["file_hash"] = self.calculate_file_hash(file_path)
            
            # Image analysis with PIL
            with Image.open(file_path) as img:
                result["dimensions"] = {"width": img.width, "height": img.height}
                result["aspect_ratio"] = round(img.width / img.height, 3)
                result["format"] = img.format
                result["mode"] = img.mode
                
                # DPI information if available
                if hasattr(img, 'info') and 'dpi' in img.info:
                    result["dpi"] = {"x": img.info['dpi'][0], "y": img.info['dpi'][1]}
            
            result["analysis_status"] = "success"
            
        except Exception as e:
            result["analysis_status"] = f"error: {str(e)}"
            self.analysis_results["errors"].append(f"Error analyzing {file_path}: {str(e)}")
            
        return result
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def extract_text_content(self, file_path: Path) -> Optional[str]:
        """
        Optional OCR-based text extraction for caption assistance.
        Requires tesseract and pytesseract - gracefully skips if not available.
        """
        try:
            import pytesseract
            from PIL import Image
            
            with Image.open(file_path) as img:
                # Extract text using OCR
                text = pytesseract.image_to_string(img, config='--psm 6')
                # Clean up the text
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                return ' | '.join(lines[:5])  # First 5 non-empty lines
                
        except ImportError:
            # OCR dependencies not available - skip gracefully
            return None
        except Exception as e:
            return f"OCR_ERROR: {str(e)}"
    
    def analyze_all_screenshots(self) -> Dict[str, Any]:
        """Analyze all screenshots referenced in the manifest."""
        try:
            manifest = self.load_manifest()
            screenshots_config = manifest.get('screenshots', [])
            
            self.analysis_results["total_screenshots"] = len(screenshots_config)
            
            for screenshot_config in screenshots_config:
                screenshot_id = screenshot_config.get('id', 'unknown')
                file_path_str = screenshot_config.get('file', '')
                
                if not file_path_str:
                    self.analysis_results["errors"].append(f"Screenshot {screenshot_id} missing file path")
                    continue
                
                # Resolve file path relative to project root
                file_path = self.project_root / file_path_str
                
                # Analyze the image
                analysis = self.analyze_image(file_path)
                
                # Add manifest metadata
                analysis.update({
                    "manifest_id": screenshot_id,
                    "manifest_title": screenshot_config.get('title', ''),
                    "manifest_tags": screenshot_config.get('tags', []),
                    "used_in_docs": screenshot_config.get('used_in', []),
                    "display_config": screenshot_config.get('display', {}),
                })
                
                # Optional OCR text extraction
                if analysis["exists"] and analysis["analysis_status"] == "success":
                    extracted_text = self.extract_text_content(file_path)
                    if extracted_text:
                        analysis["extracted_text"] = extracted_text
                    
                    self.analysis_results["valid_files"] += 1
                else:
                    self.analysis_results["missing_files"] += 1
                
                self.analysis_results["screenshots"][screenshot_id] = analysis
                
        except Exception as e:
            self.analysis_results["errors"].append(f"Analysis failed: {str(e)}")
            
        return self.analysis_results
    
    def save_analysis(self, output_path: str) -> None:
        """Save analysis results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis complete: {output_file}")
        print(f"Screenshots analyzed: {self.analysis_results['total_screenshots']}")
        print(f"Valid files: {self.analysis_results['valid_files']}")
        print(f"Missing files: {self.analysis_results['missing_files']}")
        
        if self.analysis_results["errors"]:
            print(f"Errors encountered: {len(self.analysis_results['errors'])}")
            for error in self.analysis_results["errors"]:
                print(f"  - {error}")


def main():
    """Main entry point for the screenshot analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze screenshots referenced in manifest file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze screenshots using default paths
  python3 scripts/utilities/analyze_screenshots.py --manifest config/screenshots.yaml --out data/metadata/screenshots_analysis.json
  
  # Analyze with custom project root
  python3 scripts/utilities/analyze_screenshots.py --manifest config/screenshots.yaml --out analysis.json --root /path/to/project
        """
    )
    
    parser.add_argument(
        '--manifest',
        required=True,
        help='Path to screenshots YAML manifest file'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Output path for analysis JSON file'
    )
    
    parser.add_argument(
        '--root',
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = ScreenshotAnalyzer(args.manifest, args.root)
        analyzer.analyze_all_screenshots()
        analyzer.save_analysis(args.out)
        
        # Exit with error code if there were missing files or errors
        if analyzer.analysis_results["missing_files"] > 0 or analyzer.analysis_results["errors"]:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()