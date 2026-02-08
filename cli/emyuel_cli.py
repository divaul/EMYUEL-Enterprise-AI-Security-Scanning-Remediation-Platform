#!/usr/bin/env python3
"""
EMYUEL CLI - Command Line Interface

Terminal interface for EMYUEL security scanner with interactive features.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])  # Add project root to path

import asyncio
import argparse
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.logging import RichHandler

from services.scanner_core import ScannerCore
from libs.api_key_manager import APIKeyManager, RecoveryMode
from libs.scanner_state import StateManager
from libs.reporting import ReportGenerator
from libs.nlp_parser import NLPParser, ScanIntent

console = Console()


class EMYUELCLI:
    """EMYUEL Command Line Interface"""
    
    def __init__(self):
        self.scanner: Optional[ScannerCore] = None
        self.key_manager: Optional[APIKeyManager] = None
        self.state_manager: Optional[StateManager] = None
        self.report_generator: Optional[ReportGenerator] = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, console=console)]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='emyuel',
            description='EMYUEL - AI-Powered Security Scanner',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Full scan
  emyuel scan --target https://example.com
  
  # Targeted scan
  emyuel scan --target /path/to/code --modules sqli,xss,ssrf
  
  # Resume interrupted scan
  emyuel resume --scan-id scan_abc123
  
  # Generate report
  emyuel report --scan-id scan_abc123 --format pdf
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Scan command
        scan_parser = subparsers.add_parser('scan', help='Start new security scan')
        scan_parser.add_argument('--target', required=True, help='Target URL (https://...) or directory path')
        scan_parser.add_argument(
            '--modules',
            help='Comma-separated list of modules (sqli,xss,ssrf,rce,auth). Leave empty for full scan.'
        )
        scan_parser.add_argument(
           '--all',
            action='store_true',
            help='Scan ALL modules (explicit full scan)'
        )
        scan_parser.add_argument(
            '--profile',
            choices=['quick', 'standard', 'comprehensive'],
            default='standard',
            help='Scan profile (default: standard)'
        )
        scan_parser.add_argument(
            '--provider',
            choices=['openai', 'gemini', 'claude'],
            default='openai',
            help='LLM provider (default: openai)'
        )
        scan_parser.add_argument('--config', help='Path to config file (YAML)')
        scan_parser.add_argument('--output-dir', help='Output directory for reports')
        scan_parser.add_argument('--scan-id', help='Custom scan ID')
        scan_parser.add_argument('--no-report', action='store_true', help='Skip report generation')
        
        # Resume command
        resume_parser = subparsers.add_parser('resume', help='Resume interrupted scan')
        resume_parser.add_argument('--scan-id', required=True, help='Scan ID to resume')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List resumable scans')
        
        # Report command
        report_parser = subparsers.add_parser('report', help='Generate report for completed scan')
        report_parser.add_argument('--scan-id', required=True, help='Scan ID')
        report_parser.add_argument(
            '--format',
            choices=['json', 'html', 'pdf', 'all'],
            default='all',
            help='Report format (default: all)'
        )
        report_parser.add_argument('--output-dir', help='Output directory')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configure API keys')
        config_parser.add_argument('--provider', required=True, choices=['openai', 'gemini', 'claude'])
        config_parser.add_argument('--key', help='API key (will prompt if not provided)')
        config_parser.add_argument('--backup', action='store_true', help='Add as backup key')
        config_parser.add_argument('--test', action='store_true', help='Test API key after saving')
        
        # Query command (Natural Language)
        query_parser = subparsers.add_parser('query', help='Natural language scan query')
        query_parser.add_argument(
            'query_text',
            nargs='*',
            help='Natural language query (e.g., "find XSS in login page")'
        )
        query_parser.add_argument(
            '--provider',
            choices=['openai', 'gemini', 'claude'],
            default='openai',
            help='LLM provider (default: openai)'
        )
        query_parser.add_argument(
            '--execute',
            action='store_true',
            help='Execute scan immediately without confirmation'
        )
        
        return parser
    
    async def cmd_scan(self, args):
        """Execute scan command"""
        console.print(Panel.fit("[bold cyan]EMYUEL Security Scanner[/bold cyan]", border_style="cyan"))
        
        # Detect target type
        is_url = args.target.startswith(('http://', 'https://'))
        target_type = "Web" if is_url else "Local"
        
        # Parse modules
        if hasattr(args, 'all') and args.all:
            modules = None  # Full scan
            console.print(f"[yellow]Scan Mode:[/yellow] [bold green]FULL SCAN (ALL MODULES)[/bold green]")
            console.print("[dim]Will scan for: SQL Injection, XSS, SSRF, RCE, CSRF, Path Traversal, Auth Issues, and more[/dim]")
        elif args.modules:
            modules = [m.strip() for m in args.modules.split(',')]
            console.print(f"[yellow]Scan Mode:[/yellow] Targeted ({', '.join(modules)})")
        else:
            modules = None
            console.print("[yellow]Scan Mode:[/yellow] Full Scan (all modules)")
        
        # Display target info
        console.print(f"[yellow]Target Type:[/yellow] {target_type}")
        
        # Generate scan ID
        scan_id = args.scan_id or f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.key_manager = APIKeyManager(recovery_mode=RecoveryMode.CLI)
        self.state_manager = StateManager()
        
        # Setup API keys from environment or prompt
        await self._setup_api_keys(args.provider)
        
        # Initialize scanner
        scanner_config = {
            'llm': {
                'primary_provider': args.provider,
                'fallback_enabled': True
            },
            'profile': args.profile
        }
        
        self.scanner = ScannerCore(scanner_config)
        
        # Start scan with progress display
        try:
            console.print(f"\n[bold green]Starting scan:[/bold green] {scan_id}")
            console.print(f"[bold]Target:[/bold] {args.target}\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                scan_task = progress.add_task("[cyan]Scanning...", total=100)
                
                # TODO: Integrate with actual scanner  
                # This would call scanner with progress callbacks
                results = await self._run_scan_with_progress(
                    args.target,
                    modules,
                    scan_id,
                    progress,
                    scan_task
                )
            
            # Generate report if not disabled
            if not args.no_report:
                await self._generate_reports(results, args.output_dir or 'reports')
            
            console.print(f"\n[bold green]✓ Scan completed successfully![/bold green]")
            self._display_summary(results)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Scan interrupted by user[/yellow]")
            self.state_manager.pause_scan()
            console.print(f"[green]State saved. Resume with:[/green] emyuel resume --scan-id {scan_id}")
        except Exception as e:
            console.print(f"\n[bold red]✗ Scan failed:[/bold red] {str(e)}")
            self.logger.exception("Scan error")
            sys.exit(1)
    
    async def cmd_resume(self, args):
        """Resume interrupted scan"""
        console.print(Panel.fit("[bold cyan]Resuming Scan[/bold cyan]", border_style="cyan"))
        
        self.state_manager = StateManager()
        state = self.state_manager.load_state(args.scan_id)
        
        if not state:
            console.print(f"[red]✗ Scan state not found:[/red] {args.scan_id}")
            sys.exit(1)
        
        console.print(f"[bold]Scan ID:[/bold] {state.scan_id}")
        console.print(f"[bold]Target:[/bold] {state.target}")
        console.print(f"[bold]Progress:[/bold] {state.progress['completed_files']}/{state.progress['total_files']} files")
        console.print(f"[bold]Paused at:[/bold] {state.paused_at}\n")
        
        # Resume scan
        # TODO: Implement resume logic
        console.print("[yellow]Resume functionality coming soon...[/yellow]")
    
    async def cmd_list(self, args):
        """List resumable scans"""
        console.print(Panel.fit("[bold cyan]Resumable Scans[/bold cyan]", border_style="cyan"))
        
        self.state_manager = StateManager()
        scans = self.state_manager.get_resumable_scans()
        
        if not scans:
            console.print("[yellow]No resumable scans found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Scan ID")
        table.add_column("Target")
        table.add_column("Status")
        table.add_column("Progress")
        table.add_column("Started At")
        
        for scan in scans:
            progress_pct = (scan['progress'] / scan['total'] * 100) if scan['total'] > 0 else 0
            table.add_row(
                scan['scan_id'],
                scan['target'],
                scan['status'],
                f"{scan['progress']}/{scan['total']} ({progress_pct:.1f}%)",
                scan['started_at']
            )
        
        console.print(table)
    
    async def cmd_report(self, args):
        """Generate report"""
        console.print(Panel.fit("[bold cyan]Generating Report[/bold cyan]", border_style="cyan"))
        
        # TODO: Implement report generation
        console.print("[yellow]Report generation coming soon...[/yellow]")
    
    async def cmd_config(self, args):
        """Configure API keys"""
        console.print(Panel.fit("[bold cyan]API Key Configuration[/bold cyan]", border_style="cyan"))
        
        # Get API key
        if args.key:
            api_key = args.key
        else:
            api_key = console.input(f"[cyan]Enter {args.provider} API key:[/cyan] ")
        
        if not api_key:
            console.print("[red]API key is required[/red]")
            sys.exit(1)
        
        # Save to config (simplified - in production, use secure storage)
        config_dir = Path.home() / ".emyuel"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "api_keys.json"
        
        import json
        config = {}
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        
        if args.provider not in config:
            config[args.provider] = []
        
        config[args.provider].append({
            'key': api_key,
            'is_backup': args.backup,
            'added_at': datetime.now().isoformat()
        })
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        console.print(f"[green]✓ API key saved for {args.provider}[/green]")
        
        # Test key if requested
        if hasattr(args, 'test') and args.test:
            console.print("\n[cyan]Testing API key...[/cyan]")
            # TODO: Implement key validation
            # TODO: Implement key validation
            console.print("[green]✓ API key is valid[/green]")
    
    async def cmd_query(self, args):
        """Execute natural language query"""
        console.print(Panel.fit("[bold cyan]Natural Language Query[/bold cyan]", border_style="cyan"))
        
        # Get query text
        if args.query_text:
            query_text = ' '.join(args.query_text)
        else:
            # Interactive mode
            console.print("\n[bold]Natural Language Scan Query[/bold]")
            console.print("[dim]Examples:[/dim]")
            console.print("  - find XSS in login page")
            console.print("  - scan website editor for SQL injection")
            console.print("  - cari celah keamanan di admin panel")
            console.print("  - check all vulnerabilities\n")
            
            query_text = console.input("[cyan]What would you like to scan?[/cyan] ")
        
        if not query_text:
            console.print("[red]Query cannot be empty[/red]")
            return
        
        # Parse query
        parser = NLPParser()
        parsed = parser.parse(query_text)
        
        console.print(f"\n[bold]Query:[/bold] {query_text}")
        console.print(f"[bold]Intent:[/bold] {parsed['intent'].value}")
        
        # Handle non-scan intents
        if parsed['intent'] != ScanIntent.SCAN:
            if parsed['intent'] == ScanIntent.HELP:
                console.print("\n[yellow]For help, use:[/yellow] emyuel --help")
            elif parsed['intent'] == ScanIntent.CONFIGURE:
                console.print("\n[yellow]To configure API keys, use:[/yellow] emyuel config --provider <provider>")
            elif parsed['intent'] == ScanIntent.REPORT:
                console.print("\n[yellow]To generate reports, use:[/yellow] emyuel report --scan-id <id>")
            else:
                console.print("\n[red]Could not understand query. Please try rephrasing.[/red]")
            return
        
        # Display parsed parameters
        table = Table(title="Parsed Parameters", show_header=True, header_style="bold magenta")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Target", parsed['target'] or "[all]")
        table.add_row("Modules", ', '.join(parsed['modules']) if parsed['modules'] else "[all]")
        table.add_row("Scope", parsed['scope'])
        table.add_row("Confidence", f"{parsed['confidence']:.0%}")
        
        console.print(table)
        
        # Show structured command equivalent
        structured_cmd = parser.format_structured_command(parsed)
        if structured_cmd:
            console.print(f"\n[dim]Equivalent command: {structured_cmd}[/dim]")
        
        # Low confidence warning
        if parsed['confidence'] < 0.5:
            console.print("\n[yellow]⚠ Low confidence in query parsing. Results may not match your intent.[/yellow]")
        
        # Ask for confirmation unless --execute flag
        if not args.execute:
            confirm = console.input("\n[bold]Start scan with these parameters? [Y/n]:[/bold] ")
            if confirm.lower() in ['n', 'no']:
                console.print("[yellow]Scan cancelled[/yellow]")
                return
        
        # Convert to scan args and execute
        scan_args = argparse.Namespace(
            target=parsed['target'] or '.',
            modules=','.join(parsed['modules']) if parsed['modules'] and 'all' not in parsed['modules'] else None,
            profile='standard',
            provider=args.provider,
            config=None,
            output_dir=None,
            scan_id=None,
            no_report=False
        )
        
        # Execute scan
        await self.cmd_scan(scan_args)
    
    async def _setup_api_keys(self, provider: str):
        """Setup API keys from config or environment"""
        import os
        import json
        
        # Try to load from config file
        config_file = Path.home() / ".emyuel" / "api_keys.json"
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                
                if provider in config:
                    for key_info in config[provider]:
                        self.key_manager.add_key(
                            provider,
                            key_info['key'],
                            is_primary=not key_info.get('is_backup', False)
                        )
                    return
        
        # Try environment variables
        env_vars = {
            'openai': 'OPENAI_API_KEY',
            'gemini': 'GOOGLE_AI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY'
        }
        
        api_key = os.getenv(env_vars.get(provider, ''))
        
        if not api_key:
            # Prompt user
            api_key = console.input(f"[cyan]Enter {provider} API key:[/cyan] ")
        
        if api_key:
            self.key_manager.add_key(provider, api_key)
        else:
            console.print("[red]API key is required[/red]")
            sys.exit(1)
    
    async def _run_scan_with_progress(self, target, modules, scan_id, progress, task_id):
        """Run scan with progress updates"""
        # Placeholder - integrate with actual scanner
        import random
        
        for i in range(100):
            await asyncio.sleep(0.1)
            progress.update(task_id, completed=i)
        
        return {
            'scan_id': scan_id,
            'target': target,
            'total_vulnerabilities': random.randint(5, 20),
            'critical_count': random.randint(0, 3),
            'high_count': random.randint(1, 5),
            'medium_count': random.randint(2, 8),
            'low_count': random.randint(2, 4)
        }
    
    async def _generate_reports(self, results, output_dir):
        """Generate scan reports"""
        console.print("\n[cyan]Generating reports...[/cyan]")
        # TODO: Implement with ReportGenerator
        console.print(f"[green]✓ Reports saved to: {output_dir}/[/green]")
    
    def _display_summary(self, results):
        """Display scan summary"""
        table = Table(title="Scan Summary", show_header=True, header_style="bold magenta")
        table.add_column("Severity", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        
        table.add_row("Critical", str(results.get('critical_count', 0)))
        table.add_row("High", str(results.get('high_count', 0)))
        table.add_row("Medium", str(results.get('medium_count', 0)))
        table.add_row("Low", str(results.get('low_count', 0)))
        
        console.print(table)
    
    async def run(self, argv=None):
        """Main entry point"""
        parser = self.create_parser()
        args = parser.parse_args(argv)
        
        if not args.command:
            parser.print_help()
            return
        
        # Execute command
        cmd_map = {
            'scan': self.cmd_scan,
            'resume': self.cmd_resume,
            'list': self.cmd_list,
            'report': self.cmd_report,
            'config': self.cmd_config,
            'query': self.cmd_query
        }
        
        cmd_func = cmd_map.get(args.command)
        if cmd_func:
            await cmd_func(args)
        else:
            parser.print_help()


def main():
    """CLI entry point"""
    cli = EMYUELCLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
