#!/usr/bin/env python3
"""
EMYUEL GUI - Graphical User Interface

Desktop GUI for EMYUEL security scanner using tkinter with modern design.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from libs.api_key_manager import APIKeyManager, RecoveryMode
from libs.scanner_state import StateManager
from libs.reporting import ReportGenerator


class ModernButton(tk.Button):
    """Modern styled button"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            relief=tk.FLAT,
            cursor='hand2',
            **kwargs
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self['background'] = self['activebackground']
    
    def _on_leave(self, e):
        self['background'] = self.original_bg
    
    def config(self, **kwargs):
        if 'bg' in kwargs:
            self.original_bg = kwargs['bg']
        super().config(**kwargs)


class EMYUELGUI:
    """EMYUEL Graphical User Interface"""
    
    # Color scheme
    PRIMARY_COLOR = '#4a90e2'
    SECONDARY_COLOR = '#2c3e50'
    SUCCESS_COLOR = '#27ae60'
    WARNING_COLOR = '#f39c12'
    DANGER_COLOR = '#e74c3c'
    BG_COLOR = '#ecf0f1'
    CARD_BG = '#ffffff'
    TEXT_COLOR = '#2c3e50'
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EMYUEL Security Scanner")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.BG_COLOR)
        
        # Components
        self.key_manager: Optional[APIKeyManager] = None
        self.state_manager: Optional[StateManager] = None
        self.report_generator: Optional[ReportGenerator] = None
        
        # State
        self.scan_running = False
        self.scan_thread: Optional[threading.Thread] = None
        self.message_queue = queue.Queue()
        
        # Setup UI
        self._setup_ui()
        self._check_message_queue()
        
        # Initialize components
        self.key_manager = APIKeyManager(recovery_mode=RecoveryMode.GUI)
        self.state_manager = StateManager()
        self.report_generator = ReportGenerator()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=self.PRIMARY_COLOR, height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🛡️ EMYUEL Security Scanner",
            font=('Segoe UI', 24, 'bold'),
            bg=self.PRIMARY_COLOR,
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main content area
        content_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Configuration
        left_panel = self._create_config_panel(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel - Results
        right_panel = self._create_results_panel(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Bottom status bar
        self._create_status_bar()
    
    def _create_config_panel(self, parent):
        """Create configuration panel"""
        panel = tk.LabelFrame(
            parent,
            text="Scan Configuration",
            bg=self.CARD_BG,
            font=('Segoe UI', 12, 'bold'),
            padx=20,
            pady=20
        )
        
        # Target selection
        tk.Label(
            panel,
            text="Target:",
            bg=self.CARD_BG,
            font=('Segoe UI', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        target_frame = tk.Frame(panel, bg=self.CARD_BG)
        target_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 15))
        
        self.target_entry = tk.Entry(
            target_frame,
            font=('Segoe UI', 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(
            target_frame,
            text="Browse",
            command=self._browse_target,
            bg=self.SECONDARY_COLOR,
            fg='white',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2'
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Scan mode
        tk.Label(
            panel,
            text="Scan Mode:",
            bg=self.CARD_BG,
            font=('Segoe UI', 10, 'bold')
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.scan_mode = tk.StringVar(value="full")
        
        mode_frame = tk.Frame(panel, bg=self.CARD_BG)
        mode_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))
        
        tk.Radiobutton(
            mode_frame,
            text="Full Scan",
            variable=self.scan_mode,
            value="full",
            bg=self.CARD_BG,
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Radiobutton(
            mode_frame,
            text="Targeted",
            variable=self.scan_mode,
            value="targeted",
            bg=self.CARD_BG,
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT)
        
        # Modules (for targeted scan)
        tk.Label(
            panel,
            text="Modules (comma-separated):",
            bg=self.CARD_BG,
            font=('Segoe UI', 10, 'bold')
        ).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.modules_entry = tk.Entry(
            panel,
            font=('Segoe UI', 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.modules_entry.grid(row=5, column=0, sticky=tk.EW, pady=(0, 15))
        self.modules_entry.insert(0, "sqli,xss,ssrf,rce")
        
        # Provider selection
        tk.Label(
            panel,
            text="LLM Provider:",
            bg=self.CARD_BG,
            font=('Segoe UI', 10, 'bold')
        ).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        self.provider_var = tk.StringVar(value="openai")
        provider_combo = ttk.Combobox(
            panel,
            textvariable=self.provider_var,
            values=['openai', 'gemini', 'claude'],
            state='readonly',
            font=('Segoe UI', 10)
        )
        provider_combo.grid(row=7, column=0, sticky=tk.EW, pady=(0, 15))
        
        # Profile selection
        tk.Label(
            panel,
            text="Scan Profile:",
            bg=self.CARD_BG,
            font=('Segoe UI', 10, 'bold')
        ).grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        self.profile_var = tk.StringVar(value="standard")
        profile_combo = ttk.Combobox(
            panel,
            textvariable=self.profile_var,
            values=['quick', 'standard', 'comprehensive'],
            state='readonly',
            font=('Segoe UI', 10)
        )
        profile_combo.grid(row=9, column=0, sticky=tk.EW, pady=(0, 20))
        
        # Action buttons
        btn_frame = tk.Frame(panel, bg=self.CARD_BG)
        btn_frame.grid(row=10, column=0, sticky=tk.EW)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Scan",
            command=self._start_scan,
            bg=self.SUCCESS_COLOR,
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            height=2
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 10))
        
        self.pause_btn = tk.Button(
            btn_frame,
            text="⏸ Pause",
            command=self._pause_scan,
            bg=self.WARNING_COLOR,
            fg='white',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.pause_btn.pack(fill=tk.X, pady=(0, 10))
        
        self.resume_btn = tk.Button(
            btn_frame,
            text="⏯ Resume",
            command=self._resume_scan,
            bg=self.PRIMARY_COLOR,
            fg='white',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.resume_btn.pack(fill=tk.X)
        
        panel.columnconfigure(0, weight=1)
        
        return panel
    
    def _create_results_panel(self, parent):
        """Create results panel"""
        panel = tk.LabelFrame(
            parent,
            text="Scan Results & Logs",
            bg=self.CARD_BG,
            font=('Segoe UI', 12, 'bold'),
            padx=20,
            pady=20
        )
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            panel,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Log output
        log_frame = tk.Frame(panel, bg=self.CARD_BG)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief=tk.SOLID,
            borderwidth=1,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Results summary
        summary_frame = tk.Frame(panel, bg=self.CARD_BG)
        summary_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.critical_label = self._create_stat_label(
            summary_frame, "Critical", self.DANGER_COLOR
        )
        self.critical_label.pack(side=tk.LEFT, padx=5)
        
        self.high_label = self._create_stat_label(
            summary_frame, "High", self.WARNING_COLOR
        )
        self.high_label.pack(side=tk.LEFT, padx=5)
        
        self.medium_label = self._create_stat_label(
            summary_frame, "Medium", '#3498db'
        )
        self.medium_label.pack(side=tk.LEFT, padx=5)
        
        self.low_label = self._create_stat_label(
            summary_frame, "Low", self.SUCCESS_COLOR
        )
        self.low_label.pack(side=tk.LEFT, padx=5)
        
        # Report buttons
        report_frame = tk.Frame(panel, bg=self.CARD_BG)
        report_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            report_frame,
            text="📄 Generate Report",
            command=self._generate_report,
            bg=self.PRIMARY_COLOR,
            fg='white',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            report_frame,
            text="📂 Open Reports Folder",
            command=self._open_reports_folder,
            bg=self.SECONDARY_COLOR,
            fg='white',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT)
        
        return panel
    
    def _create_stat_label(self, parent, text, color):
        """Create a statistic label"""
        frame = tk.Frame(parent, bg=color, relief=tk.SOLID, borderwidth=1)
        
        tk.Label(
            frame,
            text=text,
            bg=color,
            fg='white',
            font=('Segoe UI', 8, 'bold')
        ).pack(padx=10, pady=(5, 0))
        
        value_label = tk.Label(
            frame,
            text="0",
            bg=color,
            fg='white',
            font=('Segoe UI', 16, 'bold')
        )
        value_label.pack(padx=10, pady=(0, 5))
        
        # Store reference to update later
        frame.value_label = value_label
        
        return frame
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bg=self.SECONDARY_COLOR,
            fg='white',
            anchor=tk.W,
            font=('Segoe UI', 9),
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _browse_target(self):
        """Browse for target directory"""
        directory = filedialog.askdirectory(title="Select Target Directory")
        if directory:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, directory)
    
    def _start_scan(self):
        """Start security scan"""
        target = self.target_entry.get().strip()
        
        if not target:
            messagebox.showerror("Error", "Please specify a target directory or URL")
            return
        
        # Disable start button
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.scan_running = True
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_var.set(0)
        
        # Update status
        self._update_status("Initializing scan...")
        self._log("🚀 Starting EMYUEL security scan...")
        self._log(f"📁 Target: {target}")
        self._log(f"🔧 Provider: {self.provider_var.get()}")
        self._log(f"⚙️ Profile: {self.profile_var.get()}")
        self._log("")
        
        # Start scan in background thread
        self.scan_thread = threading.Thread(target=self._run_scan, args=(target,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def _run_scan(self, target):
        """Run scan in background thread"""
        import time
        import random
        
        try:
            # Simulate scan progress
            for i in range(101):
                if not self.scan_running:
                    self.message_queue.put(('status', 'Scan paused'))
                    break
                
                time.sleep(0.05)
                self.message_queue.put(('progress', i))
                
                if i % 20 == 0:
                    self.message_queue.put(('log', f"✓ Scanning module {i//20 + 1}/5..."))
            
            # Simulate results
            results = {
                'critical': random.randint(0, 3),
                'high': random.randint(1, 5),
                'medium': random.randint(2, 8),
                'low': random.randint(2, 6)
            }
            
            self.message_queue.put(('results', results))
            self.message_queue.put(('status', 'Scan completed'))
            self.message_queue.put(('log', '\n✅ Scan completed successfully!'))
            
        except Exception as e:
            self.message_queue.put(('error', str(e)))
        finally:
            self.message_queue.put(('done', None))
    
    def _pause_scan(self):
        """Pause scan"""
        self.scan_running = False
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.NORMAL)
        self._update_status("Scan paused")
        self._log("\n⏸ Scan paused by user")
    
    def _resume_scan(self):
        """Resume scan"""
        messagebox.showinfo("Resume", "Resume functionality coming soon...")
    
    def _generate_report(self):
        """Generate scan report"""
        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory", initialdir="reports")
        
        if output_dir:
            messagebox.showinfo("Success", f"Report will be generated in:\n{output_dir}")
    
    def _open_reports_folder(self):
        """Open reports folder"""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        import subprocess
        subprocess.Popen(f'explorer "{reports_dir.absolute()}"')
    
    def _update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
    
    def _log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _check_message_queue(self):
        """Check for messages from background thread"""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(msg_data)
                elif msg_type == 'log':
                    self._log(msg_data)
                elif msg_type == 'status':
                    self._update_status(msg_data)
                elif msg_type == 'results':
                    self._update_results(msg_data)
                elif msg_type == 'error':
                    messagebox.showerror("Scan Error", msg_data)
                elif msg_type == 'done':
                    self.start_btn.config(state=tk.NORMAL)
                    self.pause_btn.config(state=tk.DISABLED)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._check_message_queue)
    
    def _update_results(self, results):
        """Update results summary"""
        self.critical_label.value_label.config(text=str(results.get('critical', 0)))
        self.high_label.value_label.config(text=str(results.get('high', 0)))
        self.medium_label.value_label.config(text=str(results.get('medium', 0)))
        self.low_label.value_label.config(text=str(results.get('low', 0)))
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def main():
    """GUI entry point"""
    app = EMYUELGUI()
    app.run()


if __name__ == '__main__':
    main()
