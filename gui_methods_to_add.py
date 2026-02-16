# GUI Methods to Add to emyuel_gui.py
# Copy these methods to the EMYUELGUI class

def generate_ai_report(self):
    """Generate AI-enhanced professional report"""
    self.log_console("[AI REPORT] Generating AI-enhanced report...")
    
    # Check for scan results
    if not hasattr(self, 'last_scan_results') or self.last_scan_results is None:
        messagebox.showerror("No Results", "No scan results available. Please run a scan first.")
        self.log_console("[ERROR] No scan results to generate report from")
        return
    
    try:
        import sys
        from pathlib import Path
        
        parent_dir = Path(__file__).resolve().parent.parent
        libs_dir = parent_dir / "libs" / "reporting"
        if str(libs_dir) not in sys.path:
            sys.path.insert(0, str(libs_dir))
        
        from ai_report_formatter import AIReportFormatter
        from api_key_manager import APIKeyManager
        
        # Get AI provider selection
        provider = self.ai_report_provider_var.get()
        self.log_console(f"[AI REPORT] Using {provider.upper()} for report formatting...")
        
        # Initialize AI formatter
        api_mgr = APIKeyManager()
        
        # Check if we have existing LLM analyzer or create new one
        scanner_core_dir = parent_dir / "services" / "scanner-core"
        if str(scanner_core_dir) not in sys.path:
            sys.path.insert(0, str(scanner_core_dir))
        
        from llm_analyzer import LLMAnalyzer
        llm = LLMAnalyzer(api_mgr, provider)
        formatter = AIReportFormatter(llm)
        
        self.log_console("[AI REPORT] Sending results to AI for formatting...")
        self.log_console("[AI REPORT] This may take 30-60 seconds...")
        
        # Format report with AI
        ai_report_md = formatter.format_report(self.last_scan_results, provider=provider)
        
        # Create reports directory
        reports_dir = parent_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Create timestamped subdirectory
        target_name = self.last_scan_results.get('target', 'unknown').replace('://', '_').replace('/', '_')[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = reports_dir / f"{timestamp}_{target_name}_AI"
        report_dir.mkdir(exist_ok=True)
        
        # Save Markdown
        md_path = report_dir / "ai_enhanced_report.md"
        md_path.write_text(ai_report_md, encoding='utf-8')
        self.log_console(f"[AI REPORT] Markdown saved: {md_path}")
        
        # Convert to HTML
        html_path = self._convert_markdown_to_html(ai_report_md, report_dir)
        
        self.log_console(f"[AI REPORT] ✅ AI-Enhanced report generated!")
        self.log_console(f"[AI REPORT] HTML: {html_path}")
        self.log_console(f"[AI REPORT] Markdown: {md_path}")
        
        # Show success message
        message = f"AI-Enhanced Report Generated!\n\n"
        message += f"Provider: {provider.upper()}\n\n"
        message += f"Output files:\n"
        message += f"  • HTML: {html_path}\n"
        message += f"  • Markdown: {md_path}\n\n"
        message += f"Report directory: {report_dir}"
        
        messagebox.showinfo("AI Report Complete", message)
        
        # Open HTML in browser
        import webbrowser
        webbrowser.open(f"file://{html_path}")
        
        # Refresh report history
        self.refresh_report_history()
        
    except Exception as e:
        error_msg = f"Error generating AI report: {e}"
        self.log_console(f"[ERROR] {error_msg}")
        messagebox.showerror("AI Report Error", error_msg)
        import traceback
        traceback.print_exc()

def generate_raw_report(self):
    """Generate raw JSON/HTML report"""
    # Use existing report generation method
    self.generate_report()
    
    # Refresh history after generation
    self.refresh_report_history()

def _convert_markdown_to_html(self, markdown_content: str, output_dir: Path) -> Path:
    """Convert Markdown to styled HTML"""
    html_file = output_dir / "ai_enhanced_report.html"
    
    try:
        # Try using markdown library
        import markdown
        
        html_body = markdown.markdown(
            markdown_content,
            extensions=['fenced_code', 'tables', 'toc', 'nl2br']
        )
        
        # Wrap in professional template
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Enhanced Security Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }}
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            color: #ecf0f1;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            background-color: #ecf0f1;
            padding: 10px 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="content">
        {html_body}
    </div>
</body>
</html>"""
        
        html_file.write_text(html_template, encoding='utf-8')
        
    except ImportError:
        # Fallback: simple HTML without markdown conversion
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI-Enhanced Security Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 15px; overflow-x: auto; }}
    </style>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>"""
        html_file.write_text(html_template, encoding='utf-8')
    
    return html_file

def refresh_report_history(self):
    """Refresh report history list"""
    if not hasattr(self, 'report_history_text'):
        return
    
    try:
        from pathlib import Path
        
        parent_dir = Path(__file__).resolve().parent.parent
        reports_dir = parent_dir / "reports"
        
        if not reports_dir.exists():
            self.report_history_text.config(state='normal')
            self.report_history_text.delete('1.0', tk.END)
            self.report_history_text.insert('1.0', "No reports generated yet.\n\nGenerate a report to see it listed here.")
            self.report_history_text.config(state='disabled')
            return
        
        # Get all report directories
        report_dirs = sorted([d for d in reports_dir.iterdir() if d.is_dir()], 
                           key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not report_dirs:
            self.report_history_text.config(state='normal')
            self.report_history_text.delete('1.0', tk.END)
            self.report_history_text.insert('1.0', "No reports generated yet.")
            self.report_history_text.config(state='disabled')
            return
        
        # Build history text
        history_text = "Recent Reports:\n\n"
        
        for report_dir in report_dirs[:10]:  # Show last 10
            dir_name = report_dir.name
            timestamp_str = dir_name[:15] if len(dir_name) >= 15 else "Unknown"
            
            # Try to parse timestamp
            try:
                from datetime import datetime
                dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = timestamp_str
            
            # Determine report type
            report_type = "AI-Enhanced" if "_AI" in dir_name else "Raw"
            
            # Find report files
            html_files = list(report_dir.glob("*.html"))
            html_path = html_files[0] if html_files else None
            
            history_text += f"📄 {date_str} - {report_type}\n"
            history_text += f"   {report_dir.name}\n"
            if html_path:
                history_text += f"   Path: {html_path}\n"
            history_text += "\n"
        
        self.report_history_text.config(state='normal')
        self.report_history_text.delete('1.0', tk.END)
        self.report_history_text.insert('1.0', history_text)
        self.report_history_text.config(state='disabled')
        
    except Exception as e:
        self.log_console(f"[ERROR] Failed to refresh report history: {e}")

def update_report_summary(self):
    """Update report summary after scan completes"""
    if not hasattr(self, 'report_summary_label') or not hasattr(self, 'last_scan_results'):
        return
    
    if self.last_scan_results is None:
        summary = "No scan completed yet. Run a scan first to generate reports."
    else:
        target = self.last_scan_results.get('target', 'Unknown')
        total = self.last_scan_results.get('total_findings', 0)
        severity = self.last_scan_results.get('findings_by_severity', {})
        scan_time = self.last_scan_results.get('start_time', 'Unknown')
        
        summary = f"Target: {target}\n"
        summary += f"Scan Date: {scan_time}\n"
        summary += f"Total Findings: {total} vulnerabilities\n"
        summary += f"Critical: {severity.get('critical', 0)} | "
        summary += f"High: {severity.get('high', 0)} | "
        summary += f"Medium: {severity.get('medium', 0)} | "
        summary += f"Low: {severity.get('low', 0)}"
        
        # Enable report buttons
        if hasattr(self, 'generate_ai_report_btn'):
            self.generate_ai_report_btn.config(state='normal')
        if hasattr(self, 'generate_raw_report_btn'):
            self.generate_raw_report_btn.config(state='normal')
    
    self.report_summary_label.config(text=summary)
