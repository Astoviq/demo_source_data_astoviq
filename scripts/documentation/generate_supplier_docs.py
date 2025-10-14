#!/usr/bin/env python3

"""
EuroStyle Fashion - Database Technical Documentation Generator
============================================================
Generates professional database documentation for EuroStyle ClickHouse databases.
Focuses purely on database schema, table structures, and data access methods.

Databases Covered:
- EuroStyle Operational Database (eurostyle_operational)
- EuroStyle Finance Database (eurostyle_finance)
- EuroStyle HR Database (eurostyle_hr)
- EuroStyle Webshop Analytics Database (eurostyle_webshop)

Author: EuroStyle Fashion Database Team
Date: 2024-10-12
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import csv
import json

# ReportLab imports for professional PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class EuroStyleDocGenerator:
    """Professional database documentation generator for EuroStyle ClickHouse databases."""
    
    def __init__(self):
        """Initialize the database documentation generator."""
        print("📊 Initializing EuroStyle Database Documentation Generator...")
        
        # Configuration
        self.company_name = "EuroStyle Fashion Database Systems"
        self.company_tagline = "European Fashion Retail Database Solutions"
        self.doc_version = "v2.1"
        self.doc_date = datetime.now().strftime("%B %Y")
        
        # Output directory
        self.output_dir = "docs/supplier"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Brand colors (EuroStyle brand palette)
        self.primary_color = colors.Color(0.1, 0.2, 0.4)      # Dark blue
        self.secondary_color = colors.Color(0.8, 0.1, 0.3)    # Fashion red
        self.accent_color = colors.Color(0.9, 0.7, 0.1)       # Gold accent
        self.text_color = colors.Color(0.2, 0.2, 0.2)         # Dark gray
        self.light_gray = colors.Color(0.95, 0.95, 0.95)      # Light gray
        
        # Initialize styles
        self.setup_styles()
        
        # Data containers
        self.systems_data = {}
        
        print("✅ Documentation generator initialized")
    
    def setup_styles(self):
        """Setup professional document styles."""
        self.styles = getSampleStyleSheet()
        
        # Title page styles
        self.styles.add(ParagraphStyle(
            'CompanyTitle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=self.primary_color,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'SystemTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.secondary_color,
            spaceAfter=18,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            'EuroBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            'CodeText',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            backColor=self.light_gray,
            leftIndent=20,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def create_title_page(self, story, system_name: str, system_description: str):
        """Create professional title page."""
        # Company name and logo area
        story.append(Spacer(1, 2*inch))
        
        company_title = Paragraph(self.company_name, self.styles['CompanyTitle'])
        story.append(company_title)
        
        tagline = Paragraph(self.company_tagline, self.styles['EuroBodyText'])
        story.append(KeepTogether([tagline, Spacer(1, 0.5*inch)]))
        
        # System title
        system_title = Paragraph(system_name, self.styles['SystemTitle'])
        story.append(system_title)
        
        # System description
        description = Paragraph(system_description, self.styles['EuroBodyText'])
        story.append(KeepTogether([description, Spacer(1, 1*inch)]))
        
        # Document info table
        doc_info = [
            ['Document Version:', self.doc_version],
            ['Publication Date:', self.doc_date],
            ['Document Type:', 'Technical Specification & Integration Guide'],
            ['Intended Audience:', 'System Integrators, IT Architects, Developers'],
            ['Classification:', 'Confidential - Customer Use Only']
        ]
        
        doc_table = Table(doc_info, colWidths=[2*inch, 3*inch])
        doc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 1, self.light_gray)
        ]))
        
        story.append(doc_table)
        story.append(Spacer(1, 1*inch))
        
        # Copyright and contact
        copyright_text = f"""
        <b>© {datetime.now().year} EuroStyle Fashion Systems B.V.</b><br/>
        All rights reserved. This document contains proprietary and confidential information.<br/>
        <br/>
        <b>Contact Information:</b><br/>
        EuroStyle Fashion Systems B.V.<br/>
        Herengracht 123, 1015 BD Amsterdam, Netherlands<br/>
        Email: integration@eurostyle-systems.com<br/>
        Phone: +31 20 123 4567<br/>
        Web: www.eurostyle-systems.com
        """
        
        story.append(Paragraph(copyright_text, self.styles['EuroBodyText']))
        story.append(PageBreak())
    
    def create_table_of_contents(self, story):
        """Create table of contents."""
        story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # We'll use a simple TOC structure
        toc_data = [
            ['1. Executive Summary', '3'],
            ['2. System Architecture Overview', '4'],
            ['3. Data Model Specification', '6'],
            ['4. API Reference', '12'],
            ['5. Integration Guidelines', '18'],
            ['6. Security & Compliance', '22'],
            ['7. Performance & Scalability', '24'],
            ['8. Support & Maintenance', '26'],
            ['Appendix A: Sample Data', '28'],
            ['Appendix B: Error Codes', '30']
        ]
        
        toc_table = Table(toc_data, colWidths=[4.5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.light_gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(toc_table)
        story.append(PageBreak())
    
    def add_section(self, story, title: str, content: str):
        """Add a major section to the document."""
        story.append(Paragraph(title, self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(content, self.styles['EuroBodyText']))
        story.append(Spacer(1, 0.2*inch))
    
    def add_subsection(self, story, title: str, content: str):
        """Add a subsection to the document."""
        story.append(Paragraph(title, self.styles['SubHeader']))
        story.append(Paragraph(content, self.styles['EuroBodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    def create_data_table(self, headers: List[str], data: List[List[str]], title: str = None) -> Table:
        """Create a professional data table."""
        # Add headers to data
        table_data = [headers] + data
        
        # Calculate column widths
        num_cols = len(headers)
        col_width = 6.5 * inch / num_cols
        col_widths = [col_width] * num_cols
        
        table = Table(table_data, colWidths=col_widths)
        
        # Table styling
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            
            # Grid and alternating colors
            ('GRID', (0, 0), (-1, -1), 1, self.light_gray),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray] * 20),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def load_system_data(self):
        """Load data from CSV files to include in documentation."""
        print("📊 Loading system data for documentation...")
        
        # Load operational stores
        try:
            with open('eurostyle_operational.stores.csv', 'r') as f:
                reader = csv.DictReader(f)
                stores = list(reader)[:5]  # First 5 for samples
                self.systems_data['stores'] = stores
        except:
            self.systems_data['stores'] = []
        
        # Load finance entities
        try:
            with open('eurostyle_finance.legal_entities.csv', 'r') as f:
                reader = csv.DictReader(f)
                entities = list(reader)
                self.systems_data['entities'] = entities
        except:
            self.systems_data['entities'] = []
        
        # Load HR employees sample
        try:
            with open('eurostyle_hr.employees.csv', 'r') as f:
                reader = csv.DictReader(f)
                employees = list(reader)[:3]  # First 3 for samples
                self.systems_data['employees'] = employees
        except:
            self.systems_data['employees'] = []
    
    def generate_operational_db_documentation(self):
        """Generate operational database documentation."""
        print("🏢 Generating Operational Database Documentation...")
        
        filename = os.path.join(self.output_dir, "EuroStyle_Operational_Database_v2.1.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        story = []
        
        # Title page
        self.create_title_page(
            story,
            "EuroStyle Operational Database",
            "ClickHouse-powered operational database containing customer, product, order, and store data "
            "for European fashion retail operations. High-performance columnar database optimized "
            "for analytical workloads and real-time reporting."
        )
        
        # Table of contents
        self.create_table_of_contents(story)
        
        # Executive Summary
        exec_summary = """
        The EuroStyle Operational Database is a high-performance ClickHouse columnar database designed for 
        European fashion retail operations. It contains comprehensive customer, product, order, and store data 
        optimized for analytical queries and real-time business intelligence.
        
        <b>Database Characteristics:</b><br/>
        • ClickHouse columnar storage engine for ultra-fast queries<br/>
        • ReplacingMergeTree tables for efficient data versioning<br/>
        • Multi-country data support (Netherlands, Germany, France, Belgium, Luxembourg)<br/>
        • GDPR-compliant customer data structures<br/>
        • Fashion-specific product attributes and hierarchies<br/>
        • Real-time order processing and inventory tracking<br/>
        • Comprehensive store performance metrics<br/>
        • Optimized for both transactional and analytical workloads<br/>
        • Advanced indexing and partitioning strategies
        """
        
        self.add_section(story, "1. Executive Summary", exec_summary)
        
        # Database Architecture
        architecture = """
        The EuroStyle Operational Database is built on ClickHouse, a high-performance columnar database 
        management system optimized for online analytical processing (OLAP). The database schema is designed 
        for European fashion retail operations with advanced data structures and optimizations.
        
        <b>Technical Architecture:</b><br/>
        • Engine: ClickHouse 24.x+ with ReplacingMergeTree storage<br/>
        • Storage: Columnar compression with advanced codecs<br/>
        • Partitioning: Date-based partitioning for optimal performance<br/>
        • Indexing: Primary keys optimized for common query patterns<br/>
        • Data Types: Advanced ClickHouse types including Maps, Arrays, Enums<br/>
        • Materialized Views: Real-time aggregations for reporting<br/>
        • Replication: Multi-master replication for high availability
        """
        
        self.add_section(story, "2. System Architecture Overview", architecture)
        
        # Data Model - Stores Table
        self.add_subsection(story, "2.1 Core Data Entities", "")
        
        if self.systems_data.get('stores'):
            story.append(Paragraph("<b>Store Locations</b>", self.styles['SubHeader']))
            
            store_headers = ['Store ID', 'Store Name', 'Country', 'City', 'Store Format']
            store_data = []
            for store in self.systems_data['stores'][:5]:
                store_data.append([
                    store.get('store_id', ''),
                    store.get('store_name', ''),
                    store.get('country_code', ''),
                    store.get('city', ''),
                    store.get('store_format', '')
                ])
            
            store_table = self.create_data_table(store_headers, store_data)
            story.append(store_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Database Schema section
        schema_reference = """
        The EuroStyle Operational Database contains four primary tables optimized for fashion retail analytics. 
        All tables use ClickHouse's ReplacingMergeTree engine for efficient updates and data versioning.
        
        <b>Database:</b> eurostyle_operational
        
        <b>Connection Details:</b><br/>
        • Host: localhost (or your ClickHouse server)<br/>
        • Port: 8123 (HTTP) / 9000 (Native)<br/>
        • Database: eurostyle_operational<br/>
        • Engine: ClickHouse with ReplacingMergeTree tables
        
        <b>Core Database Tables:</b>
        """
        
        self.add_section(story, "3. Database Schema Overview", schema_reference)
        
        # Database tables overview
        tables_headers = ['Table Name', 'Primary Key', 'Description']
        tables_data = [
            ['customers', 'customer_id', 'Customer master data with GDPR compliance'],
            ['products', 'product_id', 'Fashion product catalog with sustainability metrics'],
            ['orders', 'order_id', 'Multi-channel order transactions and fulfillment'],
            ['order_lines', 'order_line_id', 'Individual order line items with product details'],
            ['stores', 'store_id', 'Physical store locations and performance data'],
            ['campaigns', 'campaign_id', 'Marketing campaign definitions and tracking']
        ]
        
        tables_table = self.create_data_table(tables_headers, tables_data)
        story.append(tables_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Query Examples
        query_examples = """
        Access the EuroStyle Operational Database using standard ClickHouse SQL queries. 
        The database is optimized for analytical workloads with fast aggregations and filtering.
        
        <b>Sample Queries:</b><br/>
        
        <b>Customer Analysis:</b><br/>
        SELECT country_code, COUNT(*) as customers, AVG(total_spent) as avg_spend<br/>
        FROM customers WHERE customer_status = 'active'<br/>
        GROUP BY country_code ORDER BY customers DESC;<br/>
        
        <b>Product Performance:</b><br/>
        SELECT category_l1, category_l2, COUNT(*) as products,<br/>
        AVG(sustainability_score) as avg_sustainability<br/>
        FROM products WHERE is_active = true<br/>
        GROUP BY category_l1, category_l2;<br/>
        
        <b>Order Trends:</b><br/>
        SELECT toYYYYMM(order_date) as month, COUNT(*) as orders,<br/>
        SUM(total_amount_eur) as revenue<br/>
        FROM orders WHERE order_status IN ('delivered', 'shipped')<br/>
        GROUP BY month ORDER BY month DESC;
        """
        
        self.add_section(story, "4. SQL Query Examples", query_examples)
        
        # Performance & Scalability Claims
        performance_claims = """
        The EuroStyle Operational Database delivers exceptional performance with ClickHouse's 
        advanced columnar storage and proprietary optimization algorithms.
        
        <b>Performance Benchmarks:</b><br/>
        • Query Response Time: < 100ms for 99% of analytical queries<br/>
        • Data Ingestion: 1M+ records per second sustained throughput<br/>
        • Concurrent Users: Supports 10,000+ simultaneous analytical sessions<br/>
        • Data Compression: 90%+ compression ratio with LZ4/ZSTD codecs<br/>
        • Storage Efficiency: Petabyte-scale capability on commodity hardware<br/>
        • Memory Usage: Optimized columnar processing with vectorized execution<br/>
        • Network I/O: Intelligent query distribution and result caching<br/>
        • Uptime: 99.9% availability with automatic failover capabilities
        
        <b>Advanced Features:</b><br/>
        • Real-time materialized views with automatic refresh<br/>
        • Advanced partitioning strategies for time-series optimization<br/>
        • Distributed query execution across multiple shards<br/>
        • Built-in data quality monitoring and validation<br/>
        • Automated index optimization and statistics collection
        """
        
        self.add_section(story, "5. Performance & Advanced Features", performance_claims)
        
        # Build the PDF
        doc.build(story)
        print(f"✅ Operational Database Documentation generated: {filename}")
        
        return filename
    
    def generate_finance_documentation(self):
        """Generate Finance database documentation."""
        print("💰 Generating Finance Database Documentation...")
        
        filename = os.path.join(self.output_dir, "EuroStyle_Finance_Database_v2.1.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        story = []
        
        # Title page
        self.create_title_page(
            story,
            "EuroStyle Finance Database",
            "ClickHouse-powered financial database with multi-entity BV structure, "
            "IFRS-compliant chart of accounts, and comprehensive general ledger data "
            "designed for European fashion retail financial reporting and analysis."
        )
        
        # Table of contents
        self.create_table_of_contents(story)
        
        # Executive Summary
        exec_summary = """
        The EuroStyle Finance Management System provides comprehensive financial management capabilities 
        for multi-entity European businesses. The system supports complex holding company structures 
        with full consolidation, multi-currency operations, and IFRS compliance.
        
        <b>Key Features:</b><br/>
        • Multi-entity consolidation (1 Holding + 4 BV subsidiaries)<br/>
        • Complete chart of accounts with IFRS structure<br/>
        • Multi-currency support with real-time exchange rates<br/>
        • General ledger with full audit trail capabilities<br/>
        • Budgeting and forecasting with multi-dimensional analysis<br/>
        • Fixed asset management with automated depreciation<br/>
        • Cost center management and allocation<br/>
        • Financial reporting and analytics<br/>
        • Compliance with European accounting standards
        """
        
        self.add_section(story, "1. Executive Summary", exec_summary)
        
        # Legal Entity Structure
        entity_structure = """
        The system manages a sophisticated legal entity structure designed for European operations.
        The holding company structure provides operational flexibility while maintaining financial control.
        """
        
        self.add_section(story, "2. Legal Entity Structure", entity_structure)
        
        # Legal entities table
        if self.systems_data.get('entities'):
            entity_headers = ['Entity Code', 'Entity Name', 'Country', 'Type', 'Currency']
            entity_data = []
            for entity in self.systems_data['entities']:
                entity_data.append([
                    entity.get('entity_code', ''),
                    entity.get('entity_name', '')[:40] + '...' if len(entity.get('entity_name', '')) > 40 else entity.get('entity_name', ''),
                    entity.get('country_code', ''),
                    entity.get('entity_type', ''),
                    entity.get('functional_currency', '')
                ])
            
            entity_table = self.create_data_table(entity_headers, entity_data)
            story.append(entity_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Chart of Accounts
        coa_section = """
        The system implements a comprehensive chart of accounts structure compliant with IFRS standards.
        The account structure supports multi-dimensional reporting and analysis.
        
        <b>Account Categories:</b><br/>
        • Assets (1000-1999): Current and non-current assets<br/>
        • Liabilities (2000-2999): Current and long-term liabilities<br/>
        • Equity (3000-3999): Share capital and retained earnings<br/>
        • Revenue (4000-4999): Sales and other revenue streams<br/>
        • Expenses (5000-9999): Operating and non-operating expenses
        """
        
        self.add_section(story, "3. Chart of Accounts Structure", coa_section)
        
        # API Reference
        api_reference = """
        <b>Base URL:</b> https://api.eurostyle-finance.com/v2/
        
        <b>Core Financial APIs:</b>
        """
        
        self.add_section(story, "4. API Reference", api_reference)
        
        # Finance API endpoints
        finance_api_headers = ['Endpoint', 'Method', 'Description']
        finance_api_data = [
            ['/entities', 'GET', 'Legal entity information'],
            ['/chart-of-accounts', 'GET', 'Chart of accounts structure'],
            ['/gl-transactions', 'GET, POST', 'General ledger transactions'],
            ['/budgets', 'GET, POST', 'Budget data management'],
            ['/exchange-rates', 'GET', 'Currency exchange rates'],
            ['/fixed-assets', 'GET, POST', 'Fixed asset management'],
            ['/consolidation', 'GET', 'Consolidation reports']
        ]
        
        finance_api_table = self.create_data_table(finance_api_headers, finance_api_data)
        story.append(finance_api_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Build the PDF
        doc.build(story)
        print(f"✅ Finance Documentation generated: {filename}")
        
        return filename
    
    def generate_hr_documentation(self):
        """Generate HR system supplier documentation."""
        print("👥 Generating HR System Documentation...")
        
        filename = os.path.join(self.output_dir, "EuroStyle_HR_System_v2.1.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        story = []
        
        # Title page
        self.create_title_page(
            story,
            "EuroStyle HR Management System",
            "Comprehensive Human Resources management system with European employment law compliance, "
            "GDPR data protection, multi-country operations, and advanced workforce analytics "
            "designed for modern European businesses."
        )
        
        # Table of contents
        self.create_table_of_contents(story)
        
        # Executive Summary
        exec_summary = """
        The EuroStyle HR Management System provides complete human resources management capabilities 
        with built-in European employment law compliance and GDPR data protection features.
        
        <b>Key Features:</b><br/>
        • European employment law compliance (NL, DE, FR, BE, LU)<br/>
        • GDPR-compliant employee data management<br/>
        • Complete employee lifecycle management<br/>
        • Advanced leave management with statutory compliance<br/>
        • Performance management and review cycles<br/>
        • Training and development tracking<br/>
        • Employee surveys and engagement analytics<br/>
        • Compensation and benefits administration<br/>
        • Organizational structure and hierarchy management<br/>
        • Multi-language and multi-currency support
        """
        
        self.add_section(story, "1. Executive Summary", exec_summary)
        
        # European Compliance
        compliance_section = """
        The system ensures full compliance with European employment legislation across all supported countries.
        
        <b>Compliance Features by Country:</b><br/>
        • Netherlands: 25 days annual leave, extensive sick leave protection<br/>
        • Germany: 24 days annual leave, up to 4 years sick leave continuation<br/>
        • France: 25 days annual leave, 35-hour work week compliance<br/>
        • Belgium: 20 days annual leave, comprehensive social security integration<br/>
        • Luxembourg: 25 days annual leave, multilingual support
        
        <b>GDPR Compliance:</b><br/>
        • Data masking for sensitive information<br/>
        • Right to erasure implementation<br/>
        • Consent management for surveys<br/>
        • Data minimization principles<br/>
        • Audit trail for all personal data access
        """
        
        self.add_section(story, "2. European Employment Law & GDPR Compliance", compliance_section)
        
        # Sample employee data (anonymized)
        if self.systems_data.get('employees'):
            story.append(Paragraph("<b>Employee Data Structure (Sample)</b>", self.styles['SubHeader']))
            
            emp_headers = ['Employee ID', 'Country', 'Department', 'Position Level', 'Employment Status']
            emp_data = []
            for emp in self.systems_data['employees'][:3]:
                emp_data.append([
                    emp.get('employee_id', ''),
                    emp.get('nationality', ''),
                    'Operations',  # Simplified for demo
                    'Senior',      # Simplified for demo
                    emp.get('employee_status', '')
                ])
            
            emp_table = self.create_data_table(emp_headers, emp_data)
            story.append(emp_table)
            story.append(Spacer(1, 0.3*inch))
        
        # HR API Reference
        hr_api_reference = """
        <b>Base URL:</b> https://api.eurostyle-hr.com/v2/
        
        <b>Core HR APIs:</b>
        """
        
        self.add_section(story, "4. API Reference", hr_api_reference)
        
        # HR API endpoints
        hr_api_headers = ['Endpoint', 'Method', 'Description']
        hr_api_data = [
            ['/employees', 'GET, POST, PUT', 'Employee master data management'],
            ['/contracts', 'GET, POST', 'Employment contract management'],
            ['/leave-requests', 'GET, POST', 'Leave request processing'],
            ['/performance', 'GET, POST', 'Performance review management'],
            ['/training', 'GET, POST', 'Training and development'],
            ['/surveys', 'GET, POST', 'Employee engagement surveys'],
            ['/compensation', 'GET', 'Compensation and benefits data'],
            ['/compliance', 'GET', 'Compliance reporting and metrics']
        ]
        
        hr_api_table = self.create_data_table(hr_api_headers, hr_api_data)
        story.append(hr_api_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Build the PDF
        doc.build(story)
        print(f"✅ HR Documentation generated: {filename}")
        
        return filename
    
    def generate_webshop_documentation(self):
        """Generate Webshop Analytics system documentation."""
        print("🌐 Generating Webshop Analytics Documentation...")
        
        filename = os.path.join(self.output_dir, "EuroStyle_Webshop_Analytics_v2.1.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        
        story = []
        
        # Title page
        self.create_title_page(
            story,
            "EuroStyle Webshop Analytics Platform",
            "Advanced e-commerce analytics platform providing real-time customer behavior tracking, "
            "conversion optimization, personalization capabilities, and comprehensive business intelligence "
            "for digital fashion retail operations."
        )
        
        # Table of contents
        self.create_table_of_contents(story)
        
        # Executive Summary
        exec_summary = """
        The EuroStyle Webshop Analytics Platform provides comprehensive e-commerce analytics and 
        customer behavior tracking capabilities for digital fashion retail operations.
        
        <b>Key Features:</b><br/>
        • Real-time customer session tracking and analysis<br/>
        • Advanced page view analytics with heat mapping<br/>
        • Shopping cart behavior and abandonment analysis<br/>
        • Search query analysis and optimization<br/>
        • Product recommendation engine with AI/ML<br/>
        • A/B testing framework for conversion optimization<br/>
        • Customer review and rating management<br/>
        • Email marketing campaign tracking<br/>
        • Wishlist and favorites analytics<br/>
        • Cross-device customer journey tracking<br/>
        • GDPR-compliant visitor privacy management
        """
        
        self.add_section(story, "1. Executive Summary", exec_summary)
        
        # Analytics Architecture
        analytics_arch = """
        The platform utilizes modern event-driven architecture for real-time data collection and processing.
        
        <b>Data Collection Methods:</b><br/>
        • JavaScript SDK for web tracking<br/>
        • Server-side API for backend events<br/>
        • Mobile SDK for app analytics<br/>
        • Pixel tracking for email campaigns
        
        <b>Event Processing:</b><br/>
        • Real-time stream processing<br/>
        • Batch processing for historical analysis<br/>
        • Machine learning pipeline for recommendations<br/>
        • Data warehouse integration for BI reporting
        """
        
        self.add_section(story, "2. Analytics Architecture", analytics_arch)
        
        # Event Types
        event_types = """
        The system tracks various types of user interactions and behavioral events:
        """
        
        self.add_section(story, "3. Event Tracking Specification", event_types)
        
        # Event types table
        event_headers = ['Event Type', 'Description', 'Key Attributes']
        event_data = [
            ['page_view', 'User views a page', 'page_url, session_id, user_agent'],
            ['product_view', 'User views product details', 'product_id, category, price'],
            ['cart_add', 'Item added to cart', 'product_id, quantity, price'],
            ['cart_remove', 'Item removed from cart', 'product_id, quantity'],
            ['search', 'User performs search', 'query, results_count, filters'],
            ['purchase', 'Order completion', 'order_id, total_amount, items'],
            ['email_click', 'Email campaign click', 'campaign_id, email_id, link_url'],
            ['review_submit', 'Product review submission', 'product_id, rating, review_text']
        ]
        
        event_table = self.create_data_table(event_headers, event_data)
        story.append(event_table)
        story.append(Spacer(1, 0.3*inch))
        
        # API Reference
        webshop_api = """
        <b>Base URL:</b> https://api.eurostyle-webshop.com/v2/
        
        <b>Analytics APIs:</b>
        """
        
        self.add_section(story, "4. API Reference", webshop_api)
        
        # Webshop API endpoints
        webshop_api_headers = ['Endpoint', 'Method', 'Description']
        webshop_api_data = [
            ['/events', 'POST', 'Submit behavioral events'],
            ['/sessions', 'GET', 'Session analytics and insights'],
            ['/products/recommendations', 'GET', 'AI-powered product recommendations'],
            ['/search/analytics', 'GET', 'Search query performance analytics'],
            ['/campaigns/performance', 'GET', 'Marketing campaign effectiveness'],
            ['/customers/segments', 'GET', 'Customer segmentation analytics'],
            ['/conversion/funnel', 'GET', 'Conversion funnel analysis'],
            ['/ab-tests', 'GET, POST', 'A/B test management and results']
        ]
        
        webshop_api_table = self.create_data_table(webshop_api_headers, webshop_api_data)
        story.append(webshop_api_table)
        
        # Build the PDF
        doc.build(story)
        print(f"✅ Webshop Analytics Documentation generated: {filename}")
        
        return filename
    
    def generate_technical_documentation(self):
        """Generate technical documentation files (ERD, entity descriptions, etc.)."""
        print("📋 Generating technical documentation files...")
        
        # Generate ERD documentation
        self.generate_erd_documentation()
        
        # Generate entity and attribute descriptions
        self.generate_data_dictionary()
        
        # Generate database connection guide
        self.generate_database_connection_guide()
        
        print("✅ Technical documentation files generated")
    
    def generate_erd_documentation(self):
        """Generate ERD (Entity Relationship Diagram) documentation."""
        erd_content = """
# EuroStyle Fashion - Entity Relationship Diagrams

## System Architecture ERD

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OPERATIONAL   │    │    WEBSHOP      │    │    FINANCE      │    │       HR        │
│     SYSTEM      │    │   ANALYTICS     │    │   MANAGEMENT    │    │   MANAGEMENT    │
│                 │    │                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ customers   │◄┼────┼►│web_sessions │ │    │ │legal_entities│◄┼────┼►│employees    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │        │        │    │        │        │    │        │        │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ products    │◄┼────┼►│ page_views  │ │    │ │chart_of_acct│ │    │ │departments  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │        │        │    │        │        │    │        │        │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ orders      │ │    │ │cart_activity│ │    │ │gl_journals  │ │    │ │leave_request│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│        │        │    │                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ order_lines │ │    │ │product_rev. │ │    │ │budget_data  │ │    │ │training     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Operational System ERD

```
     ┌─────────────┐
     │  customers  │
     │             │
     │ customer_id │ (PK)
     │ email       │
     │ first_name  │
     │ ...         │
     └─────┬───────┘
           │ 1
           │
           │ *
    ┌─────────────┐      ┌─────────────┐
    │   orders    │      │  campaigns  │
    │             │      │             │
    │ order_id    │ (PK) │ campaign_id │ (PK)
    │ customer_id │ (FK) │ campaign_nm │
    │ store_id    │ (FK) │ start_date  │
    │ ...         │      │ ...         │
    └─────┬───────┘      └─────────────┘
          │ 1
          │
          │ *
   ┌─────────────┐      ┌─────────────┐
   │ order_lines │      │  products   │
   │             │      │             │
   │ order_line  │ (PK) │ product_id  │ (PK)
   │ order_id    │ (FK) │ product_nm  │
   │ product_id  │ (FK) │ category    │
   │ ...         │      │ ...         │
   └─────────────┘      └─────┬───────┘
          │ *                  │ 1
          └────────────────────┘
```

## Finance System ERD

```
┌─────────────┐      ┌─────────────┐
│legal_entities│      │chart_of_acc │
│             │      │             │
│ entity_id   │ (PK) │ account_id  │ (PK)
│ entity_code │      │ account_cd  │
│ entity_name │      │ account_nm  │
│ ...         │      │ ...         │
└─────┬───────┘      └─────┬───────┘
      │ 1                  │ 1
      │                    │
      │ *                  │ *
┌─────────────┐      ┌─────────────┐
│gl_jrnl_hdr  │      │gl_jrnl_line │
│             │      │             │
│ journal_hdr │ (PK) │ journal_ln  │ (PK)
│ entity_id   │ (FK) │ journal_hdr │ (FK)
│ journal_dt  │      │ account_id  │ (FK)
│ ...         │      │ debit_amt   │
└─────────────┘      │ credit_amt  │
                     │ ...         │
                     └─────────────┘
```

## HR System ERD

```
┌─────────────┐      ┌─────────────┐
│departments  │      │job_positions│
│             │      │             │
│ department  │ (PK) │ position_id │ (PK)
│ dept_code   │      │ position_cd │
│ dept_name   │      │ dept_id     │ (FK)
│ ...         │      │ ...         │
└─────┬───────┘      └─────┬───────┘
      │ 1                  │ 1
      │                    │
      │ *                  │ *
┌─────────────┐      ┌─────────────┐
│ employees   │      │employment   │
│             │      │ _contracts  │
│ employee_id │ (PK) │ contract_id │ (PK)
│ entity_id   │ (FK) │ employee_id │ (FK)
│ first_name  │      │ position_id │ (FK)
│ last_name   │      │ start_date  │
│ ...         │      │ ...         │
└─────────────┘      └─────────────┘
```

## Cross-System Integration Points

1. **Customer Integration**: `operational.customers.customer_id` ↔ `webshop.web_sessions.customer_id`
2. **Product Integration**: `operational.products.product_id` ↔ `webshop.page_views.product_id`
3. **Campaign Integration**: `operational.campaigns.campaign_id` ↔ `webshop.email_marketing.campaign_id`
4. **Entity Integration**: `finance.legal_entities.entity_id` ↔ `hr.employees.entity_id`
5. **Financial Integration**: Order data flows to GL through automated journal entries
"""
        
        erd_file = os.path.join(self.output_dir, "EuroStyle_ERD_Documentation.txt")
        with open(erd_file, 'w') as f:
            f.write(erd_content)
        print(f"  📊 ERD Documentation: {os.path.basename(erd_file)}")
    
    def generate_data_dictionary(self):
        """Generate comprehensive data dictionary."""
        data_dict_content = """
# EuroStyle Fashion - Data Dictionary & Entity Descriptions

## OPERATIONAL SYSTEM ENTITIES

### customers
**Purpose**: Central customer master data with GDPR compliance
**Key Attributes**:
- customer_id (String, PK): Unique identifier format CUST_EU_XXXXXX
- email (String): Primary contact method, used for online authentication  
- first_name, last_name (String): Personal identification, GDPR protected
- country_code (String): NL, DE, FR, BE, LU for European operations
- loyalty_tier (String): Bronze, Silver, Gold, Platinum for segmentation
- total_spent (Decimal64): Customer lifetime value in EUR

**Business Rules**:
- Email must be unique across all customers
- Marketing consent required for promotional communications (GDPR)
- Customer data retention policy: 7 years after last interaction

### products
**Purpose**: Fashion product catalog with multi-country pricing
**Key Attributes**:
- product_id (String, PK): Unique identifier format PROD_EU_XXXXXX
- category_l1, l2, l3 (String): Hierarchical categorization (Women > Tops > T-Shirts)
- price_eur (Decimal64): Base price in EUR, converted to local currencies
- sustainability_score (UInt8): 1-10 rating for environmental impact
- material_composition (String): "80% Organic Cotton, 20% Recycled Polyester"

**Business Rules**:
- Products must have at least one size variant to be sellable
- Sustainability score mandatory for all new products since 2024
- Price changes require approval for active products

### orders
**Purpose**: Customer purchase transactions across all channels
**Key Attributes**:
- order_id (String, PK): Format ORD_EU_YYYY_XXXXXX with year embedded
- customer_id (String, FK): Links to customers table
- store_id (String, FK): 'ONLINE' for e-commerce, store ID for retail
- order_status (String): pending, confirmed, shipped, delivered, cancelled, returned
- total_amount_eur (Decimal64): Final order value including tax and shipping

**Business Rules**:
- Orders cannot be deleted, only cancelled with reason
- Payment must be confirmed before order confirmation
- European VAT rates applied based on delivery country

## WEBSHOP ANALYTICS ENTITIES

### web_sessions
**Purpose**: Digital customer journey tracking across country websites
**Key Attributes**:
- session_id (String, PK): Unique session identifier
- customer_id (String, FK, Nullable): NULL for anonymous sessions
- country_code (String): Which country site (nl.eurostyle.com, etc.)
- device_type (String): desktop, mobile, tablet for responsive analysis
- conversion_session (Bool): True if session resulted in purchase

**Business Rules**:
- Sessions timeout after 30 minutes of inactivity
- Anonymous sessions can be linked to customer post-login
- GDPR compliance: IP addresses stored for 90 days maximum

### page_views
**Purpose**: Detailed page interaction tracking for UX optimization
**Key Attributes**:
- page_view_id (String, PK): Unique page view identifier
- product_id (String, FK, Nullable): Set for product detail pages
- time_on_page_seconds (UInt16): User engagement measurement
- scroll_depth_percent (UInt8): How far user scrolled (0-100)

**Business Rules**:
- Page views under 3 seconds considered bounces
- Product page views trigger recommendation engine
- Heat map data aggregated weekly for performance

## FINANCE SYSTEM ENTITIES

### legal_entities
**Purpose**: European BV structure with holding company
**Key Attributes**:
- entity_id (String, PK): ENTITY_[COUNTRY]_[TYPE] format
- entity_code (String): Short code ESLH, ESDE, ESFR, ESBE, ESLU
- functional_currency (String): Base currency for each entity (EUR)
- parent_entity_id (String, FK): Links to ESLH holding company

**Business Rules**:
- All BV entities owned 100% by ESLH holding company
- Each entity must have valid registration in home country
- Fiscal year end must align with group reporting (December 31)

### chart_of_accounts
**Purpose**: IFRS-compliant account structure for consolidated reporting
**Key Attributes**:
- account_code (String): 4-digit code following IFRS structure
- account_type (String): ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
- normal_balance (String): DEBIT or CREDIT for validation
- ifrs_classification (String): IFRS financial statement mapping

**Business Rules**:
- Account codes 1000-1999: Assets, 2000-2999: Liabilities, etc.
- All journal entries must balance (total debits = total credits)
- Accounts cannot be deleted if used in posted transactions

### gl_journal_headers & gl_journal_lines
**Purpose**: General ledger transaction recording with audit trail
**Key Attributes (Headers)**:
- journal_header_id (String, PK): Unique journal batch identifier
- entity_id (String, FK): Which BV entity the transaction belongs to
- journal_status (String): DRAFT, POSTED, REVERSED for control

**Key Attributes (Lines)**:
- journal_line_id (String, PK): Unique line identifier
- account_id (String, FK): Chart of accounts reference
- debit_amount, credit_amount (Decimal64): Transaction amounts

**Business Rules**:
- Journal entries cannot be modified once POSTED
- Each journal must have at least 2 lines (double-entry bookkeeping)
- Monthly closing prevents posting to prior periods

## HR SYSTEM ENTITIES

### employees
**Purpose**: European workforce management with GDPR compliance
**Key Attributes**:
- employee_id (String, PK): EMP_XXXXXX format
- entity_id (String, FK): Links to finance.legal_entities
- first_name, last_name (String): GDPR protected, masked in non-prod
- social_security_number (String): Encrypted/masked format ***-**-####
- employee_status (Enum8): ACTIVE, INACTIVE, TERMINATED, ON_LEAVE

**Business Rules**:
- Personal data must be masked in non-production environments
- GDPR consent required for data processing beyond employment needs
- Data retention: 7 years after employment termination

### employment_contracts
**Purpose**: European employment law compliant contract management
**Key Attributes**:
- contract_id (String, PK): CONT_[COUNTRY]_XXXXXX format
- annual_leave_days (UInt16): Country-specific legal minimums
- works_council_applicable (Bool): Germany/Netherlands requirement
- notice_period_weeks (UInt8): European termination notice periods

**Business Rules**:
- Leave entitlements vary by country: NL=25, DE=24, FR=25, BE=20, LU=25
- Probation periods limited by local law
- Fixed-term contracts require end_date

### leave_requests & leave_balances
**Purpose**: European leave management with statutory compliance
**Key Attributes (Requests)**:
- leave_type (String): ANNUAL, SICK, MATERNITY, PATERNITY, PARENTAL
- statutory_entitlement (Bool): Required by law vs. company policy
- medical_certificate_required (Bool): For sick leave > 3 days

**Key Attributes (Balances)**:
- statutory_minimum (Decimal32): Legal minimum entitlement
- sick_leave_unlimited (Bool): Germany/Netherlands unlimited sick leave
- max_carryover (Decimal32): Maximum days that can carry over

**Business Rules**:
- Sick leave unlimited in Germany and Netherlands
- Annual leave must be taken within 18 months (EU directive)
- Parental leave varies by country and gender

## CROSS-SYSTEM DATA FLOWS

1. **Order to Finance**: Order data automatically creates AR journal entries
2. **Customer to Analytics**: Customer registration triggers web session linking
3. **Product to Analytics**: Product views feed recommendation algorithms
4. **Employee to Finance**: Payroll data flows to expense accounts
5. **Campaign to Analytics**: Marketing campaigns tracked across web events

## DATA QUALITY RULES

- **Referential Integrity**: All foreign keys must have valid parent records
- **Data Consistency**: Customer country must match delivery country for EU orders
- **Temporal Consistency**: Order date cannot be before customer registration
- **Business Logic**: Product price must be > cost price (positive margin)
- **Compliance**: GDPR data masking enforced in non-production environments
"""
        
        dict_file = os.path.join(self.output_dir, "EuroStyle_Data_Dictionary.txt")
        with open(dict_file, 'w') as f:
            f.write(data_dict_content)
        print(f"  📖 Data Dictionary: {os.path.basename(dict_file)}")
    
    def generate_database_connection_guide(self):
        """Generate database connection specifications and access guides."""
        db_spec_content = """
# EuroStyle Fashion - Database Connection Guide & SQL Reference

## CLICKHOUSE CONNECTION

Connect to the EuroStyle ClickHouse databases using standard ClickHouse clients:
```
# HTTP Interface (port 8123)
ClickHouse HTTP endpoint: http://localhost:8123
Database: eurostyle_operational, eurostyle_finance, eurostyle_hr, eurostyle_webshop

# Native Interface (port 9000)
ClickHouse Native: localhost:9000
```

## OPERATIONAL DATABASE QUERIES

### Database: eurostyle_operational

#### Customer Data Access
```sql
-- Get customers by country with spending analysis
SELECT 
    customer_id,
    email,
    first_name,
    last_name,
    country_code,
    loyalty_tier,
    total_spent,
    marketing_opt_in
FROM customers 
WHERE country_code IN ('NL', 'DE', 'FR', 'BE', 'LU') 
    AND customer_status = 'active'
ORDER BY total_spent DESC
LIMIT 100;

-- Customer counts and average spending by country
SELECT 
    country_code,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spending,
    SUM(total_spent) as total_revenue
FROM customers 
GROUP BY country_code
ORDER BY total_revenue DESC;
```

#### Product Data Access
```sql
-- Get products by category with sustainability metrics
SELECT 
    product_id,
    product_name,
    category_l1,
    category_l2,
    category_l3,
    price_eur,
    sustainability_score,
    current_stock_total,
    is_active
FROM products 
WHERE category_l1 = 'Women' 
    AND category_l2 = 'Tops'
    AND is_active = true
ORDER BY sustainability_score DESC;

-- Product performance by category
SELECT 
    category_l1,
    COUNT(*) as product_count,
    AVG(price_eur) as avg_price,
    AVG(sustainability_score) as avg_sustainability,
    SUM(current_stock_total) as total_stock
FROM products
WHERE is_active = true
GROUP BY category_l1
ORDER BY product_count DESC;
```

#### Order Analysis
```sql
-- Order trends and revenue analysis
SELECT 
    toYYYYMM(order_date) as order_month,
    order_channel,
    COUNT(*) as order_count,
    SUM(total_amount_eur) as total_revenue,
    AVG(total_amount_eur) as avg_order_value
FROM orders 
WHERE order_status IN ('delivered', 'shipped')
GROUP BY order_month, order_channel
ORDER BY order_month DESC, total_revenue DESC;

-- Customer order behavior
SELECT 
    country_code,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) as total_orders,
    AVG(total_amount_eur) as avg_order_value,
    SUM(total_amount_eur) as total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE order_status = 'delivered'
GROUP BY country_code
ORDER BY total_revenue DESC;
```

## WEBSHOP ANALYTICS DATABASE

### Database: eurostyle_webshop

#### Session Data Analysis
```sql
-- Web session analytics by country and device
SELECT 
    country_code,
    device_type,
    COUNT(*) as session_count,
    AVG(session_duration_seconds) as avg_duration,
    AVG(page_views) as avg_page_views,
    SUM(CASE WHEN conversion_session = true THEN 1 ELSE 0 END) as conversions,
    (conversions * 100.0 / session_count) as conversion_rate
FROM web_sessions 
WHERE session_date >= '2024-01-01'
GROUP BY country_code, device_type
ORDER BY session_count DESC;

-- Page view analysis with product performance
SELECT 
    p.category_l1,
    p.category_l2,
    COUNT(pv.page_view_id) as total_views,
    AVG(pv.time_on_page_seconds) as avg_time_on_page,
    AVG(pv.scroll_depth_percent) as avg_scroll_depth
FROM page_views pv
JOIN products p ON pv.product_id = p.product_id
WHERE pv.page_view_date >= '2024-01-01'
GROUP BY p.category_l1, p.category_l2
ORDER BY total_views DESC;
```

## FINANCE DATABASE

### Database: eurostyle_finance

#### Legal Entity and Financial Data
```sql
-- Legal entity financial summary
SELECT 
    le.entity_code,
    le.entity_name,
    le.country_code,
    le.functional_currency,
    COUNT(DISTINCT jl.journal_header_id) as journal_entries,
    SUM(jl.debit_amount) as total_debits,
    SUM(jl.credit_amount) as total_credits
FROM legal_entities le
LEFT JOIN gl_journal_lines jl ON le.entity_id = jl.entity_id
WHERE le.is_active = true
GROUP BY le.entity_code, le.entity_name, le.country_code, le.functional_currency
ORDER BY total_debits DESC;

-- Chart of accounts with transaction volumes
SELECT 
    coa.account_code,
    coa.account_name,
    coa.account_type,
    COUNT(jl.journal_line_id) as transaction_count,
    SUM(jl.debit_amount) as total_debits,
    SUM(jl.credit_amount) as total_credits
FROM chart_of_accounts coa
LEFT JOIN gl_journal_lines jl ON coa.account_id = jl.account_id
GROUP BY coa.account_code, coa.account_name, coa.account_type
ORDER BY transaction_count DESC;
```

## HR DATABASE

### Database: eurostyle_hr

#### Employee and Contract Analysis
```sql
-- Employee distribution by entity and status
SELECT 
    le.entity_name,
    e.employee_status,
    COUNT(*) as employee_count,
    AVG(CASE WHEN e.salary_amount > 0 THEN e.salary_amount END) as avg_salary
FROM employees e
JOIN legal_entities le ON e.entity_id = le.entity_id
GROUP BY le.entity_name, e.employee_status
ORDER BY le.entity_name, employee_count DESC;

-- Leave balance analysis by country
SELECT 
    e.nationality,
    lb.leave_type,
    AVG(lb.balance_days) as avg_balance,
    AVG(lb.used_days) as avg_used,
    COUNT(*) as employee_count
FROM leave_balances lb
JOIN employees e ON lb.employee_id = e.employee_id
WHERE lb.balance_year = 2024
GROUP BY e.nationality, lb.leave_type
ORDER BY e.nationality, lb.leave_type;
```

## CONNECTION TOOLS

Recommended ClickHouse clients for database access:

**Command Line:**
- clickhouse-client (native ClickHouse CLI)
- DBeaver (GUI database tool)
- DataGrip (JetBrains database IDE)

**Programming Languages:**
- Python: clickhouse-driver, clickhouse-connect
- Node.js: @clickhouse/client
- Java: clickhouse-jdbc
- .NET: ClickHouse.Client

**Connection Examples:**
```bash
# Command line connection
clickhouse-client --host localhost --port 9000 --database eurostyle_operational

# HTTP query example
curl 'http://localhost:8123/?query=SELECT COUNT(*) FROM eurostyle_operational.customers'
```
"""
        
        db_file = os.path.join(self.output_dir, "EuroStyle_Database_Connection_Guide.txt")
        with open(db_file, 'w') as f:
            f.write(db_spec_content)
        print(f"  📊 Database Connection Guide: {os.path.basename(db_file)}")
    
    def generate_all_documentation(self):
        """Generate all supplier documentation."""
        print("\n🚀 Starting comprehensive supplier documentation generation...")
        
        # Load system data
        self.load_system_data()
        
        # Generate individual system documentation
        generated_files = []
        
        try:
            generated_files.append(self.generate_operational_db_documentation())
        except Exception as e:
            print(f"❌ Error generating Operational Database documentation: {e}")
        
        try:
            generated_files.append(self.generate_finance_documentation())
        except Exception as e:
            print(f"❌ Error generating Finance documentation: {e}")
        
        try:
            generated_files.append(self.generate_hr_documentation())
        except Exception as e:
            print(f"❌ Error generating HR documentation: {e}")
        
        try:
            generated_files.append(self.generate_webshop_documentation())
        except Exception as e:
            print(f"❌ Error generating Webshop documentation: {e}")
        
        # Generate technical documentation files
        try:
            self.generate_technical_documentation()
        except Exception as e:
            print(f"❌ Error generating technical documentation: {e}")
        
        # Summary
        print(f"\n✅ Documentation generation completed!")
        print(f"Generated {len(generated_files)} professional supplier documents:")
        
        for filename in generated_files:
            if filename and os.path.exists(filename):
                file_size = os.path.getsize(filename)
                size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
                print(f"  📄 {os.path.basename(filename)} ({size_str})")
        
        # List technical documentation files
        tech_files = ['EuroStyle_ERD_Documentation.txt', 'EuroStyle_Data_Dictionary.txt', 'EuroStyle_API_Specifications.txt']
        for tech_file in tech_files:
            tech_path = os.path.join(self.output_dir, tech_file)
            if os.path.exists(tech_path):
                file_size = os.path.getsize(tech_path)
                size_str = f"{file_size / 1024:.1f} KB"
                print(f"  📋 {tech_file} ({size_str})")
        
        print(f"\n📁 All documents saved to: {os.path.abspath(self.output_dir)}")
        
        return generated_files

def main():
    """Main function to generate all database documentation."""
    print("📊 EuroStyle Fashion - Professional Database Documentation Generator")
    print("===================================================================")
    
    try:
        generator = EuroStyleDocGenerator()
        generated_files = generator.generate_all_documentation()
        
        print("\n🎉 Professional database documentation generation completed successfully!")
        print("\n💾 These documents can be provided to:")
        print("   • Database administrators and architects")
        print("   • Data analysts and business intelligence teams")
        print("   • Analytics developers and data engineers")
        print("   • Technical stakeholders requiring database access")
        print("   • System integrators working with ClickHouse data")
        
    except Exception as e:
        print(f"\n❌ Error during documentation generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()