#!/usr/bin/env python3
"""
Image Link Validator
===================

Validates image references in markdown documentation files to ensure:
- All referenced images exist
- Images are within the screenshots directory
- Images are registered in the screenshot manifest

Usage:
    python3 scripts/validation/validate_image_links.py

Following WARP.md principles:
- Configuration-driven: Validates against manifest
- Automated: Prevents broken documentation
- Comprehensive: Checks all documentation files
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Any

try:
    import yaml
except ImportError:
    print("Error: Missing PyYAML dependency. Please install: pip install PyYAML")
    sys.exit(1)


class ImageLinkValidator:
    """Validates image links in markdown documentation."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        
    def load_manifest(self) -> Dict[str, Any]:
        """Load screenshot manifest if available."""
        manifest_path = self.project_root / "config" / "screenshots.yaml"
        if not manifest_path.exists():
            return {"screenshots": []}
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {"screenshots": []}
        except Exception as e:
            self.warnings.append(f"Could not load screenshot manifest: {e}")
            return {"screenshots": []}
    
    def get_manifest_files(self, manifest: Dict[str, Any]) -> Set[str]:
        """Get set of files registered in manifest."""
        files = set()
        for screenshot in manifest.get("screenshots", []):
            file_path = screenshot.get("file", "")
            if file_path:
                files.add(file_path)
        return files
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files to validate."""
        md_files = []
        
        # Core documentation files
        core_files = ["README.md", "QUICKSTART.md", "SCREENSHOTS.md"]
        for filename in core_files:
            file_path = self.project_root / filename
            if file_path.exists():
                md_files.append(file_path)
                
        # Additional docs directory files (but skip auto-generated ones)
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for md_file in docs_dir.rglob("*.md"):
                # Skip auto-generated files
                if md_file.name in ["SCHEMA.md", "CSV_MAPPINGS.md"]:
                    continue
                md_files.append(md_file)
                
        return md_files
    
    def extract_image_references(self, md_file: Path) -> List[Dict[str, str]]:
        """Extract all image references from a markdown file."""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Could not read {md_file}: {e}")
            return []
            
        images = []
        for match in self.image_pattern.finditer(content):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # Skip external URLs and data URIs
            if (image_path.startswith(('http://', 'https://', 'data:', 'ftp://')) or
                image_path.startswith('https://img.shields.io/')):
                continue
                
            images.append({
                "alt_text": alt_text,
                "path": image_path,
                "file": str(md_file),
                "line": content[:match.start()].count('\\n') + 1
            })
            
        return images
    
    def validate_image_reference(self, image_ref: Dict[str, str], 
                               manifest_files: Set[str]) -> List[str]:
        """Validate a single image reference."""
        issues = []
        image_path = image_ref["path"]
        source_file = image_ref["file"]
        line_num = image_ref["line"]
        
        # Convert to absolute path
        if not Path(image_path).is_absolute():
            absolute_path = (self.project_root / image_path)
        else:
            absolute_path = Path(image_path)
            
        # Check if file exists
        if not absolute_path.exists():
            issues.append(f"Missing image: {image_path} (referenced in {source_file}:{line_num})")
            return issues
            
        # Check if image is in screenshots directory (for relative paths)
        if not Path(image_path).is_absolute():
            if not image_path.startswith("screenshots/"):
                issues.append(f"Image outside screenshots directory: {image_path} (referenced in {source_file}:{line_num})")
            
        # Check if image is registered in manifest
        if manifest_files and image_path not in manifest_files:
            issues.append(f"Image not in manifest: {image_path} (referenced in {source_file}:{line_num})")
            
        # Validate alt text
        alt_text = image_ref.get("alt_text", "")
        if not alt_text or len(alt_text.strip()) < 10:
            issues.append(f"Missing or insufficient alt text for {image_path} (referenced in {source_file}:{line_num})")
            
        return issues
    
    def validate_all_images(self) -> None:
        """Validate all image references in documentation."""
        print("🔍 Validating image references in documentation...")
        
        # Load manifest
        manifest = self.load_manifest()
        manifest_files = self.get_manifest_files(manifest)
        
        # Find markdown files
        md_files = self.find_markdown_files()
        print(f"📄 Found {len(md_files)} markdown files to validate")
        
        total_images = 0
        valid_images = 0
        
        # Process each file
        for md_file in md_files:
            print(f"  📋 Checking {md_file.relative_to(self.project_root)}")
            
            image_refs = self.extract_image_references(md_file)
            total_images += len(image_refs)
            
            for image_ref in image_refs:
                issues = self.validate_image_reference(image_ref, manifest_files)
                if issues:
                    self.errors.extend(issues)
                else:
                    valid_images += 1
                    
        # Summary
        print(f"\\n📊 Validation Summary:")
        print(f"  📄 Files checked: {len(md_files)}")
        print(f"  🖼️  Images found: {total_images}")
        print(f"  ✅ Valid images: {valid_images}")
        print(f"  ❌ Issues found: {len(self.errors)}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")
        
        # Report issues
        if self.warnings:
            print("\\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
                
        if self.errors:
            print("\\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
            return False
            
        print("\\n✅ All image references are valid!")
        return True


def main():
    """Main entry point for image link validator."""
    parser = argparse.ArgumentParser(
        description="Validate image references in markdown documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all image references
  python3 scripts/validation/validate_image_links.py
  
  # Validate with custom project root
  python3 scripts/validation/validate_image_links.py --root /path/to/project
        """
    )
    
    parser.add_argument(
        '--root',
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    try:
        validator = ImageLinkValidator(args.root)
        success = validator.validate_all_images()
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()