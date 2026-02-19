"""
Report Generator

Generates professional security reports in multiple formats (JSON, HTML, PDF).
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates security scan reports in multiple formats
    
    Supported formats:
    - JSON: Machine-readable, full data
    - HTML: Interactive web report
    - PDF: Executive summary
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize report generator
        
        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Register custom filters
        self.jinja_env.filters['b64encode'] = lambda x: base64.b64encode(x.encode()).decode()
        
        logger.info(f"Report generator initialized with templates: {self.templates_dir}")
    
    def generate_all(
        self,
        scan_results: Dict[str, Any],
        output_dir: Path,
        formats: List[str] = None
    ) -> Dict[str, Path]:
        """
        Generate reports in all requested formats
        
        Args:
            scan_results: Scan results dictionary
            output_dir: Output directory
            formats: List of formats to generate (default: all)
            
        Returns:
            Dictionary mapping format to output file path
        """
        if formats is None:
            formats = ['json', 'html', 'pdf']
        
        # Create output directory structure
        scan_id = scan_results.get('scan_id', 'unknown')
        target_name = self._sanitize_filename(scan_results.get('target', 'unknown'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report_dir = Path(output_dir) / f"{timestamp}_{target_name}"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Create evidence subdirectory
        evidence_dir = report_dir / "evidence"
        evidence_dir.mkdir(exist_ok=True)
        
        output_files = {}
        
        # Generate each format
        if 'json' in formats:
            json_file = self._generate_json(scan_results, report_dir)
            output_files['json'] = json_file
            logger.info(f"Generated JSON report: {json_file}")
        
        if 'html' in formats:
            html_file = self._generate_html(scan_results, report_dir, evidence_dir)
            output_files['html'] = html_file
            logger.info(f"Generated HTML report: {html_file}")
        
        if 'pdf' in formats:
            pdf_file = self._generate_pdf(scan_results, report_dir)
            output_files['pdf'] = pdf_file
            logger.info(f"Generated PDF report: {pdf_file}")
        
        # Generate metadata file
        self._generate_metadata(scan_results, report_dir)
        
        return output_files
    
    def _generate_json(self, scan_results: Dict[str, Any], output_dir: Path) -> Path:
        """Generate JSON report"""
        output_file = output_dir / "report.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scan_results, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def _generate_html(
        self,
        scan_results: Dict[str, Any],
        output_dir: Path,
        evidence_dir: Path
    ) -> Path:
        """Generate HTML report"""
        output_file = output_dir / "report.html"
        
        # Prepare template context
        context = self._prepare_report_context(scan_results)
        context['evidence_dir'] = evidence_dir.name
        
        # Render template
        template = self.jinja_env.get_template('html_report_template.html')
        html_content = template.render(**context)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_pdf(self, scan_results: Dict[str, Any], output_dir: Path) -> Path:
        """Generate PDF report"""
        output_file = output_dir / "report.pdf"
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Container for elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            elements.append(Paragraph("EMYUEL Security Scan Report", title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            elements.append(Paragraph("Executive Summary", styles['Heading1']))
            elements.append(Spacer(1, 0.2*inch))
            
            summary_data = [
                ["Target", scan_results.get('target', 'N/A')],
                ["Scan ID", scan_results.get('scan_id', 'N/A')],
                ["Scan Date", scan_results.get('start_time', 'N/A')],
                ["Duration", f"{scan_results.get('duration_seconds', 0):.2f} seconds"],
                ["Files Scanned", str(scan_results.get('files_scanned', 0))],
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Vulnerability Statistics
            elements.append(Paragraph("Vulnerability Statistics", styles['Heading1']))
            elements.append(Spacer(1, 0.2*inch))
            
            findings_by_severity = scan_results.get('findings_by_severity', {})
            
            vuln_data = [
                ["Severity", "Count"],
                ["Critical", str(findings_by_severity.get('critical', 0))],
                ["High", str(findings_by_severity.get('high', 0))],
                ["Medium", str(findings_by_severity.get('medium', 0))],
                ["Low", str(findings_by_severity.get('low', 0))],
            ]
            
            vuln_table = Table(vuln_data, colWidths=[3*inch, 2*inch])
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(vuln_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Critical Findings
            critical_findings = [
                f for f in scan_results.get('findings', [])
                if f.get('severity', '').lower() == 'critical'
            ]
            
            if critical_findings:
                elements.append(PageBreak())
                elements.append(Paragraph("Critical Findings", styles['Heading1']))
                elements.append(Spacer(1, 0.2*inch))
                
                for i, finding in enumerate(critical_findings[:5], 1):  # Limit to 5
                    elements.append(Paragraph(f"{i}. {finding.get('title', 'Untitled')}", styles['Heading2']))
                    elements.append(Paragraph(f"<b>File:</b> {finding.get('file_path', 'N/A')}", styles['Normal']))
                    elements.append(Paragraph(f"<b>Type:</b> {finding.get('type', 'N/A')}", styles['Normal']))
                    elements.append(Paragraph(f"<b>Description:</b> {finding.get('description', 'N/A')}", styles['Normal']))
                    elements.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            doc.build(elements)
            
        except ImportError:
            logger.warning("reportlab not installed, skipping PDF generation")
            # Create placeholder
            with open(output_file, 'w') as f:
                f.write("PDF generation requires reportlab library\n")
                f.write("Install with: pip install reportlab\n")
        
        return output_file
    
    def _generate_metadata(self, scan_results: Dict[str, Any], output_dir: Path):
        """Generate metadata file"""
        metadata = {
            'scan_id': scan_results.get('scan_id'),
            'target': scan_results.get('target'),
            'generated_at': datetime.now().isoformat(),
            'total_findings': scan_results.get('total_findings', 0),
            'report_version': '1.0'
        }
        
        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _prepare_report_context(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template context from scan results"""
        findings_by_severity = scan_results.get('findings_by_severity', {})
        findings = scan_results.get('findings', [])
        
        # Group findings by tool
        findings_by_tool = {}
        for f in findings:
            tool = f.get('tool', f.get('source', 'AI Scanner'))
            if tool.startswith('external:'):
                tool = tool.replace('external:', '')
            if tool not in findings_by_tool:
                findings_by_tool[tool] = []
            findings_by_tool[tool].append(f)
        
        context = {
            'scan_id': scan_results.get('scan_id', 'Unknown'),
            'target': scan_results.get('target', 'Unknown'),
            'start_time': scan_results.get('start_time', 'Unknown'),
            'end_time': scan_results.get('end_time', 'Unknown'),
            'duration': scan_results.get('duration_seconds', 0),
            'files_scanned': scan_results.get('files_scanned', 0),
            'total_findings': scan_results.get('total_findings', 0),
            'critical_count': findings_by_severity.get('critical', 0),
            'high_count': findings_by_severity.get('high', 0),
            'medium_count': findings_by_severity.get('medium', 0),
            'low_count': findings_by_severity.get('low', 0),
            'findings': findings,
            'findings_by_type': scan_results.get('findings_by_type', {}),
            'findings_by_tool': findings_by_tool,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return context
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for safe filesystem usage"""
        import re
        # Remove protocol and special chars
        name = re.sub(r'https?://', '', name)
        name = re.sub(r'[^\w\s-]', '_', name)
        name = re.sub(r'[-\s]+', '_', name)
        return name[:50]  # Limit length
