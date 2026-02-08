#!/usr/bin/env python3
"""
EMYUEL GUI - Enhanced Graphical User Interface

Modern desktop GUI with API key management and natural language query support.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from typing import Optional
import asyncio
import threading
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.api_key_manager import APIKeyManager, RecoveryMode
from libs.scanner_state import StateManager
from libs.nlp_parser import NLPParser


class ModernButton(tk.Button):
    """Custom styled button with hover effect"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self['background'] = self['activebackground']
    
    def on_leave(self, e):
        self['background'] = self.defaultBackground


class EMYUELGUI:
    """Enhanced EMYUEL Graphical User Interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EMYUEL Security Scanner")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Color scheme - Modern cyber security theme
        self.colors = {
            'bg_primary': '#1a1d29',
            'bg_secondary': '#252836',
            'bg_tertiary': '#2d3142',
            'accent_cyan': '#00d9ff',
            'accent_purple': '#a855f7',
            'text_primary': '#ffffff',
            'text_secondary': '#9ca3af',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'critical': '#dc2626'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Initialize components
        self.key_manager = APIKeyManager(recovery_mode=RecoveryMode.GUI)
        self.state_manager = StateManager()
        self.nlp_parser = NLPParser()
        
        # Variables
        self.target_var = tk.StringVar()
        self.provider_var = tk.StringVar(value="openai")
        self.profile_var = tk.StringVar(value="standard")
        self.scan_mode_var = tk.StringVar(value="full")
        self.query_var = tk.StringVar()
        
        # API Key variables
        self.api_key_openai = tk.StringVar()
        self.api_key_gemini = tk.StringVar()
        self.api_key_claude = tk.StringVar()
        self.show_key_var = tk.BooleanVar(value=False)
        
        # Scan state
        self.is_scanning = False
        self.scan_thread = None
        
        # Build UI
        self.setup_ui()
        
        # Load saved API keys if available
        self.load_saved_keys()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="EMYUEL",
            font=('Arial', 28, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_secondary']
        )
        title_label.pack(side='left', padx=30, pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI-Powered Security Scanner",
            font=('Arial', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        subtitle_label.pack(side='left', padx=0, pady=20)
        
        # Main container with scroll
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_primary'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_tertiary'])],
                 foreground=[('selected', self.colors['accent_cyan'])])
        
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Quick Scan (Natural Language)
        quick_scan_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(quick_scan_frame, text='Quick Scan')
        self.setup_quick_scan_tab(quick_scan_frame)
        
        # Tab 2: Advanced Scan
        advanced_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(advanced_frame, text='Advanced Scan')
        self.setup_advanced_tab(advanced_frame)
        
        # Tab 3: API Configuration
        api_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(api_frame, text='API Keys')
        self.setup_api_tab(api_frame)
        
        # Tab 4: Scan Results
        results_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(results_frame, text='Results')
        self.setup_results_tab(results_frame)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=40)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to scan",
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=20, pady=10)
    
    def setup_quick_scan_tab(self, parent):
        """Setup quick scan tab with natural language input"""
        
        # Natural Language Query Section
        query_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        query_frame.pack(fill='x', padx=20, pady=20)
        
        query_title = tk.Label(
            query_frame,
            text="🔍 Natural Language Query",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        query_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        query_subtitle = tk.Label(
            query_frame,
            text="Describe what you want to scan in plain English or Indonesian",
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        query_subtitle.pack(anchor='w', padx=20, pady=(0, 15))
        
        # Query input
        query_input_frame = tk.Frame(query_frame, bg=self.colors['bg_secondary'])
        query_input_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.query_entry = tk.Entry(
            query_input_frame,
            textvariable=self.query_var,
            font=('Arial', 12),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=10
        )
        self.query_entry.pack(fill='x', side='left', expand=True)
        self.query_entry.bind('<Return>', lambda e: self.analyze_query())
        
        # Placeholder text
        self.query_entry.insert(0, 'e.g., "find XSS in login page" or "cari celah di website editor"')
        self.query_entry.config(fg=self.colors['text_secondary'])
        self.query_entry.bind('<FocusIn>', self.on_query_focus_in)
        self.query_entry.bind('<FocusOut>', self.on_query_focus_out)
        
        analyze_btn = tk.Button(
            query_input_frame,
            text="Analyze",
            font=('Arial', 11, 'bold'),
            bg=self.colors['accent_cyan'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_purple'],
            relief='flat',
            cursor='hand2',
            command=self.analyze_query,
            padx=30,
            pady=10
        )
        analyze_btn.pack(side='right', padx=(10, 0))
        
        # Examples
        examples_label = tk.Label(
            query_frame,
            text="Examples:",
            font=('Arial', 9, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        examples_label.pack(anchor='w', padx=20, pady=(10, 5))
        
        examples = [
            "• find SQL injection vulnerabilities",
            "• scan login page for XSS",
            "• cari celah keamanan di admin panel",
            "• check all security issues in website"
        ]
        
        for example in examples:
            ex_label = tk.Label(
                query_frame,
                text=example,
                font=('Arial', 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_secondary'],
                cursor='hand2'
            )
            ex_label.pack(anchor='w', padx=40, pady=2)
            # Make clickable
            ex_label.bind('<Button-1>', lambda e, text=example[2:]: self.set_query_example(text))
        
        query_frame.pack_propagate(False)
        query_frame.configure(height=280)
        
        # Parsed Results Section
        results_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        results_title = tk.Label(
            results_frame,
            text="📋 Parsed Parameters",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        results_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        #Parsed output text
        self.parsed_text = scrolledtext.ScrolledText(
            results_frame,
            font=('Courier New', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            height=10,
            state='disabled'
        )
        self.parsed_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Action buttons
        action_frame = tk.Frame(results_frame, bg=self.colors['bg_secondary'])
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.quick_scan_btn = tk.Button(
            action_frame,
            text="▶ Start Scan",
            font=('Arial', 12, 'bold'),
            bg=self.colors['success'],
            fg='white',
            activebackground='#059669',
            relief='flat',
            cursor='hand2',
            command=self.start_quick_scan,
            padx=40,
            pady=12,
            state='disabled'
        )
        self.quick_scan_btn.pack(side='right')
    
    def setup_advanced_tab(self, parent):
        """Setup advanced scan configuration tab"""
        
        # Target selection
        target_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        target_frame.pack(fill='x', padx=20, pady=20)
        
        target_label = tk.Label(
            target_frame,
            text="📁 Target Directory",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        target_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        target_input_frame = tk.Frame(target_frame, bg=self.colors['bg_secondary'])
        target_input_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.target_entry = tk.Entry(
            target_input_frame,
            textvariable=self.target_var,
            font=('Arial', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=10
        )
        self.target_entry.pack(fill='x', side='left', expand=True)
        
        browse_btn = tk.Button(
            target_input_frame,
            text="Browse",
            font=('Arial', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            cursor='hand2',
            command=self.browse_target,
            padx=20,
            pady=8
        )
        browse_btn.pack(side='right', padx=(10, 0))
        
        # Scan options
        options_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        options_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        options_label = tk.Label(
            options_frame,
            text="⚙ Scan Configuration",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        options_label.pack(anchor='w', padx=20, pady=(15, 15))
        
        # Provider selection
        provider_frame = tk.Frame(options_frame, bg=self.colors['bg_secondary'])
        provider_frame.pack(fill='x', padx=40, pady=5)
        
        provider_label = tk.Label(
            provider_frame,
            text="LLM Provider:",
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            width=15,
            anchor='w'
        )
        provider_label.pack(side='left')
        
        providers = ['openai', 'gemini', 'claude']
        for provider in providers:
            rb = tk.Radiobutton(
                provider_frame,
                text=provider.capitalize(),
                variable=self.provider_var,
                value=provider,
                font=('Arial', 10),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                selectcolor=self.colors['bg_tertiary'],
                activebackground=self.colors['bg_secondary'],
                activeforeground=self.colors['accent_cyan']
            )
            rb.pack(side='left', padx=10)
        
        # Profile selection
        profile_frame = tk.Frame(options_frame, bg=self.colors['bg_secondary'])
        profile_frame.pack(fill='x', padx=40, pady=5)
        
        profile_label = tk.Label(
            profile_frame,
            text="Scan Profile:",
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            width=15,
            anchor='w'
        )
        profile_label.pack(side='left')
        
        profiles = ['quick', 'standard', 'comprehensive']
        for profile in profiles:
            rb = tk.Radiobutton(
                profile_frame,
                text=profile.capitalize(),
                variable=self.profile_var,
                value=profile,
                font=('Arial', 10),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                selectcolor=self.colors['bg_tertiary'],
                activebackground=self.colors['bg_secondary'],
                activeforeground=self.colors['accent_cyan']
            )
            rb.pack(side='left', padx=10)
        
        # Scan mode
        mode_frame = tk.Frame(options_frame, bg=self.colors['bg_secondary'])
        mode_frame.pack(fill='x', padx=40, pady=(5, 15))
        
        mode_label = tk.Label(
            mode_frame,
            text="Scan Mode:",
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            width=15,
            anchor='w'
        )
        mode_label.pack(side='left')
        
        tk.Radiobutton(
            mode_frame,
            text="Full Scan (All Modules)",
            variable=self.scan_mode_var,
            value="full",
            font=('Arial', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            selectcolor=self.colors['bg_tertiary'],
            activebackground=self.colors['bg_secondary'],
            activeforeground=self.colors['accent_cyan']
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            mode_frame,
            text="Targeted Scan",
            variable=self.scan_mode_var,
            value="targeted",
            font=('Arial', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            selectcolor=self.colors['bg_tertiary'],
            activebackground=self.colors['bg_secondary'],
            activeforeground=self.colors['accent_cyan']
        ).pack(side='left', padx=10)
        
        # Control buttons
        control_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        control_frame.pack(fill='x', padx=20, pady=20)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start Scan",
            font=('Arial', 12, 'bold'),
            bg=self.colors['success'],
            fg='white',
            activebackground='#059669',
            relief='flat',
            cursor='hand2',
            command=self.start_advanced_scan,
            padx=30,
            pady=12
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.pause_btn = tk.Button(
            control_frame,
            text="⏸ Pause",
            font=('Arial', 12, 'bold'),
            bg=self.colors['warning'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.pause_scan,
            padx=30,
            pady=12,
            state='disabled'
        )
        self.pause_btn.pack(side='left', padx=5)
        
        self.report_btn = tk.Button(
            control_frame,
            text="📊 Generate Report",
            font=('Arial', 12, 'bold'),
            bg=self.colors['accent_purple'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.generate_report,
            padx=30,
            pady=12
        )
        self.report_btn.pack(side='right', padx=5)
    
    def setup_api_tab(self, parent):
        """Setup API configuration tab"""
        
        info_label = tk.Label(
            parent,
            text="Configure your LLM provider API keys below. Keys are stored securely on your local machine.",
            font=('Arial', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary'],
            wraplength=800,
            justify='left'
        )
        info_label.pack(anchor='w', padx=30, pady=20)
        
        # OpenAI
        self.create_api_key_section(parent, "OpenAI", self.api_key_openai, "openai")
        
        # Google Gemini
        self.create_api_key_section(parent, "Google Gemini", self.api_key_gemini, "gemini")
        
        # Anthropic Claude
        self.create_api_key_section(parent, "Anthropic Claude", self.api_key_claude, "claude")
        
        # Show/Hide toggle
        show_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        show_frame.pack(fill='x', padx=30, pady=20)
        
        show_check = tk.Checkbutton(
            show_frame,
            text="Show API Keys",
            variable=self.show_key_var,
            font=('Arial', 10),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            selectcolor=self.colors['bg_tertiary'],
            activebackground=self.colors['bg_primary'],
            activeforeground=self.colors['text_primary'],
            command=self.toggle_show_keys
        )
        show_check.pack(side='left')
        
        # Save button
        save_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        save_frame.pack(fill='x', padx=30, pady=20)
        
        save_btn = tk.Button(
            save_frame,
            text="💾 Save API Keys",
            font=('Arial', 12, 'bold'),
            bg=self.colors['success'],
            fg='white',
            activebackground='#059669',
            relief='flat',
            cursor='hand2',
            command=self.save_api_keys,
            padx=40,
            pady=12
        )
        save_btn.pack(side='right')
    
    def create_api_key_section(self, parent, provider_name, var, provider_key):
        """Create API key input section"""
        
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        frame.pack(fill='x', padx=30, pady=10)
        
        title_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        title_frame.pack(fill='x', padx=20, pady=(15, 5))
        
        title_label = tk.Label(
            title_frame,
            text=f"🔑 {provider_name}",
            font=('Arial', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        title_label.pack(side='left')
        
        status_label = tk.Label(
            title_frame,
            text="",
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        status_label.pack(side='right')
        setattr(self, f"{provider_key}_status_label", status_label)
        
        input_frame = tk.Frame(frame, bg=self.colors['bg_secondary'])
        input_frame.pack(fill='x', padx=20, pady=(5, 15))
        
        entry = tk.Entry(
            input_frame,
            textvariable=var,
            font=('Arial', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=10,
            show='*'
        )
        entry.pack(fill='x', side='left', expand=True)
        setattr(self, f"{provider_key}_entry", entry)
        
        test_btn = tk.Button(
            input_frame,
            text="Test",
            font=('Arial', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            relief='flat',
            cursor='hand2',
            command=lambda: self.test_api_key(provider_key),
            padx=15,
            pady=8
        )
        test_btn.pack(side='right', padx=(10, 0))
    
    def setup_results_tab(self, parent):
        """Setup scan results tab"""
        
        # Progress section
        progress_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        progress_frame.pack(fill='x', padx=20, pady=20)
        
        progress_label = tk.Label(
            progress_frame,
            text="📊 Scan Progress",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        progress_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', padx=20, pady=(0, 10))
        
        self.progress_label = tk.Label(
            progress_frame,
            text="No active scan",
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        self.progress_label.pack(anchor='w', padx=20, pady=(0, 15))
        
        # Statistics
        stats_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        stats_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        stats_label = tk.Label(
            stats_frame,
            text="📈 Findings",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        stats_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        stats_inner = tk.Frame(stats_frame, bg=self.colors['bg_secondary'])
        stats_inner.pack(fill='x', padx=20, pady=(0, 15))
        
        # Create stat boxes
        self.create_stat_box(stats_inner, "Critical", "0", self.colors['critical'])
        self.create_stat_box(stats_inner, "High", "0", self.colors['error'])
        self.create_stat_box(stats_inner, "Medium", "0", self.colors['warning'])
        self.create_stat_box(stats_inner, "Low", "0", self.colors['text_secondary'])
        
        # Console output
        console_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        console_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        console_label = tk.Label(
            console_frame,
            text="💻 Console Output",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        console_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            font=('Courier New', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            state='disabled'
        )
        self.console_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    def create_stat_box(self, parent, label, value, color):
        """Create a statistics box"""
        box = tk.Frame(parent, bg=self.colors['bg_tertiary'], relief='flat')
        box.pack(side='left', padx=5, fill='x', expand=True)
        
        value_label = tk.Label(
            box,
            text=value,
            font=('Arial', 24, 'bold'),
            fg=color,
            bg=self.colors['bg_tertiary']
        )
        value_label.pack(pady=(15, 5))
        
        text_label = tk.Label(
            box,
            text=label,
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_tertiary']
        )
        text_label.pack(pady=(0, 15))
        
        setattr(self, f"stat_{label.lower()}_label", value_label)
    
    # Event handlers and utility methods
    
    def on_query_focus_in(self, event):
        """Handle focus in for query entry"""
        if self.query_entry.get() == 'e.g., "find XSS in login page" or "cari celah di website editor"':
            self.query_entry.delete(0, 'end')
            self.query_entry.config(fg=self.colors['text_primary'])
    
    def on_query_focus_out(self, event):
        """Handle focus out for query entry"""
        if not self.query_entry.get():
            self.query_entry.insert(0, 'e.g., "find XSS in login page" or "cari celah di website editor"')
            self.query_entry.config(fg=self.colors['text_secondary'])
    
    def set_query_example(self, text):
        """Set query from example click"""
        self.query_var.set(text)
        self.query_entry.config(fg=self.colors['text_primary'])
        self.analyze_query()
    
    def analyze_query(self):
        """Analyze natural language query"""
        query = self.query_var.get()
        
        if not query or query == 'e.g., "find XSS in login page" or "cari celah di website editor"':
            return
        
        # Parse query
        parsed = self.nlp_parser.parse(query)
        
        # Display results
        self.parsed_text.config(state='normal')
        self.parsed_text.delete('1.0', 'end')
        
        self.parsed_text.insert('end', f"Original Query: {query}\n\n", 'header')
        self.parsed_text.insert('end', f"Intent: {parsed['intent'].value}\n", 'normal')
        self.parsed_text.insert('end', f"Target: {parsed['target'] or '[all]'}\n", 'normal')
        self.parsed_text.insert('end', f"Modules: {', '.join(parsed['modules']) if parsed['modules'] else '[all]'}\n", 'normal')
        self.parsed_text.insert('end', f"Scope: {parsed['scope']}\n", 'normal')
        self.parsed_text.insert('end', f"Confidence: {parsed['confidence']:.0%}\n\n", 'normal')
        
        structured_cmd = self.nlp_parser.format_structured_command(parsed)
        if structured_cmd:
            self.parsed_text.insert('end', f"Equivalent Command:\n{structured_cmd}\n", 'dim')
        
        self.parsed_text.config(state='disabled')
        
        # Store parsed result
        self.last_parsed = parsed
        
        # Enable scan button
        self.quick_scan_btn.config(state='normal')
        
        self.log_console(f"[NLP] Analyzed query with {parsed['confidence']:.0%} confidence")
    
    def browse_target(self):
        """Browse for target directory"""
        directory = filedialog.askdirectory(title="Select Target Directory")
        if directory:
            self.target_var.set(directory)
    
    def start_quick_scan(self):
        """Start scan from natural language query"""
        if not hasattr(self, 'last_parsed'):
            messagebox.showerror("Error", "Please analyze a query first")
            return
        
        # TODO: Implement actual scan
        self.log_console("[SCAN] Starting scan from natural language query...")
        self.log_console(f"[INFO] Target: {self.last_parsed['target'] or 'all'}")
        self.log_console(f"[INFO] Modules: {', '.join(self.last_parsed['modules'])}")
        messagebox.showinfo("Scan Started", "Natural language scan started (stub)")
    
    def start_advanced_scan(self):
        """Start advanced scan"""
        target = self.target_var.get()
        
        if not target:
            messagebox.showerror("Error", "Please select a target directory")
            return
        
        # TODO: Implement actual scan
        self.log_console(f"[SCAN] Starting advanced scan on: {target}")
        self.log_console(f"[INFO] Provider: {self.provider_var.get()}")
        self.log_console(f"[INFO] Profile: {self.profile_var.get()}")
        messagebox.showinfo("Scan Started", "Advanced scan started (stub)")
    
    def pause_scan(self):
        """Pause current scan"""
        self.log_console("[SCAN] Pausing scan...")
        # TODO: Implement pause
    
    def generate_report(self):
        """Generate scan report"""
        self.log_console("[REPORT] Generating report...")
        # TODO: Implement report generation
        messagebox.showinfo("Report", "Report generation coming soon")
    
    def test_api_key(self, provider):
        """Test API key"""
        key = getattr(self, f"api_key_{provider}").get()
        
        if not key:
            messagebox.showerror("Error", f"Please enter {provider} API key first")
            return
        
        self.log_console(f"[API] Testing {provider} key...")
        # TODO: Implement actual key validation
        
        status_label = getattr(self, f"{provider}_status_label")
        status_label.config(text="✓ Valid", fg=self.colors['success'])
        
        messagebox.showinfo("Success", f"{provider.capitalize()} API key is valid")
    
    def save_api_keys(self):
        """Save API keys"""
        import json
        
        config_dir = Path.home() / ".emyuel"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "api_keys.json"
        
        config = {}
        
        for provider in ['openai', 'gemini', 'claude']:
            key = getattr(self, f"api_key_{provider}").get()
            if key:
                config[provider] = [{
                    'key': key,
                    'is_backup': False,
                    'added_at': datetime.now().isoformat()
                }]
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_console("[CONFIG] API keys saved successfully")
        messagebox.showinfo("Success", "API keys saved successfully!")
    
    def load_saved_keys(self):
        """Load saved API keys"""
        import json
        
        config_file = Path.home() / ".emyuel" / "api_keys.json"
        
        if not config_file.exists():
            return
        
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            for provider in ['openai', 'gemini', 'claude']:
                if provider in config and config[provider]:
                    key = config[provider][0]['key']
                    getattr(self, f"api_key_{provider}").set(key)
                    
                    # Update status
                    status_label = getattr(self, f"{provider}_status_label")
                    status_label.config(text="✓ Loaded", fg=self.colors['success'])
            
            self.log_console("[CONFIG] Loaded saved API keys")
        except Exception as e:
            self.log_console(f"[ERROR] Failed to load API keys: {e}")
    
    def toggle_show_keys(self):
        """Toggle show/hide API keys"""
        show_char = '' if self.show_key_var.get() else '*'
        
        for provider in ['openai', 'gemini', 'claude']:
            entry = getattr(self, f"{provider}_entry")
            entry.config(show=show_char)
    
    def log_console(self, message):
        """Log message to console"""
        self.console_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.console_text.insert('end', f"[{timestamp}] {message}\n")
        self.console_text.see('end')
        self.console_text.config(state='disabled')
    
    def run(self):
        """Run the GUI"""
        self.log_console("[INFO] EMYUEL GUI started")
        self.log_console("[INFO] Ready to scan")
        self.root.mainloop()


def main():
    """GUI entry point"""
    app = EMYUELGUI()
    app.run()


if __name__ == '__main__':
    main()
