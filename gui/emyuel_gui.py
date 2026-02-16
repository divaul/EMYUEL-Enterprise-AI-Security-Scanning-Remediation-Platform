#!/usr/bin/env python3
"""
EMYUEL Security Scanner - GUI Application
Enterprise AI-powered vulnerability scanner with modern GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from datetime import datetime
import threading
import sys
from typing import Optional, List, Dict, Any
import asyncio
import os

# Import modular GUI components
from gui.utils.colors import get_color_scheme
from gui.components.hover_button import HoverButton
from gui.tabs import (
    setup_quick_scan_tab,
    setup_advanced_tab,
    setup_ai_analysis_tab,
    setup_api_tab,
    setup_reports_tab  # Changed from setup_results_tab
)

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
        self.colors = get_color_scheme()
        
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
        """Create a scrollable frame container with always-visible scrollbar"""
        # Create main container
        container = tk.Frame(parent, bg=self.colors['bg_primary'])
        container.pack(fill='both', expand=True)
        
        # Create canvas
        canvas = tk.Canvas(
            container, 
            bg=self.colors['bg_primary'], 
            highlightthickness=0,
            borderwidth=0
        )
        
        # Create scrollbar with custom styling - ALWAYS VISIBLE
        scrollbar = tk.Scrollbar(
            container, 
            orient="vertical", 
            command=canvas.yview,
            bg=self.colors['bg_secondary'],
            troughcolor=self.colors['bg_primary'],
            activebackground=self.colors['accent_cyan'],
            width=16,  # Ensure minimum width for visibility
            relief='flat',
            bd=0
        )
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        # Configure scroll region when frame size changes
        def _configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Force scrollbar to always show by ensuring canvas is scrollable
            canvas.update_idletasks()
        
        # Configure canvas width to match container (minus scrollbar)
        def _configure_canvas_width(event):
            # Subtract scrollbar width to prevent horizontal scrollbar
            canvas_width = max(100, event.width - 20)
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas width
        canvas.bind('<Configure>', _configure_canvas_width)
        
        # Pack scrollbar FIRST (right side) then canvas - ensures scrollbar always visible
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Mouse wheel scrolling - cross-platform support
        def _on_mousewheel(event):
            try:
                # Windows and macOS
                delta = int(-1*(event.delta/120))
                canvas.yview_scroll(delta, "units")
            except:
                try:
                    # Linux - Button 4/5
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")
                except:
                    pass
        
        # Bind mousewheel to canvas and all children
        def _bind_to_mousewheel(event):
            try:
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
                # Linux support
                canvas.bind_all("<Button-4>", _on_mousewheel)
                canvas.bind_all("<Button-5>", _on_mousewheel)
            except:
                pass
        
        def _unbind_from_mousewheel(event):
            try:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            except:
                pass
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Ensure scrollbar is visible and raised
        scrollbar.lift()
        
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
        setup_quick_scan_tab(quick_scan_frame, self)  # Using modular setup
        
        # Tab 2: Advanced Scan
        advanced_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(advanced_frame, text='Advanced Scan')
        setup_advanced_tab(advanced_frame, self)  # Using modular setup
        
        # Tab 3: AI Analysis (MODULAR)
        ai_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(ai_frame, text='AI Analysis')
        setup_ai_analysis_tab(ai_frame, self)  # Using modular setup
        
        # Tab 4: API Keys (MODULAR)
        api_keys_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(api_keys_frame, text='API Keys')
        setup_api_tab(api_keys_frame, self)  # Using modular setup
        
        # Tab 5: Reports (MODULAR) - Changed from Results
        reports_frame = tk.Frame(notebook, bg=self.colors['bg_primary'])
        notebook.add(reports_frame, text='📊 Reports')
        setup_reports_tab(reports_frame, self)  # Using modular setup
        
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
    
    # setup_quick_scan_tab and setup_advanced_tab removed - now using modular versions
    
    # setup_api_tab removed - now using modular version from gui/tabs/api_keys_tab.py
    
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
    
    # setup_results_tab removed - now using modular version from gui/tabs/results_tab.py
    
    def create_stat_box(self, parent, label, value, color, icon=""):
        """Create a statistics box with icon"""
        box = tk.Frame(parent, bg=self.colors['bg_tertiary'], relief='flat', bd=1)
        box.pack(side='left', padx=5, fill='x', expand=True)
        
        # Icon if provided
        if icon:
            icon_label = tk.Label(
                box,
                text=icon,
                font=('Segoe UI Emoji', 18),
                bg=self.colors['bg_tertiary']
            )
            icon_label.pack(pady=(10, 0))
        
        value_label = tk.Label(
            box,
            text=value,
            font=('Segoe UI', 28, 'bold'),
            fg=color,
            bg=self.colors['bg_tertiary']
        )
        value_label.pack(pady=(5, 2))
        
        text_label = tk.Label(
            box,
            text=label,
            font=('Segoe UI', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_tertiary']
        )
        text_label.pack(pady=(0, 15))
        
        setattr(self, f"stat_{label.lower()}_label", value_label)
    
    def clear_console(self):
        """Clear console output"""
        self.console_text.config(state='normal')
        self.console_text.delete('1.0', tk.END)
        self.console_text.config(state='disabled')
    
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
        
        # Check SSL bypass setting (NEW)
        skip_ssl = getattr(self, 'quick_scan_skip_ssl_var', tk.BooleanVar(value=False)).get()
        if skip_ssl:
            self.log_console("[WARNING] ⚠️ SSL verification DISABLED - vulnerable to MITM attacks!")
        
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
                
                # Check if SSL verification should be skipped (from EITHER tab)
                skip_ssl_advanced = getattr(self, 'opt_skip_ssl_var', tk.BooleanVar(value=False)).get()
                skip_ssl_quick = getattr(self, 'quick_scan_skip_ssl_var', tk.BooleanVar(value=False)).get()
                skip_ssl = skip_ssl_advanced or skip_ssl_quick  # Skip if EITHER is checked
                
                # Configure scanner
                config = {
                    'api_key_manager': api_key_manager,
                    'provider': self.provider_var.get(),
                    'profile': self.profile_var.get(),
                    'verify_ssl': not skip_ssl  # Invert: checkbox is "skip", config is "verify"
                }
                
                # Log SSL warning if verification disabled
                if skip_ssl:
                    self.root.after(0, lambda: self.log_console("[WARNING] ⚠️ SSL verification DISABLED - vulnerable to MITM attacks!"))
                    self.root.after(0, lambda: self.log_console("[WARNING] Only use this for testing against sites with invalid/self-signed certificates"))
                
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
                
                # Store results for report generation
                self.last_scan_results = results
                self.root.after(0, lambda: self.log_console(f"[INFO] Scan results stored for report generation"))
                
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
        # Validate results structure (BUG FIX #1)
        if not isinstance(results, dict):
            self.log_console("[ERROR] Invalid scan results format")
            return
        
        # Ensure required keys exist
        if 'total_findings' not in results:
            self.log_console("[WARNING] Scan results missing total_findings, defaulting to 0")
            results['total_findings'] = 0
        if 'findings_by_severity' not in results:
            results['findings_by_severity'] = {}
        
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

        # Enable report button if we have findings
        if total_findings > 0:
            self.log_console(f"[INFO] ✅ You can now generate a report!")
            if hasattr(self, 'report_btn'):
                self.report_btn.config(state='normal')
        
        # Update Reports tab summary (NEW!)
        self.update_report_summary()
        
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
    
    def generate_raw_report(self):
        """Generate raw JSON/HTML report"""
        self.log_console("[REPORT] Generating raw report...")
        
        # Check if we have scan results
        if not hasattr(self, 'last_scan_results') or self.last_scan_results is None:
            messagebox.showerror("No Results", "No scan results available. Please run a scan first.")
            self.log_console("[ERROR] No scan results to generate report from")
            return
        
        try:
            # Import ReportGenerator
            import sys
            from pathlib import Path
            
            parent_dir = Path(__file__).resolve().parent.parent
            libs_dir = parent_dir / "libs" / "reporting"
            if str(libs_dir) not in sys.path:
                sys.path.insert(0, str(libs_dir))
            
            from report_generator import ReportGenerator
            
            # Create output directory
            reports_dir = parent_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            # Initialize generator
            templates_dir = libs_dir / "templates"
            generator = ReportGenerator(templates_dir=templates_dir)
            
            self.log_console("[REPORT] Initializing report generator...")
            
            # Generate reports in all formats
            output_files = generator.generate_all(
                scan_results=self.last_scan_results,
                output_dir=reports_dir,
                formats=['html', 'json']  # Skip PDF if reportlab not installed
            )
            
            self.log_console(f"[REPORT] ✅ Reports generated successfully!")
            
            # Show success message with file paths
            report_paths = "\n".join([f"  • {fmt.upper()}: {path}" for fmt, path in output_files.items()])
            message = f"Reports generated successfully!\n\nOutput files:\n{report_paths}\n\nReport directory: {reports_dir}"
            
            messagebox.showinfo("Report Generated", message)
            
            # Log each file
            for fmt, path in output_files.items():
                self.log_console(f"[REPORT] {fmt.upper()}: {path}")
            
            # Open HTML report in browser
            if 'html' in output_files:
                import webbrowser
                html_path = output_files['html']
                self.log_console(f"[REPORT] Opening HTML report in browser...")
                webbrowser.open(f"file://{html_path}")
                
        except ImportError as e:
            error_msg = f"Error importing report generator: {e}"
            self.log_console(f"[ERROR] {error_msg}")
            messagebox.showerror("Import Error", f"{error_msg}\n\nMake sure report_generator.py is in libs/reporting/")
            
        except Exception as e:
            error_msg = f"Error generating report: {e}"
            self.log_console(f"[ERROR] {error_msg}")
            messagebox.showerror("Report Error", error_msg)
            import traceback
            traceback.print_exc()
    
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
        """Log message to console (thread-safe with overflow protection)"""
        def update():
            try:
                if not hasattr(self, 'console_text') or not self.console_text.winfo_exists():
                    return
                    
                self.console_text.config(state='normal')
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.console_text.insert('end', f"[{timestamp}] {message}\n")
                
                # Overflow protection (BUG FIX): Limit to 1000 lines
                try:
                    line_count = int(self.console_text.index('end-1c').split('.')[0])
                    if line_count > 1000:
                        # Delete first 100 lines to prevent frequent trimming
                        self.console_text.delete('1.0', '101.0')
                except:
                    pass  # If line count fails, continue anyway
                
                self.console_text.see('end')
                self.console_text.config(state='disabled')
            except Exception as e:
                # Fallback: print to stderr if console update fails
                import sys
                print(f"[CONSOLE ERROR] {e}: {message}", file=sys.stderr)
        
        # Execute on main thread
        try:
            if hasattr(self, 'root'):
                self.root.after(0, update)
            else:
                update()
        except:
            # If scheduling fails, try direct call
            update()
    
    # setup_ai_analysis_tab removed - now using modular version from gui/tabs/ai_analysis_tab.py
    
    def start_ai_analysis(self):
        """Start AI-driven autonomous security analysis with real LLM"""
        target_url = self.ai_target_var.get().strip()
        
        if not target_url or target_url == 'https://example.com':
            messagebox.showwarning("Invalid URL", "Please enter a valid target URL")
            return
        
        if hasattr(self, 'ai_analysis_running') and self.ai_analysis_running:
            messagebox.showinfo("Analysis Running", "An AI analysis is already in progress")
            return
        
        # Get AI provider from UI (map to scanner providers)
        provider_ui = self.ai_provider_var.get() if hasattr(self, 'ai_provider_var') else 'OpenAI GPT-4'
        provider_map = {
            'OpenAI GPT-4': 'openai',
            'OpenAI GPT-3.5': 'openai',
            'Google Gemini': 'gemini',
            'Anthropic Claude': 'claude'
        }
        provider = provider_map.get(provider_ui, 'gemini')
        
        # Validate API key for selected provider
        from api_key_manager import APIKeyManager
        api_mgr = APIKeyManager()
        
        try:
            api_key = api_mgr.get_key(provider)
            if not api_key:
                messagebox.showerror("API Key Required", 
                                   f"Please configure your {provider.upper()} API key in the API Keys tab first")
                return
        except:
            messagebox.showerror("API Key Required", 
                               f"Please configure your {provider.upper()} API key in the API Keys tab")
            return
        
        # Parse natural language query if provided
        nlp_query = self.ai_nlp_query_var.get().strip()
        
        if nlp_query:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 💬 Natural Language Query: {nlp_query}")
        
        self.ai_analysis_running = True
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI Analysis initialized")
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Target: {target_url}")
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 AI Provider: {provider.upper()}")
        
        # Run real AI analysis in thread
        import threading
        thread = threading.Thread(target=self._run_real_ai_analysis_thread, 
                                 args=(target_url, nlp_query, provider))
        thread.daemon = True
        thread.start()
    
    def _run_real_ai_analysis_thread(self, target_url: str, nlp_query: str = "", provider: str = "gemini"):
        """Thread wrapper for async AI analysis"""
        import asyncio
        
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run async analysis
            loop.run_until_complete(self._run_real_ai_analysis(target_url, nlp_query, provider))
            
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")
            self.ai_update_reasoning(f"Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.ai_analysis_running = False
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ AI Analysis complete")
    
    async def _run_real_ai_analysis(self, target_url: str, nlp_query: str = "", provider: str = "gemini"):
        """Real AI-powered autonomous security analysis"""
        from api_key_manager import APIKeyManager
        from services.scanner_core.llm_analyzer import LLMAnalyzer
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 Initializing AI analyzer...")
        
        # Initialize LLM
        api_mgr = APIKeyManager()
        llm = LLMAnalyzer(api_mgr, provider)
        
        # ==========================================
        # PHASE 1: TARGET RECONNAISSANCE (15-30s)
        # ==========================================
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Phase 1: Target Reconnaissance")
        self.ai_update_reasoning("🔍 PHASE 1: TARGET RECONNAISSANCE\n\nAnalyzing target architecture and attack surface...")
        
        recon_prompt = f"""You are a professional penetration tester analyzing a target for security assessment.

Target URL: {target_url}
User Focus: {nlp_query if nlp_query else "Comprehensive security analysis"}

Analyze this target and provide:

1. **Technology Stack Detection**
   - Identify web server, frameworks, databases
   - Detect technologies from URL patterns

2. **Attack Surface Identification**
   - List potential entry points (login, search, file upload, etc.)
   - Identify user-controllable inputs

3. **Initial Security Assessment**
   - Obvious security headers missing?
   - Common misconfigurations?

4. **Recommended Test Vectors**
   - Top 5 most relevant vulnerability tests
   - Prioritize based on target characteristics

**Format as step-by-step analysis. Be concise but thorough.**
"""

        try:
            recon_response = await llm.chat(recon_prompt)
            self.ai_update_reasoning(f"🔍 PHASE 1: TARGET RECONNAISSANCE\n\n{recon_response}")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Reconnaissance complete")
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Reconnaissance failed: {e}")
            recon_response = "Unable to perform AI reconnaissance"
        
        # ==========================================
        # PHASE 2: VULNERABILITY DETECTION (30-60s)
        # ==========================================
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 Phase 2: Vulnerability Detection")
        
        # Determine focus areas
        if nlp_query:
            focus_context = f"Focus specifically on: {nlp_query}"
        else:
            focus_context = "Perform comprehensive vulnerability assessment"
        
        vuln_prompt = f"""You are performing autonomous vulnerability detection.

Target: {target_url}
Previous Reconnaissance:
{recon_response[:500]}...

{focus_context}

Generate a detailed vulnerability testing strategy:

1. **Test Vectors to Execute**
   - SQL Injection payloads (if applicable)
   - XSS vectors
   - CSRF checks
   - Authentication bypass attempts
   - File upload vulnerabilities

2. **Prioritization**
   - Which tests are most critical based on reconnaissance?
   - Expected risk levels

3. **Detection Logic**
   - How to identify if vulnerability exists
   - What responses indicate success

**Be specific and actionable. List exact tests to run.**
"""

        try:
            vuln_response = await llm.chat(vuln_prompt)
            self.ai_update_reasoning(f"🔬 PHASE 2: VULNERABILITY DETECTION\n\n{vuln_response}")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Vulnerability analysis complete")
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Vulnerability analysis failed: {e}")
            vuln_response = "Unable to perform AI vulnerability analysis"
        
        # ==========================================
        # PHASE 3: RECOMMENDATIONS (10-20s)
        # ==========================================
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 💡 Phase 3: Generating Recommendations")
        
        rec_prompt = f"""Based on the analysis, provide security recommendations.

Target: {target_url}
Analysis Results:
- Reconnaissance: {recon_response[:300]}...
- Vulnerability Strategy: {vuln_response[:300]}...

Generate:

1. **High Priority Findings**
   - Most critical security issues identified
   - Severity rating (Critical/High/Medium/Low)

2. **Remediation Steps**
   - Specific fixes for each issue
   - Code examples where applicable

3. **Best Practices**
   - General security improvements
   - Compliance recommendations (OWASP, NIST)

4. **Next Steps**
   - What should be tested manually
   - Tools to use for deeper analysis

**Provide actionable, professional recommendations suitable for a security report.**
"""

        try:
            rec_response = await llm.chat(rec_prompt)
            final_reasoning = f"""{'='*60}
🎯 AI SECURITY ANALYSIS COMPLETE
{'='*60}

TARGET: {target_url}
AI PROVIDER: {provider.upper()}
USER QUERY: {nlp_query if nlp_query else "N/A"}

{'='*60}
🔍 PHASE 1: RECONNAISSANCE
{'='*60}

{recon_response}

{'='*60}
🔬 PHASE 2: VULNERABILITY DETECTION STRATEGY
{'='*60}

{vuln_response}

{'='*60}
💡 PHASE 3: RECOMMENDATIONS
{'='*60}

{rec_response}

{'='*60}
"""
            self.ai_update_reasoning(final_reasoning)
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Recommendations generated")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Full AI analysis complete!")
            
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Recommendation generation failed: {e}")
            self.ai_update_reasoning(f"Analysis incomplete due to error: {e}")
    
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
    
    # ============ REPORTS TAB  METHODS ============
    
    def generate_ai_report(self):
        """Generate AI-enhanced professional report"""
        self.log_console("[AI REPORT] Generating AI-enhanced report...")
        
        # Check for scan results
        if not hasattr(self, 'last_scan_results') or self.last_scan_results is None:
            messagebox.showerror("No Results", "No scan results available. Please run a scan first.")
            self.log_console("[ERROR] No scan results to generate report from")
            return
        
        try:
            from pathlib import Path
            
            parent_dir = Path(__file__).resolve().parent.parent
            
            # Import AI report formatter
            from libs.reporting.ai_report_formatter import AIReportFormatter
            from api_key_manager import APIKeyManager
            from services.scanner_core.llm_analyzer import LLMAnalyzer
            
            # Get AI provider selection
            provider = self.ai_report_provider_var.get() if hasattr(self, 'ai_report_provider_var') else 'gemini'
            self.log_console(f"[AI REPORT] Using {provider.upper()} for report formatting...")
            
            # Initialize AI formatter
            api_mgr = APIKeyManager()
            llm = LLMAnalyzer(api_mgr, provider)
            formatter = AIReportFormatter(llm)
            
            self.log_console("[AI REPORT] Sending results to AI for formatting...")
            self.log_console("[AI REPORT] This may take 30-60 seconds...")
            
            # Format report with AI (using sync wrapper)
            ai_report_md = formatter.format_report_sync(self.last_scan_results, provider=provider)
            
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
        """Generate raw report (wrapper for existing generate_report)"""
        self.generate_report()
    
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
        """Update report summary after scan (thread-safe)"""
        # Thread-safe UI update (BUG FIX #2)
        def _update():
            try:
                if not hasattr(self, 'report_summary_label'):
                    return
                
                # Check if widget still exists
                if not self.report_summary_label.winfo_exists():
                    return
                
                if not hasattr(self, 'last_scan_results') or self.last_scan_results is None:
                    summary = "No scan completed yet. Run a scan first to generate reports."
                else:
                    # Validate results
                    if not isinstance(self.last_scan_results, dict):
                        summary = "Error: Invalid scan results"
                    else:
                        target = self.last_scan_results.get('target', 'Unknown')
                        total = self.last_scan_results.get('total_findings', 0)
                        severity = self.last_scan_results.get('findings_by_severity', {})
                        
                        summary = f"Target: {target}\n"
                        summary += f"Total Findings: {total} vulnerabilities\n"
                        summary += f"Critical: {severity.get('critical', 0)} | "
                        summary += f"High: {severity.get('high', 0)} | "
                        summary += f"Medium: {severity.get('medium', 0)} | "
                        summary += f"Low: {severity.get('low', 0)}"
                        
                        # Enable report buttons only if we have valid results
                        if total >= 0:  # Even 0 findings is valid
                            try:
                                if hasattr(self, 'generate_ai_report_btn') and self.generate_ai_report_btn.winfo_exists():
                                    self.generate_ai_report_btn.config(state='normal')
                                if hasattr(self, 'generate_raw_report_btn') and self.generate_raw_report_btn.winfo_exists():
                                    self.generate_raw_report_btn.config(state='normal')
                            except Exception as e:
                                self.log_console(f"[WARNING] Could not enable report buttons: {e}")
                
                self.report_summary_label.config(text=summary)
            except Exception as e:
                # Graceful degradation
                self.log_console(f"[ERROR] Failed to update report summary: {e}")
        
        # Ensure we're on main thread
        try:
            self.root.after(0, _update)
        except:
            # If root doesn't exist, call directly
            _update()
    
    def _convert_markdown_to_html(self, markdown_content: str, output_dir) -> str:
        """Convert Markdown to styled HTML"""
        from pathlib import Path
        output_dir = Path(output_dir)
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
        h3 {{ color: #7f8c8d; }}
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
    
    # ==============================================
    
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
