#!/usr/bin/env python3
"""
EuroStyle Source System Documentation Generator

Generates professional PDF documentation for the ERP and Webshop source systems
from the TXT files and configuration settings, following framework compliance rules.

Usage:
    python3 scripts/generate_source_docs.py [--system erp|webshop|all]
"""

import argparse
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import yaml

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib import colors
    from reportlab.platypus.flowables import KeepTogether
except ImportError:
    print("Error: reportlab is required. Install with: pip install reportlab")
    sys.exit(1)

# Framework compliance imports (following your rules)
def get_config(config_file: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file - framework compliance"""
    if config_file is None:
        config_file = Path(__file__).parent.parent / "config" / "documentation_generation.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")

def get_logger(name: str):
    """Get logger instance - framework compliance placeholder"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def get_storage_manager():
    """Get storage manager - framework compliance placeholder"""
    class SimpleStorageManager:
        def ensure_directory_exists(self, path: Path):
            path.mkdir(parents=True, exist_ok=True)
            
        def write_file(self, path: Path, content: bytes):
            with open(path, 'wb') as f:
                f.write(content)
                
        def read_file(self, path: Path) -> str:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    
    return SimpleStorageManager()

class SourceSystemDocGenerator:
    """Professional PDF generator for source system documentation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(__name__)
        self.storage = get_storage_manager()
        
        # PDF styling configuration from YAML
        self.doc_config = config['documentation']
        self.pdf_config = self.doc_config['pdf']
        
        # Color scheme
        self.colors = {
            'primary': HexColor(self.pdf_config['colors']['primary']),
            'secondary': HexColor(self.pdf_config['colors']['secondary']),
            'accent': HexColor(self.pdf_config['colors']['accent'])
        }
        
        # Margins (convert to points)
        self.margins = {k: v * 72/25.4 for k, v in self.pdf_config['margins'].items()}  # mm to points
        
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=self.colors['primary'],
                spaceAfter=30,
                alignment=1,  # Center
                fontName='Helvetica-Bold'
            ),
            'SectionHeader': ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                spaceAfter=20,
                spaceBefore=30,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=self.colors['secondary'],
                borderPadding=5
            ),
            'SubsectionHeader': ParagraphStyle(
                'SubsectionHeader',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['secondary'],
                spaceAfter=12,
                spaceBefore=18,
                fontName='Helvetica-Bold'
            ),
            'BodyText': ParagraphStyle(
                'BodyText',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                fontName='Helvetica'
            ),
            'Code': ParagraphStyle(
                'Code',
                parent=styles['Code'],
                fontSize=9,
                fontName='Courier',
                backgroundColor=colors.lightgrey,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=3
            )
        }
        
        return custom_styles
    
    def create_header_footer(self, canvas, doc, vendor_info: Dict[str, str]):
        """Add header and footer to each page"""
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(self.colors['primary'])
        canvas.drawString(doc.leftMargin, doc.height + 40, vendor_info['name'])
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height + 40, 
                              vendor_info['system_name'])
        
        # Header line
        canvas.setStrokeColor(self.colors['secondary'])
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, doc.height + 30, 
                   doc.width + doc.leftMargin, doc.height + 30)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, 
                         f"© 2024 {vendor_info['name']} - Confidential")
        canvas.drawRightString(doc.width + doc.leftMargin, 30, 
                              f"Page {doc.page}")
        
        # Footer line
        canvas.line(doc.leftMargin, 40, doc.width + doc.leftMargin, 40)
    
    def parse_txt_content(self, txt_content: str) -> Dict[str, str]:
        """Parse structured TXT content into sections"""
        sections = {}
        current_section = None
        current_content = []
        section_started = False
        
        lines = txt_content.split('\n')
        
        for line in lines:
            # Detect section headers (lines with ===)
            if line.startswith('=') and len(line) > 40:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Reset for next section
                current_section = None
                current_content = []
                section_started = True
                continue
            
            # After a === line, look for the section title
            if section_started and line.strip() and not line.startswith('Supplier:'):
                # Check if this looks like a section title - more flexible matching
                stripped_line = line.strip()
                # Match numbered sections (1. EXECUTIVE SUMMARY) or keywords
                is_section_title = (
                    bool(re.match(r'^\d+\.\s+[A-Z][A-Z\s]+$', stripped_line)) or
                    stripped_line.replace('.', '').replace(' ', '').replace('_', '').isupper() or
                    any(keyword in stripped_line.upper() for keyword in 
                      ['EXECUTIVE SUMMARY', 'SYSTEM ARCHITECTURE', 'ENTITY RELATIONSHIP', 
                       'DETAILED ENTITY', 'DATA DICTIONARY', 'BUSINESS RULES', 
                       'INTEGRATION SPECIFICATIONS', 'SAMPLE DATA', 'APPENDICES', 'PLATFORM OVERVIEW',
                       'CUSTOMER JOURNEY', 'EVENT TAXONOMY', 'API SPECIFICATIONS', 'END OF DOCUMENT'])
                )
                
                if is_section_title:
                    current_section = stripped_line
                    section_started = False
                    continue
                # If not a section title, treat as content
                section_started = False
            
            # Add content to current section
            if current_section:
                current_content.append(line)
            elif not current_section and not section_started:
                # Content before first section - skip header info
                continue
        
        # Add final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections
    
    def format_text_content(self, content: str, styles: Dict) -> list:
        """Convert text content to reportlab flowables"""
        flowables = []
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            # Determine style based on content
            if para.startswith('•') or para.startswith('-'):
                # Bullet list
                flowables.append(Paragraph(para.replace('•', '&bull;').replace('-', '&bull;'), 
                                         styles['BodyText']))
            elif para.upper() == para and len(para.split()) <= 5:
                # All caps short text = subsection header
                flowables.append(Paragraph(para, styles['SubsectionHeader']))
            elif para.startswith('Field Name') or para.startswith('customer_id'):
                # Data dictionary table content
                flowables.append(Paragraph(f"<font name='Courier'>{para}</font>", 
                                         styles['Code']))
            else:
                # Regular paragraph
                flowables.append(Paragraph(para, styles['BodyText']))
                
            flowables.append(Spacer(1, 6))
        
        return flowables
    
    def generate_erp_pdf(self) -> Path:
        """Generate ERP system documentation PDF"""
        self.logger.info("Generating ERP system documentation PDF...")
        
        # Load TXT content
        txt_file = Path("docs/source_systems/erp_source_system.txt")
        txt_content = self.storage.read_file(txt_file)
        
        # Parse content into sections
        sections = self.parse_txt_content(txt_content)
        
        # Create PDF
        output_path = Path(self.doc_config['output_directory']) / "EuroStyle_ERP_Documentation.pdf"
        self.storage.ensure_directory_exists(output_path.parent)
        
        vendor_info = self.doc_config['erp_vendor']
        
        def add_header_footer(canvas, doc):
            self.create_header_footer(canvas, doc, vendor_info)
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=self.margins['left'],
            rightMargin=self.margins['right'],
            topMargin=self.margins['top'] + 30,  # Extra space for header
            bottomMargin=self.margins['bottom'] + 30  # Extra space for footer
        )
        
        styles = self.create_styles()
        story = []
        
        # Title page
        story.append(Paragraph(vendor_info['system_name'], styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("SOURCE SYSTEM DOCUMENTATION", styles['SectionHeader']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Supplier: {vendor_info['name']}", styles['BodyText']))
        story.append(Paragraph(f"Location: {vendor_info['location']}", styles['BodyText']))
        story.append(Paragraph(f"Contact: {vendor_info['contact_email']}", styles['BodyText']))
        story.append(Paragraph(f"Document Date: {datetime.now().strftime('%B %Y')}", styles['BodyText']))
        story.append(PageBreak())
        
        # Add sections
        for section_name, section_content in sections.items():
            if section_content.strip():
                story.append(Paragraph(section_name, styles['SectionHeader']))
                story.extend(self.format_text_content(section_content, styles))
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        self.logger.info(f"ERP documentation generated: {output_path}")
        
        return output_path
    
    def generate_webshop_pdf(self) -> Path:
        """Generate Webshop system documentation PDF"""
        self.logger.info("Generating Webshop system documentation PDF...")
        
        # Load TXT content
        txt_file = Path("docs/source_systems/webshop_source_system.txt")
        txt_content = self.storage.read_file(txt_file)
        
        # Parse content into sections
        sections = self.parse_txt_content(txt_content)
        
        # Create PDF
        output_path = Path(self.doc_config['output_directory']) / "EuroStyle_Webshop_Documentation.pdf"
        self.storage.ensure_directory_exists(output_path.parent)
        
        vendor_info = self.doc_config['webshop_vendor']
        
        def add_header_footer(canvas, doc):
            self.create_header_footer(canvas, doc, vendor_info)
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=self.margins['left'],
            rightMargin=self.margins['right'],
            topMargin=self.margins['top'] + 30,
            bottomMargin=self.margins['bottom'] + 30
        )
        
        styles = self.create_styles()
        story = []
        
        # Title page
        story.append(Paragraph(vendor_info['system_name'], styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("WEBSHOP SOURCE SYSTEM DOCUMENTATION", styles['SectionHeader']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Supplier: {vendor_info['name']}", styles['BodyText']))
        story.append(Paragraph(f"Location: {vendor_info['location']}", styles['BodyText']))
        story.append(Paragraph(f"Contact: {vendor_info['contact_email']}", styles['BodyText']))
        story.append(Paragraph(f"Document Date: {datetime.now().strftime('%B %Y')}", styles['BodyText']))
        story.append(PageBreak())
        
        # Add sections  
        for section_name, section_content in sections.items():
            if section_content.strip():
                story.append(Paragraph(section_name, styles['SectionHeader']))
                story.extend(self.format_text_content(section_content, styles))
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        self.logger.info(f"Webshop documentation generated: {output_path}")
        
        return output_path

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate source system documentation PDFs')
    parser.add_argument('--system', choices=['erp', 'webshop', 'all'], default='all',
                       help='Which system documentation to generate')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        # Load configuration (framework compliance)
        config = get_config(args.config)
        
        # Initialize generator
        generator = SourceSystemDocGenerator(config)
        
        # Generate PDFs based on selection
        generated_files = []
        
        if args.system in ['erp', 'all']:
            pdf_path = generator.generate_erp_pdf()
            generated_files.append(pdf_path)
        
        if args.system in ['webshop', 'all']:
            pdf_path = generator.generate_webshop_pdf()
            generated_files.append(pdf_path)
        
        print("\n✅ Documentation generation completed successfully!")
        print("Generated files:")
        for file_path in generated_files:
            print(f"  📄 {file_path}")
            
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()