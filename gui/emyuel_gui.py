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
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.api_key_manager import APIKeyManager, RecoveryMode
from libs.scanner_state import StateManager
from libs.nlp_parser import NLPParser


class GradientButton(tk.Canvas):
    """Premium gradient button with hover effects"""
    def __init__(self, parent, text="", command=None, width=120, height=40, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bd=0, **kwargs)
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.is_hovered = False
        
        # Colors
        self.gradient_start = kwargs.get('gradient_start', '#00d9ff')
        self.gradient_end = kwargs.get('gradient_end', '#a855f7')
        self.text_color = kwargs.get('fg', '#ffffff')
        self.bg_color = kwargs.get('bg', '#1a1d2e')
        
        self.draw()
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def draw(self, hover=False):
        self.delete("all")
        self.configure(bg=self.bg_color)
        
        # Draw rounded rectangle with gradient effect
        radius = 8
        x1, y1 = 2, 2
        x2, y2 = self.width - 2, self.height - 2
        
        if hover:
            # Glow effect on hover
            self.create_oval(0, 0, self.width, self.height,
                           fill='', outline=self.gradient_start, width=2)
        
        # Gradient background (simulated with overlapping rectangles)
        self.create_rectangle(x1, y1, x2, y2, fill=self.gradient_start, 
                            outline='', tags='bg')
        
        # Text
        self.create_text(self.width/2, self.height/2, text=self.text,
                        fill=self.text_color, font=('Segoe UI', 10, 'bold'),
                        tags='text')
    
    def on_enter(self, e):
        self.is_hovered = True
        self.draw(hover=True)
    
    def on_leave(self, e):
        self.is_hovered = False
        self.draw(hover=False)
    
    def on_click(self, e):
        if self.command:
            self.command()


class ModernButton(tk.Button):
    """Enhanced button with modern styling"""
    def __init__(self, parent, **kwargs):
        # Set default modern styling
        defaults = {
            'font': ('Segoe UI', 10, 'bold'),
            'bd': 0,
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 20,
            'pady': 12
        }
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        
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
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set initial size to 80% of screen
        initial_width = int(screen_width * 0.8)
        initial_height = int(screen_height * 0.8)
        
        # Center window
        x = (screen_width - initial_width) // 2
        y = (screen_height - initial_height) // 2
        
        self.root.geometry(f"{initial_width}x{initial_height}+{x}+{y}")
        self.root.minsize(900, 650)
        
        # Enable fullscreen toggle with F11
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.is_fullscreen = False
        
        # Enhanced color scheme - Premium cyber security theme
        self.colors = {
            'bg_primary': '#0f1117',      # Darker main background
            'bg_secondary': '#1a1d2e',    # Card backgrounds
            'bg_tertiary': '#252837',     # Elevated elements
            'bg_hover': '#2d3142',        # Hover states
            'accent_cyan': '#00d9ff',     # Primary accent
            'accent_purple': '#a855f7',   # Secondary accent
            'accent_pink': '#ec4899',     # Tertiary accent
            'accent_gold': '#fbbf24',     # Premium/warning
            'text_primary': '#f9fafb',    # Bright white
            'text_secondary': '#9ca3af',  # Muted gray
            'text_tertiary': '#6b7280',   # Very muted
            'success': '#10b981',         # Green
            'warning': '#f59e0b',         # Orange
            'error': '#ef4444',           # Red
            'critical': '#dc2626',        # Dark red
            'border': '#374151',          # Subtle borders
            'shadow': '#000000'           # Shadows
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Initialize components
        self.key_manager = APIKeyManager(recovery_mode=RecoveryMode.GUI)
        self.state_manager = StateManager()
        self.nlp_parser = NLPParser()  # For natural language query parsing
        
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
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame container"""
        # Create canvas
        canvas = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        # Configure scroll region
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame, canvas
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Enhanced header with premium design
        header_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=90)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Icon + Title container
        title_container = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        title_container.pack(side='left', padx=32, pady=24)
        
        # Security shield icon
        icon_label = tk.Label(
            title_container,
            text="🛡️",
            font=('Segoe UI Emoji', 32),
            bg=self.colors['bg_secondary']
        )
        icon_label.pack(side='left', padx=(0, 12))
        
        # Title section
        title_section = tk.Frame(title_container, bg=self.colors['bg_secondary'])
        title_section.pack(side='left')
        
        title_label = tk.Label(
            title_section,
            text="EMYUEL",
            font=('Segoe UI', 32, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_secondary']
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_section,
            text="Enterprise AI Security Scanner",
            font=('Segoe UI', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        subtitle_label.pack(anchor='w')
        
        # Status indicator (top right)
        status_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        status_frame.pack(side='right', padx=32, pady=24)
        
        status_dot = tk.Label(
            status_frame,
            text="●",
            font=('Segoe UI', 16),
            fg=self.colors['success'],
            bg=self.colors['bg_secondary']
        )
        status_dot.pack(side='left', padx=(0, 8))
        
        status_text = tk.Label(
            status_frame,
            text="Ready",
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        status_text.pack(side='left')
        self.header_status_label = status_text
        self.header_status_dot = status_dot
        
        # Main container with improved spacing
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=24, pady=16)
        
        # Create notebook for tabs with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_primary'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       padding=[24, 12],
                       font=('Segoe UI', 10, 'bold'))
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
        
        # Tab 3: AI Analysis (NEW)
        ai_analysis_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(ai_analysis_frame, text='  🤖  AI Analysis  ')
        self.setup_ai_analysis_tab(ai_analysis_frame)
        
        # Tab 4: API Configuration
        api_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(api_frame, text='API Keys')
        self.setup_api_tab(api_frame)
        
        # Tab 5: Scan Results
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
        """Setup quick scan tab with website URL input and natural language query"""
        
        # Create scrollable container
        scrollable_frame, canvas = self.create_scrollable_frame(parent)
        
        # Website URL Section (NEW - Priority #1)
        url_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        url_frame.pack(fill='x', padx=20, pady=20)
        
        url_title = tk.Label(
            url_frame,
            text="🌐 Website URL Scanner",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        url_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        url_subtitle = tk.Label(
            url_frame,
            text="Enter a website URL to scan for security vulnerabilities",
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        url_subtitle.pack(anchor='w', padx=20, pady=(0, 15))
        
        # URL input with scan button
        url_input_frame = tk.Frame(url_frame, bg=self.colors['bg_secondary'])
        url_input_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.url_entry = tk.Entry(
            url_input_frame,
            textvariable=self.target_var,
            font=('Segoe UI', 12),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_cyan'],
            relief='flat',
            bd=12
        )
        self.url_entry.pack(fill='x', side='left', expand=True)
        self.url_entry.bind('<Return>', lambda e: self.quick_scan_url())
        
        # Placeholder
        self.url_entry.insert(0, 'https://example.com')
        self.url_entry.config(fg=self.colors['text_secondary'])
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        
        # Quick Scan button
        quick_scan_btn = tk.Button(
            url_input_frame,
            text="⚡ Quick Scan",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent_cyan'],
            fg=self.colors['bg_primary'],
            activebackground=self.colors['accent_purple'],
            relief='flat',
            cursor='hand2',
            command=self.quick_scan_url,
            padx=30,
            pady=12
        )
        quick_scan_btn.pack(side='right', padx=(10, 0))
        
        # URL Examples
        url_examples_label = tk.Label(
            url_frame,
            text="Quick Examples:",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        url_examples_label.pack(anchor='w', padx=20, pady=(10, 5))
        
        url_examples = [
            "https://example.com",
            "https://testphp.vulnweb.com",
            "http://demo.testfire.net"
        ]
        
        url_ex_container = tk.Frame(url_frame, bg=self.colors['bg_secondary'])
        url_ex_container.pack(anchor='w', padx=40, pady=(0, 15))
        
        for url_example in url_examples:
            ex_btn = tk.Label(
                url_ex_container,
                text=f"🔗 {url_example}",
                font=('Segoe UI', 9),
                fg=self.colors['accent_cyan'],
                bg=self.colors['bg_secondary'],
                cursor='hand2'
            )
            ex_btn.pack(side='left', padx=(0, 15))
            ex_btn.bind('<Button-1>', lambda e, url=url_example: self.set_url_example(url))
        
        # Vulnerability Selection Section
        vuln_selection_label = tk.Label(
            url_frame,
            text="Select Vulnerabilities to Scan:",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        vuln_selection_label.pack(anchor='w', padx=20, pady=(15, 8))
        
        # Checkbox container
        checkbox_container = tk.Frame(url_frame, bg=self.colors['bg_secondary'])
        checkbox_container.pack(anchor='w', padx=40, pady=(0, 15))
        
        # Create checkboxes for vulnerability types
        self.vuln_vars = {}
        vulnerabilities = [
            ('xss', 'XSS (Cross-Site Scripting)', True),
            ('sqli', 'SQL Injection', True),
            ('csrf', 'CSRF', True),
            ('headers', 'Security Headers', True),
            ('brute_force', '🔓 Brute Force (Auth Testing)', False),
            ('ssl', 'SSL/TLS Issues', False),
            ('info_disclosure', 'Information Disclosure', True),
            ('all', 'Scan All', False)
        ]
        
        # Create 2 columns of checkboxes
        col1 = tk.Frame(checkbox_container, bg=self.colors['bg_secondary'])
        col1.pack(side='left', padx=(0, 30))
        
        col2 = tk.Frame(checkbox_container, bg=self.colors['bg_secondary'])
        col2.pack(side='left')
        
        for i, (vuln_id, vuln_label, default) in enumerate(vulnerabilities):
            var = tk.BooleanVar(value=default)
            self.vuln_vars[vuln_id] = var
            
            container = col1 if i < 4 else col2
            
            cb = tk.Checkbutton(
                container,
                text=vuln_label,
                variable=var,
                font=('Segoe UI', 9),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'],
                selectcolor=self.colors['bg_tertiary'],
                activebackground=self.colors['bg_secondary'],
                activeforeground=self.colors['accent_cyan'],
                cursor='hand2',
                command=lambda vid=vuln_id: self.on_vuln_checkbox_change(vid)
            )
            cb.pack(anchor='w', pady=2)
        
        url_frame.pack_propagate(False)
        url_frame.configure(height=320)
        
        # Divider
        divider = tk.Frame(parent, bg=self.colors['border'], height=1)
        divider.pack(fill='x', padx=40, pady=10)
        
        # Natural Language Query Section (ALTERNATIVE METHOD)
        query_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        query_frame.pack(fill='x', padx=20, pady=20)
        
        query_title = tk.Label(
            query_frame,
            text="🔍 Natural Language Query (Alternative)",
            font=('Segoe UI', 13, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        query_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        query_subtitle = tk.Label(
            query_frame,
            text="Or describe what you want to scan in plain English or Indonesian",
            font=('Segoe UI', 9),
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
        
        # Create scrollable container
        scrollable_frame, canvas = self.create_scrollable_frame(parent)
        
        # Target selection
        target_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        target_frame.pack(fill='x', padx=20, pady=20)
        
        target_label = tk.Label(
            target_frame,
            text="🎯 Scan Target",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        )
        target_label.pack(anchor='w', padx=20, pady=(15, 5))
        
        target_hint = tk.Label(
            target_frame,
            text="Enter URL (https://...) or local directory path",
            font=('Arial', 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        target_hint.pack(anchor='w', padx=20, pady=(0, 10))
        
        target_input_frame = tk.Frame(target_frame, bg=self.colors['bg_secondary'])
        target_input_frame.pack(fill='x', padx=20, pady=(0, 10))
        
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
        
        # Add placeholder
        self.target_entry.insert(0, "https://example.com or /path/to/directory")
        self.target_entry.config(fg=self.colors['text_secondary'])
        self.target_entry.bind('<FocusIn>', self.on_target_focus_in)
        self.target_entry.bind('<FocusOut>', self.on_target_focus_out)
        
        browse_btn = tk.Button(
            target_input_frame,
            text="📁 Browse",
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
        
        # Quick actions
        quick_actions_frame = tk.Frame(target_frame, bg=self.colors['bg_secondary'])
        quick_actions_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        scan_all_btn = tk.Button(
            quick_actions_frame,
            text="🌐 Scan All (Full Website/Directory)",
            font=('Arial', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['accent_cyan'],
            relief='flat',
            cursor='hand2',
            command=self.set_scan_all_mode,
            padx=15,
            pady=8
        )
        scan_all_btn.pack(side='left', padx=(0, 10))
        
        self.target_type_label = tk.Label(
            quick_actions_frame,
            text="",
            font=('Arial', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        self.target_type_label.pack(side='left', padx=10)
        
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
        
        # Create scrollable container
        scrollable_frame, canvas = self.create_scrollable_frame(parent)
        
        info_label = tk.Label(
            scrollable_frame,
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
        
        # Create scrollable container
        scrollable_frame, canvas = self.create_scrollable_frame(parent)
        
        # Progress section
        progress_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
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
    
    def on_target_focus_in(self, event):
        """Handle focus in for target entry"""
        if self.target_entry.get() == "https://example.com or /path/to/directory":
            self.target_entry.delete(0, 'end')
            self.target_entry.config(fg=self.colors['text_primary'])
    
    def on_target_focus_out(self, event):
        """Handle focus out for target entry"""
        target = self.target_entry.get()
        if not target:
            self.target_entry.insert(0, "https://example.com or /path/to/directory")
            self.target_entry.config(fg=self.colors['text_secondary'])
        else:
            # Detect target type
            self.detect_target_type(target)
    
    def detect_target_type(self, target):
        """Detect if target is URL or directory"""
        if target.startswith(('http://', 'https://')):
            self.target_type_label.config(
                text="🌐 Web Target",
                fg=self.colors['accent_cyan']
            )
            self.log_console(f"[INFO] Detected web target: {target}")
        elif target and target != "https://example.com or /path/to/directory":
            self.target_type_label.config(
                text="📁 Local Directory",
                fg=self.colors['success']
            )
            self.log_console(f"[INFO] Detected local directory: {target}")
        else:
            self.target_type_label.config(text="")
    
    def on_url_focus_in(self, event):
        """Handle URL entry focus in"""
        if self.url_entry.get() == 'https://example.com':
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg=self.colors['text_primary'])
    
    def on_url_focus_out(self, event):
        """Handle URL entry focus out"""
        if not self.url_entry.get():
            self.url_entry.insert(0, 'https://example.com')
            self.url_entry.config(fg=self.colors['text_secondary'])
    
    def set_url_example(self, url):
        """Set URL from example click"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.url_entry.config(fg=self.colors['text_primary'])
        self.target_var.set(url)
        self.log_console(f"[INFO] URL set to: {url}")
    
    def on_vuln_checkbox_change(self, vuln_id):
        """Handle vulnerability checkbox changes"""
        if vuln_id == 'all':
            # If 'Scan All' is checked, check all others
            scan_all = self.vuln_vars['all'].get()
            for vid in self.vuln_vars:
                if vid != 'all':
                    self.vuln_vars[vid].set(scan_all)
        else:
            # If any specific vuln is unchecked, uncheck 'Scan All'
            if not self.vuln_vars[vuln_id].get():
                self.vuln_vars['all'].set(False)
    
    def get_selected_vulnerabilities(self):
        """Get list of selected vulnerability modules"""
        selected = []
        for vuln_id, var in self.vuln_vars.items():
            if var.get() and vuln_id != 'all':
                selected.append(vuln_id)
        
        # If none selected or all selected, return 'all'
        if not selected or len(selected) == len(self.vuln_vars) - 1:
            return ['all']
        
        return selected
    
    def quick_scan_url(self):
        """Quick scan a website URL directly"""
        url = self.target_var.get().strip()
        
        # Clear placeholder
        if url == 'https://example.com' or not url:
            self.log_console("[ERROR] Please enter a valid website URL")
            messagebox.showwarning("Invalid URL", "Please enter a valid website URL to scan")
            return
        
        # Validate and fix URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.target_var.set(url)
        
        # Get selected vulnerabilities
        modules = self.get_selected_vulnerabilities()
        modules_str = ', '.join(modules) if len(modules) < 6 else f"{len(modules)} modules"
        
        self.log_console(f"[INFO] 🚀 Starting quick scan...")
        self.log_console(f"[INFO] Target: {url}")
        self.log_console(f"[INFO] Profile: standard")
        self.log_console(f"[INFO] Modules: {modules_str}")
        
        # Update header status
        if hasattr(self, 'header_status_label'):
            self.header_status_label.config(text="Scanning...")
            self.header_status_dot.config(fg=self.colors['warning'])
        
        # Execute real scan with selected modules
        self._execute_real_scan(url, modules=modules)
    
    def set_scan_all_mode(self):
        """Set scan to 'scan all' mode"""
        self.scan_mode_var.set("full")
        self.log_console("[MODE] Set to FULL SCAN (All Modules)")
        
        # Highlight mode change
        self.status_label.config(
            text="Mode: Full Scan (All Vulnerabilities)",
            fg=self.colors['accent_cyan']
        )
        
        messagebox.showinfo(
            "Scan All Mode",
            "Full scan mode activated!\n\nWill scan for ALL vulnerability types:\n" +
            "• SQL Injection\n• XSS\n• SSRF\n• RCE\n• CSRF\n" +
            "• Path Traversal\n• Auth Issues\n• And more..."
        )
    
    def browse_target(self):
        """Browse for target directory"""
        directory = filedialog.askdirectory(title="Select Target Directory")
        if directory:
            self.target_var.set(directory)
            self.target_entry.config(fg=self.colors['text_primary'])
            self.detect_target_type(directory)
    
    def start_quick_scan(self):
        """Start scan from natural language query"""
        if not hasattr(self, 'last_parsed'):
            messagebox.showerror("Error", "Please analyze a query first")
            return
        
        # Get target from parsed query or use default
        target = self.last_parsed.get('target') or self.target_var.get()
        
        if not target or target == "https://example.com or /path/to/directory":
            messagebox.showerror("Error", "Please specify a target to scan")
            return
        
        self.log_console("[SCAN] Starting scan from natural language query...")
        self.log_console(f"[INFO] Target: {target}")
        self.log_console(f"[INFO] Modules: {', '.join(self.last_parsed['modules'])}")
        
        # Start real scan
        self._execute_real_scan(target, self.last_parsed.get('modules'))
    
    def start_advanced_scan(self):
        """Start advanced scan"""
        target = self.target_var.get()
        
        if not target or target == "https://example.com or /path/to/directory":
            messagebox.showerror("Error", "Please enter a target URL or select a directory")
            return
        
        # Detect target type
        is_url = target.startswith(('http://', 'https://'))
        target_type = "Web" if is_url else "Local"
        
        # Get scan mode
        scan_mode = self.scan_mode_var.get()
        modules = None if scan_mode == "full" else []  # None = all modules
        
        # Log scan details
        mode_text = "Full Scan (All Modules)" if scan_mode == "full" else "Targeted Scan"
        self.log_console(f"[SCAN] Starting {mode_text} on {target_type} target")
        self.log_console(f"[TARGET] {target}")
        self.log_console(f"[INFO] Provider: {self.provider_var.get()}")
        self.log_console(f"[INFO] Profile: {self.profile_var.get()}")
        
        self.status_label.config(
            text=f"Scanning: {target}",
            fg=self.colors['accent_cyan']
        )
        
        # Start real scan
        self._execute_real_scan(target, modules)
    
    def _execute_real_scan(self, target: str, modules: Optional[List[str]] = None):
        """Execute real scan in background thread"""
        import threading
        
        def run_scan():
            try:
                import asyncio
                import sys
                from pathlib import Path
                
                # Ensure parent directory is in path
                parent_dir = Path(__file__).parent.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                
                # Import scanner
                try:
                    from services.scanner_core import ScannerCore
                except ImportError as e:
                    err_msg = str(e)  # Capture value immediately
                    self.root.after(0, lambda msg=err_msg: self.log_console(f"[ERROR] Failed to import ScannerCore: {msg}"))
                    self.root.after(0, lambda: self.log_console("[ERROR] Make sure scanner-core directory exists in services/"))
                    self.root.after(0, lambda msg=err_msg: messagebox.showerror(
                        "Import Error", 
                        f"Failed to import scanner:\n{msg}\n\nMake sure services/scanner-core/ directory exists."
                    ))
                    return
                
                # Import API key manager
                scanner_core_dir = parent_dir / "services" / "scanner-core"
                if str(scanner_core_dir) not in sys.path:
                    sys.path.insert(0, str(scanner_core_dir))
                
                from api_key_manager import APIKeyManager
                
                # Get API keys
                api_key_manager = APIKeyManager()
                
                # Configure scanner
                config = {
                    'api_key_manager': api_key_manager,
                    'provider': self.provider_var.get(),
                    'profile': self.profile_var.get()
                }
                
                # Create scanner
                scanner = ScannerCore(config)
                
                # Run scan
                scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Run async scan
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.root.after(0, lambda: self.log_console("[SCAN] Initializing scanner..."))
                self.root.after(0, lambda: self.progress_var.set(5))
                
                results = loop.run_until_complete(
                    scanner.scan(
                        target=target,
                        modules=modules,
                        scan_id=scan_id
                    )
                )
                
                loop.close()
                
                # Update UI with results
                self.root.after(0, lambda: self._display_scan_results(results))
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                error_trace = traceback.format_exc()
                self.root.after(0, lambda msg=error_msg: self.log_console(f"[ERROR] Scan failed: {msg}"))
                self.root.after(0, lambda trace=error_trace: self.log_console(f"[ERROR] Traceback:\n{trace}"))
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Scan Error", f"Scan failed:\n\n{msg}"))
                self.root.after(0, lambda: self.status_label.config(text="Scan failed", fg=self.colors['error']))
        
        # Start scan thread
        scan_thread = threading.Thread(target=run_scan, daemon=True)
        scan_thread.start()
        
        # Show progress
        self.progress_var.set(10)
        self.progress_label.config(text="Scan in progress...")
    
    def _display_scan_results(self, results: Dict[str, Any]):
        """Display scan results in UI"""
        # Update progress
        self.progress_var.set(100)
        self.progress_label.config(text="Scan completed")
        
        # Update status
        total_findings = results.get('total_findings', 0)
        self.status_label.config(
            text=f"Scan complete: {total_findings} vulnerabilities found",
            fg=self.colors['success'] if total_findings == 0 else self.colors['warning']
        )
        
        # Update severity stats
        by_severity = results.get('findings_by_severity', {})
        if hasattr(self, 'stat_critical_label'):
            self.stat_critical_label.config(text=str(by_severity.get('critical', 0)))
        if hasattr(self, 'stat_high_label'):
            self.stat_high_label.config(text=str(by_severity.get('high', 0)))
        if hasattr(self, 'stat_medium_label'):
            self.stat_medium_label.config(text=str(by_severity.get('medium', 0)))
        if hasattr(self, 'stat_low_label'):
            self.stat_low_label.config(text=str(by_severity.get('low', 0)))
        
        # Log findings
        self.log_console(f"[RESULT] Total findings: {total_findings}")
        self.log_console(f"[RESULT] Critical: {by_severity.get('critical', 0)}")
        self.log_console(f"[RESULT] High: {by_severity.get('high', 0)}")
        self.log_console(f"[RESULT] Medium: {by_severity.get('medium', 0)}")
        self.log_console(f"[RESULT] Low: {by_severity.get('low', 0)}")
        
        # Show summary dialog
        messagebox.showinfo(
            "Scan Complete",
            f"Scan finished successfully!\n\n" +
            f"Total vulnerabilities: {total_findings}\n" +
            f"Critical: {by_severity.get('critical', 0)}\n" +
            f"High: {by_severity.get('high', 0)}\n" +
            f"Medium: {by_severity.get('medium', 0)}\n" +
            f"Low: {by_severity.get('low', 0)}"
        )
    
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
        
        status_label = getattr(self, f"{provider}_status_label")
        
        # Basic validation
        try:
            # Check key format
            if provider == 'openai':
                if not key.startswith('sk-'):
                    raise ValueError("OpenAI key must start with 'sk-'")
                if len(key) < 20:
                    raise ValueError("OpenAI key too short")
            elif provider == 'gemini':
                if not key.startswith('AI'):
                    raise ValueError("Gemini key must start with 'AI'")
                if len(key) < 20:
                    raise ValueError("Gemini key too short")
            elif provider == 'claude':
                if not key.startswith('sk-ant-'):
                    raise ValueError("Claude key must start with 'sk-ant-'")
                if len(key) < 20:
                    raise ValueError("Claude key too short")
            
            # TODO: Add actual API call validation
            # For now, just format validation
            status_label.config(text="⚠ Format OK (Not tested live)", fg=self.colors['warning'])
            
            self.log_console(f"[API] {provider.capitalize()} key format is valid")
            self.log_console(f"[WARN] Live API validation not implemented yet")
            
            messagebox.showinfo(
                "Key Validation",
                f"{provider.capitalize()} key format is valid!\n\n" +
                "⚠ Note: Live API validation not implemented yet.\n" +
                "The key will be tested when you run a scan."
            )
            
        except ValueError as e:
            status_label.config(text="✗ Invalid", fg=self.colors['error'])
            self.log_console(f"[ERROR] {provider.capitalize()} key validation failed: {e}")
            messagebox.showerror("Invalid Key", f"{provider.capitalize()} API key is invalid:\n\n{str(e)}")
    
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
    
    def setup_ai_analysis_tab(self, parent):
        """Setup AI-driven autonomous security analysis tab"""
        
        # Scrollable container
        canvas = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🤖 AI-Driven Autonomous Security Analysis",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 5))
        
        tk.Label(
            header_frame,
            text="AI analyzes targets, generates custom testing strategies, and adapts based on results",
            font=('Segoe UI', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(0, 15))
        
        # Target URL Section
        url_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        url_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(
            url_frame,
            text="🎯 Target URL",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        url_input_frame = tk.Frame(url_frame, bg=self.colors['bg_secondary'])
        url_input_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.ai_target_var = tk.StringVar(value='https://testphp.vulnweb.com')
        
        url_entry = tk.Entry(
            url_input_frame,
            textvariable=self.ai_target_var,
            font=('Segoe UI', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=0
        )
        url_entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(0, 10))
        
        # Start Analysis Button
        start_btn = tk.Button(
            url_input_frame,
            text="🚀 Start AI Analysis",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent_cyan'],
            fg='#000000',
            activebackground=self.colors['accent_purple'],
            activeforeground='#ffffff',
            relief='flat',
            cursor='hand2',
            command=self.start_ai_analysis,
            padx=20,
            pady=10
        )
        start_btn.pack(side='right')
        
        # Natural Language Query Section (NEW!)
        nlp_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        nlp_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(
            nlp_frame,
            text="💬 Natural Language Query (Optional)",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 5))
        
        tk.Label(
            nlp_frame,
            text="Contoh: 'test keamanan databasenya' atau 'find SQL injection vulnerabilities'",
            font=('Segoe UI', 9, 'italic'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(0, 10))
        
        nlp_input_frame = tk.Frame(nlp_frame, bg=self.colors['bg_secondary'])
        nlp_input_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.ai_nlp_query_var = tk.StringVar()
        
        nlp_entry = tk.Entry(
            nlp_input_frame,
            textvariable=self.ai_nlp_query_var,
            font=('Segoe UI', 10),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            relief='flat',
            bd=0
        )
        nlp_entry.pack(fill='x', ipady=10)
        
        # Quick example buttons
        examples_frame = tk.Frame(nlp_frame, bg=self.colors['bg_secondary'])
        examples_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(
            examples_frame,
            text="Quick examples:",
            font=('Segoe UI', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        ).pack(side='left', padx=(0, 10))
        
        example_queries = [
            ("Database", "test keamanan databasenya"),
            ("XSS", "cari celah XSS"),
            ("Full Scan", "scan semua kerentanan")
        ]
        
        for label, query in example_queries:
            btn = tk.Button(
                examples_frame,
                text=label,
                font=('Segoe UI', 8),
                bg=self.colors['bg_tertiary'],
                fg=self.colors['text_secondary'],
                activebackground=self.colors['accent_cyan'],
                activeforeground='#000000',
                relief='flat',
                cursor='hand2',
                command=lambda q=query: self.ai_nlp_query_var.set(q),
                padx=8,
                pady=4
            )
            btn.pack(side='left', padx=2)
        
        # Progress Section
        progress_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        progress_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            progress_frame,
            text="📊 Analysis Progress",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        # Steps container with scroll
        steps_canvas = tk.Canvas(progress_frame, bg=self.colors['bg_tertiary'], height=250, highlightthickness=0)
        steps_scroll = tk.Scrollbar(progress_frame, orient="vertical", command=steps_canvas.yview)
        self.ai_steps_frame = tk.Frame(steps_canvas, bg=self.colors['bg_tertiary'])
        
        self.ai_steps_frame.bind(
            "<Configure>",
            lambda e: steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))
        )
        
        steps_canvas.create_window((0, 0), window=self.ai_steps_frame, anchor="nw", width=700)
        steps_canvas.configure(yscrollcommand=steps_scroll.set)
        
        steps_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
        steps_scroll.pack(side="right", fill="y", pady=(0, 15), padx=(0, 20))
        
        # Initial placeholder
        tk.Label(
            self.ai_steps_frame,
            text="No analysis started. Enter a URL above and click 'Start AI Analysis'",
            font=('Segoe UI', 9, 'italic'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_tertiary']
        ).pack(padx=15, pady=30)
        
        # AI Reasoning Section
        reasoning_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        reasoning_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(
            reasoning_frame,
            text="💬 AI Reasoning",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        self.ai_reasoning_text = tk.Text(
            reasoning_frame,
            height=4,
            font=('Segoe UI', 9),
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_secondary'],
            relief='flat',
            wrap='word',
            state='disabled'
        )
        self.ai_reasoning_text.pack(fill='x', padx=20, pady=(0, 15))
        
        # Live Console
        console_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat', bd=2)
        console_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(
            console_frame,
            text="📄 Live Console",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        self.ai_console_text = tk.Text(
            console_frame,
            height=8,
            font=('Consolas', 9),
            bg='#000000',
            fg='#00ff00',
            relief='flat',
            wrap='word',
            state='disabled'
        )
        self.ai_console_text.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Initialize AI analysis state
        self.ai_analysis_running = False
        self.ai_step_widgets = []
    
    def start_ai_analysis(self):
        """Start AI-driven security analysis"""
        target_url = self.ai_target_var.get().strip()
        
        if not target_url or target_url == 'https://example.com':
            messagebox.showwarning("Invalid URL", "Please enter a valid target URL")
            return
        
        if hasattr(self, 'ai_analysis_running') and self.ai_analysis_running:
            messagebox.showinfo("Analysis Running", "An AI analysis is already in progress")
            return
        
        # Validate API key
        openai_key = self.api_key_openai.get()
        if not openai_key:
            messagebox.showerror("API Key Required", 
                               "Please configure your OpenAI API key in the API Keys tab first")
            return
        
        # Parse natural language query if provided
        nlp_query = self.ai_nlp_query_var.get().strip()
        focus_modules = []
        query_context = ""
        
        if nlp_query:
            parsed = self.nlp_parser.parse(nlp_query)
            focus_modules = parsed.get('modules', [])
            query_context = f"User Request: {nlp_query}\n"
            
            if parsed.get('confidence', 0) > 0.5:
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 💬 Understood: {nlp_query}")
                if focus_modules and 'all' not in focus_modules:
                    self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Focus: {', '.join(focus_modules).upper()}")
            else:
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Query unclear, running full scan")
        
        self.ai_analysis_running = True
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] AI Analysis initialized")
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Target: {target_url}")
        
        if query_context:
            self.ai_update_reasoning(f"{query_context}\nAnalyzing request and preparing scan strategy...")
        else:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] NOTE: Full AI analysis requires integration")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Running basic security scan instead...")
        
        # Run basic scan (placeholder - full implementation available in ai_analysis_tab_methods.py)
        import threading
        thread = threading.Thread(target=self.run_basic_analysis, args=(target_url, focus_modules, query_context))
        thread.daemon = True
        thread.start()
    
    def run_basic_analysis(self, target_url: str, focus_modules: list = None, query_context: str = ""):
        """Run basic analysis (simplified version)"""
        import asyncio
        from services.executor import Executor
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            executor = Executor(verbose=False)
            
            # Determine what to scan based on NLP query
            if focus_modules and 'all' not in focus_modules:
                scan_description = f"Focusing on: {', '.join([m.upper() for m in focus_modules])}"
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] {scan_description}")
                if query_context:
                    self.ai_update_reasoning(f"{query_context}\nStrategy: Targeted scan on {', '.join(focus_modules)}")
            else:
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Running comprehensive security check...")
                self.ai_update_reasoning("Analyzing all security aspects...")
            
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] Checking security headers...")
            
            # Basic header analysis
            import aiohttp
            async def check_headers():
                async with aiohttp.ClientSession() as session:
                    async with session.get(target_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        headers = dict(response.headers)
                        return headers
            
            headers = loop.run_until_complete(check_headers())
            
            # Check for security headers
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Content-Security-Policy', 'Strict-Transport-Security']
            missing = [h for h in security_headers if h not in headers]
            
            if missing:
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Missing headers: {', '.join(missing)}")
                reasoning = f"Found {len(missing)} missing security headers.\n\n"
                reasoning += f"Missing: {', '.join(missing)}\n\n"
                reasoning += "Recommendation: Add security headers to prevent common attacks."
                if query_context:
                    reasoning = f"{query_context}\n\n{reasoning}"
                self.ai_update_reasoning(reasoning)
            else:
                self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ All security headers present")
                self.ai_update_reasoning("Security headers are properly configured.")
            
            # If focusing on specific modules, mention them
            if focus_modules and 'all' not in focus_modules:
                if 'sqli' in focus_modules or 'sql' in focus_modules:
                    self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 SQL Injection testing would run here (full AI mode)")
                if 'xss' in focus_modules:
                    self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 XSS testing would run here (full AI mode)")
            
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Analysis complete!")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] For full AI-powered analysis, see: ai_analysis_tab_methods.py")
            
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")
        
        finally:
            self.ai_analysis_running = False
            loop.close()
    
    def ai_log_console(self, message: str):
        """Log message to AI console (thread-safe)"""
        if hasattr(self, 'ai_console_text'):
            def update():
                self.ai_console_text.config(state='normal')
                self.ai_console_text.insert('end', message + '\n')
                self.ai_console_text.see('end')
                self.ai_console_text.config(state='disabled')
            
            # Execute on main thread
            self.root.after(0, update)
    
    def ai_update_reasoning(self, reasoning: str):
        """Update AI reasoning display (thread-safe)"""
        if hasattr(self, 'ai_reasoning_text'):
            def update():
                self.ai_reasoning_text.config(state='normal')
                self.ai_reasoning_text.delete('1.0', 'end')
                self.ai_reasoning_text.insert('1.0', reasoning)
                self.ai_reasoning_text.config(state='disabled')
            
            # Execute on main thread
            self.root.after(0, update)
    
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
