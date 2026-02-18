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
from gui.tabs.quick_scan_tab import setup_quick_scan_tab
from gui.tabs.advanced_scan_tab import setup_advanced_tab
from gui.tabs.ai_analysis_tab import setup_ai_analysis_tab
from gui.tabs.api_keys_tab import setup_api_tab
from gui.tabs.reports_tab import setup_reports_tab
from gui.tabs.results_tab import setup_results_tab  # Re-enabled for real-time monitoring


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
        self.provider_var = tk.StringVar(value="gemini")  # Default to gemini since user has gemini key
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
        
        # Pause/Resume state management (NEW!)
        self.scan_paused = False
        self.scan_pause_reason = None
        self.scan_state = {
            'target': None,
            'modules': None,
            'pages_scanned': 0,
            'total_pages': 0,
            'partial_results': [],
            'visited_urls': set(),
            'remaining_pages': []
        }
        
        # Database for persistent scan history
        try:
            from services.database.db_manager import DatabaseManager
            self.db = DatabaseManager()
            print("[DB] ✅ Database initialized successfully")
        except Exception as e:
            print(f"[DB] ⚠️ Failed to initialize database: {e}")
            self.db = None
        
        # Initialize scan history attributes (before tab creation)
        self.scan_history_listbox = None
        self.scan_history_ids = []
        self.scan_search_var = None
        self.selected_scan_details = None
        self.delete_scan_btn = None
        
        # Scan state management
        self.scan_running = False
        self.scan_paused = False
        self.last_scan_results = None
        self.current_scan_thread = None
        
        # Scan queue system
        self.scan_queue = []
        self.queue_processing = False
        
        # Progress tracking (initialized here, UI widgets set in setup_ui)
        self.progress_var = tk.IntVar(value=0)
        self.progress_label = None  # Will be set by setup_ui
        self.status_label = None    # Will be set by setup_ui
        
        # Scan history storage
        self.scan_history = []
        
        # Build UI
        self.setup_ui()
        
        # Load saved API keys if available
        self.load_saved_keys()
        
        # Load scan history from database
        if self.db:
            self.load_scan_history()
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def pause_scan(self, reason: str):
        """Pause current scan due to error or user request"""
        self.scan_paused = True
        self.scan_pause_reason = reason
        self.is_scanning = False
        
        # Update UI
        self.log_console(f"[SCAN] ⚠️ Scan paused: {reason}")
        self.log_console(f"[SCAN] Progress: {self.scan_state.get('pages_scanned', 0)}/{self.scan_state.get('total_pages', 0)} pages")
        self.log_console(f"[SCAN] Fix the issue and click 'Resume Scan' to continue")
        
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.config(text=f"⚠️ Paused: {reason}", fg=self.colors['warning'])
        
        # Show popup dialog
        messagebox.showwarning(
            "Scan Paused",
            f"⚠️ Scan has been paused:\n\n{reason}\n\n" +
            f"Progress: {self.scan_state.get('pages_scanned', 0)}/{self.scan_state.get('total_pages', 0)} pages scanned\n\n" +
            "Fix the issue (e.g., update API key in API Keys tab)\n" +
            "then click the 'Resume Scan' button to continue."
        )
        
        # Show resume buttons in ALL tabs
        for btn_attr in ['resume_scan_btn_quick', 'resume_scan_btn_advanced', 'resume_scan_btn_ai']:
            if hasattr(self, btn_attr):
                btn = getattr(self, btn_attr)
                if btn and btn.winfo_exists():
                    btn.config(state='normal')
                    try:
                        # Use pack with side='left' for button frames
                        btn.pack(side='left', padx=5)
                    except:
                        pass  # May already be packed
    
    def resume_scan(self):
        """Resume paused scan from saved state"""
        if not self.scan_paused:
            messagebox.showinfo("No Paused Scan", "There is no paused scan to resume.")
            return
        
        if not self.scan_state.get('target'):
            messagebox.showerror("Error", "Scan state corrupted - cannot resume")
            self.clear_scan_state()
            return
        
        self.log_console(f"[SCAN] ▶️ Resuming scan...")
        self.scan_paused = False
        self.scan_pause_reason = None
        
        # Hide resume buttons in ALL tabs
        for btn_attr in ['resume_scan_btn_quick', 'resume_scan_btn_advanced', 'resume_scan_btn_ai']:
            if hasattr(self, btn_attr):
                btn = getattr(self, btn_attr)
                if btn and btn.winfo_exists():
                    btn.config(state='disabled')
                    try:
                        btn.pack_forget()
                    except:
                        pass
        
        # Continue scan
        target = self.scan_state.get('target')
        modules = self.scan_state.get('modules', ['all'])
        self._execute_real_scan(target, modules, resume_state=self.scan_state.copy())
    
    def clear_scan_state(self):
        """Clear saved scan state"""
        self.scan_paused = False
        self.scan_pause_reason = None
        self.scan_state = {
            'target': None, 'modules': None, 'pages_scanned': 0,
            'total_pages': 0, 'partial_results': [], 'visited_urls': set(),
            'remaining_pages': []
        }
    
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
        ai_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        setup_ai_analysis_tab(ai_frame, self)
        notebook.add(ai_frame, text='AI Analysis')
        
        # Results tab - Real-time scan monitoring
        results_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        setup_results_tab(results_frame, self)
        notebook.add(results_frame, text='📊 Results')
        
        # API Keys tab
        api_keys_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        setup_api_tab(api_keys_frame, self)
        notebook.add(api_keys_frame, text='API Keys')
        
        # Reports tab
        reports_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        setup_reports_tab(reports_frame, self)
        notebook.add(reports_frame, text='📋 Reports')
        
        # Auto-load scan history after tab is created
        if self.db and hasattr(self, 'scan_history_listbox') and self.scan_history_listbox:
            self.root.after(100, self.refresh_scan_history)  # Delayed to ensure UI is ready
        
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
    
    def _execute_real_scan(self, target: str, modules: Optional[List[str]] = None, resume_state: Optional[Dict] = None):
        """Execute real scan in background thread with pause/resume support"""
        import threading
        
        def run_scan():
            try:
                import asyncio
                import sys
                from pathlib import Path
                
                # Import scanner exceptions
                sys.path.insert(0, str(Path(__file__).parent.parent / 'libs'))
                from scanner_exceptions import ScanPausedException, APIError
                
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
                
                from libs.api_key_manager import APIKeyManager
                
                # Get API keys from GUI and pass to scanner
                api_key_manager = APIKeyManager()
                
                # Set keys from GUI if they exist and SAVE to file
                keys_set = []
                for provider in ['openai', 'gemini', 'claude']:
                    key_var = getattr(self, f'api_key_{provider}', None)
                    if key_var:
                        key = key_var.get()
                        if key and key.strip():
                            # Set key in manager
                            api_key_manager.add_key(provider, key.strip()) # Changed to add_key
                            keys_set.append(provider)
                
                # CRITICAL: Save keys to file so scanner can read them
                if keys_set:
                    api_key_manager.save_keys()
                    self.root.after(0, lambda providers=keys_set: self.log_console(f"[API] Saved keys to file: {providers}"))
                else:
                    self.root.after(0, lambda: self.log_console("[API] ⚠️ No API keys found in GUI"))
                
                self.root.after(0, lambda: self.log_console(f"[API] Active keys: {list(api_key_manager.keys.keys())}"))
                
                # Check if SSL verification should be skipped (from EITHER tab)
                skip_ssl_advanced = getattr(self, 'opt_skip_ssl_var', tk.BooleanVar(value=False)).get()
                skip_ssl_quick = getattr(self, 'quick_scan_skip_ssl_var', tk.BooleanVar(value=False)).get()
                skip_ssl = skip_ssl_advanced or skip_ssl_quick  # Skip if EITHER is checked
                
                # Configure scanner
                config = {
                    'llm': {
                        'api_key_manager': api_key_manager,  # Move into llm subconfig!
                        'provider': self.provider_var.get()
                    },
                    'profile': self.profile_var.get(),
                    'verify_ssl': not skip_ssl  # Invert: checkbox is "skip", config is "verify"
                }
                
                # Log SSL warning if verification disabled
                if skip_ssl:
                    self.root.after(0, lambda: self.log_console("[WARNING] ⚠️ SSL verification DISABLED - vulnerable to MITM attacks!"))
                    self.root.after(0, lambda: self.log_console("[WARNING] Only use this for testing against sites with invalid/self-signed certificates"))
                
                # Create scanner with config
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
                
                # Store last scan results (keep for backwards compatibility)
                self.last_scan_results = results
                
                # Save to database for persistent history
                if self.db:
                    try:
                        # LOG: Debug scan results structure
                        self.root.after(0, lambda: self.log_console(f"[DEBUG] Results keys: {list(results.keys())}"))
                        self.root.after(0, lambda count=len(results.get('findings', [])): self.log_console(f"[DEBUG] Findings count in results: {count}"))
                        
                        # Use scan_id from scanner (passed as parameter)
                        scan_data = {
                            'scan_id': scan_id,  # Use existing scan_id from scanner
                            'target': target,
                            'scan_type': 'quick',  # TODO: detect scan type
                            'modules': modules if modules else ['all'],
                            'total_pages': results.get('total_pages', 0),
                            'findings': results.get('findings', [])
                        }
                        
                        # LOG: Debug scan_data being saved
                        self.root.after(0, lambda count=len(scan_data['findings']): self.log_console(f"[DEBUG] Saving {count} findings to database"))
                        
                        saved_id = self.db.save_scan(scan_data)
                        self.root.after(0, lambda sid=saved_id: self.log_console(f"[DB] ✅ Scan saved to database: {sid}"))
                    except Exception as e:
                        err_msg = str(e)
                        import traceback
                        err_trace = traceback.format_exc()
                        self.root.after(0, lambda msg=err_msg: self.log_console(f"[DB] ⚠️ Failed to save scan: {msg}"))
                        self.root.after(0, lambda trace=err_trace: self.log_console(f"[DB] Traceback: {trace}"))

                self.root.after(0, lambda: self.log_console(f"[INFO] Scan results stored for report generation"))
                
                # CRITICAL: Store results in main thread to ensure it's accessible
                self.root.after(0, lambda r=results: setattr(self, 'last_scan_results', r))
                
                loop.close()
                
                # Update UI with results
                self.root.after(0, lambda: self._display_scan_results(results))
                
            except ScanPausedException as e:
                # Scan paused - save state and trigger pause UI
                self.scan_state = e.state
                # Log to GUI console
                self.root.after(0, lambda reason=e.reason: self.log_console(f"[ERROR] API Error - Scan paused: {reason}"))
                self.root.after(0, lambda: self.log_console(f"[INFO] Progress saved: {e.state.get('pages_scanned', 0)}/{e.state.get('total_pages', 0)} pages"))
                # Show pause UI
                self.root.after(0, lambda reason=e.reason: self.pause_scan(reason))
                
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
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text="Scan in progress...")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Initializing...", fg=self.colors['warning'])
    
    def start_scan(self):
        """Start vulnerability scan or add to queue"""
        # Get scan configuration
        scan_config = self._get_scan_config()
        if not scan_config:
            return  # Validation failed
        
        # Check if scan is already running
        if self.scan_running:
            # Add to queue
            self.scan_queue.append(scan_config)
            queue_pos = len(self.scan_queue)
            messagebox.showinfo(
                "Scan Queued",
                f"A scan is already running.\n\n"
                f"Your scan has been added to the queue.\n"
                f"Position in queue: {queue_pos}\n\n"
                f"It will start automatically when the current scan completes."
            )
            self.log_console(f"[QUEUE] Scan added to queue (position {queue_pos})")
            self._update_queue_ui()
            return
        
        # Start scan immediately
        self._execute_scan(scan_config)
    
    def _get_scan_config(self):
        """Extract and validate scan configuration from UI"""
        # Reset scan state
        self.scan_complete = False
        self.scan_cancelled = False
        self.scan_paused = False
        
        # Reset progress
        self.progress_var.set(0)
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Preparing scan...", fg=self.colors['text_primary'])
        
        # Get target URL from input field
        target = self.target_var.get()
        
        if not target or target == "https://example.com or /path/to/directory":
            messagebox.showerror("Error", "Please enter a target URL or select a directory")
            return None
        
        # Detect target type
        is_url = target.startswith(('http://', 'https://'))
        target_type = "Web" if is_url else "Local"
        
        # Get scan mode
        scan_mode = self.scan_mode_var.get()
        modules = None if scan_mode == "full" else []  # None = all modules
        
        # Check if SSL verification should be skipped
        skip_ssl = self.opt_skip_ssl_var.get()
        
        # Construct scan configuration dictionary
        scan_config = {
            'target': target,
            'modules': modules,
            'scan_mode': scan_mode,
            'target_type': target_type,
            'provider': self.provider_var.get(),
            'profile': self.profile_var.get(),
            'skip_ssl': skip_ssl
        }
        
        return scan_config
    
    def _execute_scan(self, scan_config: Dict[str, Any], resume_state: Optional[Dict] = None):
        """Execute a scan based on the provided configuration."""
        self.scan_running = True
        self.current_scan_config = scan_config
        
        target = scan_config['target']
        modules = scan_config['modules']
        scan_mode = scan_config['scan_mode']
        target_type = scan_config['target_type']
        provider = scan_config['provider']
        profile = scan_config['profile']
        skip_ssl = scan_config['skip_ssl']
        
        # Log scan details
        mode_text = "Full Scan (All Modules)" if scan_mode == "full" else "Targeted Scan"
        self.log_console(f"[SCAN] Starting {mode_text} on {target_type} target")
        self.log_console(f"[TARGET] {target}")
        self.log_console(f"[INFO] Provider: {provider}")
        self.log_console(f"[INFO] Profile: {profile}")
        
        self.status_label.config(
            text=f"Scanning: {target}",
            fg=self.colors['accent_cyan']
        )
        
        # Start real scan in a new thread
        scan_thread = threading.Thread(
            target=self._run_scan_thread,
            args=(target, modules, provider, profile, skip_ssl, resume_state),
            daemon=True
        )
        scan_thread.start()
        
        # Show initial progress
        self.progress_var.set(10)
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text="Scan in progress...")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Initializing...", fg=self.colors['warning'])
    
    def _run_scan_thread(self, target, modules, provider, profile, skip_ssl, resume_state):
        """Internal method to run the actual scanner in a thread."""
        try:
            import asyncio
            import sys
            from pathlib import Path
            
            # Import scanner exceptions
            sys.path.insert(0, str(Path(__file__).parent.parent / 'libs'))
            from scanner_exceptions import ScanPausedException, APIError
            
            # Ensure parent directory is in path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Import scanner
            try:
                from services.scanner_core import ScannerCore
            except ImportError as e:
                err_msg = str(e)
                self.root.after(0, lambda msg=err_msg: self.log_console(f"[ERROR] Failed to import ScannerCore: {msg}"))
                self.root.after(0, lambda: self.log_console("[ERROR] Make sure scanner-core directory exists in services/"))
                self.root.after(0, lambda msg=err_msg: messagebox.showerror(
                    "Import Error", 
                    f"Failed to import scanner:\n{msg}\n\nMake sure services/scanner-core/ directory exists."
                ))
                self._scan_finished_callback(success=False, error_msg=err_msg)
                return
            
            # Import API key manager
            scanner_core_dir = parent_dir / "services" / "scanner-core"
            if str(scanner_core_dir) not in sys.path:
                sys.path.insert(0, str(scanner_core_dir))
            
            from libs.api_key_manager import APIKeyManager
            
            # Get API keys from GUI and pass to scanner
            api_key_manager = APIKeyManager()
            
            # Set keys from GUI if they exist and SAVE to file
            keys_set = []
            for p in ['openai', 'gemini', 'claude']:
                key_var = getattr(self, f'api_key_{p}', None)
                if key_var:
                    key = key_var.get()
                    if key and key.strip():
                        api_key_manager.keys[p] = [{'key': key.strip(), 'is_backup': False}]
                        keys_set.append(p)
            
            if keys_set:
                api_key_manager.save_keys()
                self.root.after(0, lambda providers=keys_set: self.log_console(f"[API] Saved keys to file: {providers}"))
            else:
                self.root.after(0, lambda: self.log_console("[API] ⚠️ No API keys found in GUI"))
            
            self.root.after(0, lambda: self.log_console(f"[API] Active keys: {list(api_key_manager.keys.keys())}"))
            
            # Configure scanner (FIXED: match Advanced Scan config structure)
            config = {
                'llm': {
                    'api_key_manager': api_key_manager,  # Move into llm subconfig!
                    'provider': provider                  # Move into llm subconfig!
                },
                'profile': profile,
                'verify_ssl': not skip_ssl
            }
            
            if skip_ssl:
                self.root.after(0, lambda: self.log_console("[WARNING] ⚠️ SSL verification DISABLED - vulnerable to MITM attacks!"))
                self.root.after(0, lambda: self.log_console("[WARNING] Only use this for testing against sites with invalid/self-signed certificates"))
            
            scanner = ScannerCore(config)
            
            scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.root.after(0, lambda: self.log_console("[SCAN] Initializing scanner..."))
            self.root.after(0, lambda: self.progress_var.set(5))
            
            results = loop.run_until_complete(
                scanner.scan(
                    target=target,
                    modules=modules,
                    scan_id=scan_id,
                    resume_state=resume_state
                )
            )
            
            self.last_scan_results = results
            
            if self.db:
                try:
                    scan_data = {
                        'scan_id': scan_id,
                        'target': target,
                        'scan_type': 'advanced', # Assuming advanced for now
                        'modules': modules if modules else ['all'],
                        'total_pages': results.get('total_pages', 0),
                        'findings': results.get('findings', [])
                    }
                    saved_id = self.db.save_scan(scan_data)
                    self.root.after(0, lambda: self.log_console(f"[DB] ✅ Scan saved to database: {saved_id}"))
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log_console(f"[DB] ⚠️ Failed to save scan: {err}"))
            
            self.root.after(0, lambda: self.log_console(f"[INFO] Scan results stored for report generation"))
            self.root.after(0, lambda r=results: setattr(self, 'last_scan_results', r))
            loop.close()
            
            self._scan_finished_callback(success=True, results=results)
            
        except ScanPausedException as e:
            self.scan_state = e.state
            self.root.after(0, lambda reason=e.reason: self.log_console(f"[ERROR] API Error - Scan paused: {reason}"))
            self.root.after(0, lambda: self.log_console(f"[INFO] Progress saved: {e.state.get('pages_scanned', 0)}/{e.state.get('total_pages', 0)} pages"))
            self._scan_finished_callback(success=False, paused=True, reason=e.reason)
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            self.root.after(0, lambda msg=error_msg: self.log_console(f"[ERROR] Scan failed: {msg}"))
            self.root.after(0, lambda trace=error_trace: self.log_console(f"[ERROR] Traceback:\n{trace}"))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Scan Error", f"Scan failed:\n\n{msg}"))
            self._scan_finished_callback(success=False, error_msg=error_msg)
    
    def _scan_finished_callback(self, success: bool, results: Optional[Dict] = None, error_msg: Optional[str] = None, paused: bool = False, reason: Optional[str] = None):
        """Callback executed when a scan thread finishes."""
        self.scan_running = False
        self.current_scan_config = None
        
        if success:
            self.scan_complete = True
            self.root.after(0, lambda: self._display_scan_results(results))
        elif paused:
            self.scan_paused = True
            self.root.after(0, lambda: self.pause_scan(reason))
        else:
            self.root.after(0, lambda: self.status_label.config(text="Scan failed", fg=self.colors['error']))
        
        self.root.after(0, self._process_scan_queue)
        self.root.after(0, self._update_queue_ui)
    
    def _process_scan_queue(self):
        """Process the next scan in the queue if no scan is running."""
        if not self.scan_running and self.scan_queue:
            next_scan_config = self.scan_queue.pop(0)
            self.log_console(f"[QUEUE] Starting next scan from queue: {next_scan_config['target']}")
            self._execute_scan(next_scan_config)
        elif not self.scan_running and not self.scan_queue:
            self.log_console("[QUEUE] Scan queue is empty.")
    
    def _update_queue_ui(self):
        """Update the UI to reflect the current queue status."""
        if hasattr(self, 'queue_status_label'):
            if self.scan_queue:
                self.queue_status_label.config(text=f"Queue: {len(self.scan_queue)} scans pending", fg=self.colors['warning'])
            else:
                self.queue_status_label.config(text="Queue: Empty", fg=self.colors['text_primary'])
    
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
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text="Scan completed")
        
        # Update status
        total_findings = results.get('total_findings', 0)
        if hasattr(self, 'status_label'):
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
        
        # CRITICAL FIX: Store scan results for Reports tab (Bug Fix #9)
        self.last_scan_results = results
        
        # Update Reports tab summary (NEW!)
        self.update_report_summary()
        self.update_bug_monitoring_dashboard()
        
        # Show completion dialog (check window exists to prevent TclError)
        try:
            if self.root and self.root.winfo_exists():
                messagebox.showinfo(
                    "Scan Complete",
                    "Scan finished successfully!\n\n" +
                    f"Total vulnerabilities: {total_findings}\n" +
                    f"Critical: {by_severity.get('critical', 0)}\n" +
                    f"High: {by_severity.get('high', 0)}\n" +
                    f"Medium: {by_severity.get('medium', 0)}\n" +
                    f"Low: {by_severity.get('low', 0)}"
                )
        except Exception as e:
            print(f"[INFO] Couldn't show completion dialog: {e}")
    
    def pause_scan(self):
        """Pause current scan"""
        self.log_console("[SCAN] Pausing scan...")
        # TODO: Implement pause
    
    def test_api_key(self, provider):
        """Test API key with real API call"""
        key = getattr(self, f"api_key_{provider}").get()
        
        if not key:
            messagebox.showerror("Error", f"Please enter {provider} API key first")
            return
        
        self.log_console(f"[API] Testing {provider} key...")
        
        status_label = getattr(self, f"{provider}_status_label")
        status_label.config(text="⏳ Testing...", fg=self.colors['warning'])
        
        # Test in background thread
        def test_in_thread():
            try:
                # Basic format validation first
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
                
                # Now test with real API call
                self.log_console(f"[API] Making test API call to {provider}...")
                
                success = False
                error_msg = None
                
                try:
                    if provider == 'gemini':
                        # Try NEW SDK first (google-genai), then fallback to OLD SDK (google-generativeai)
                        try:
                            # NEW SDK (google-genai) - https://ai.google.dev/gemini-api/docs/quickstart
                            from google import genai
                            self.log_console(f"[API] Using NEW Gemini SDK (google-genai)")
                            
                            # Create client with API key
                            client = genai.Client(api_key=key)
                            
                            # Test with simple generation using current stable model
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',  # Current stable model
                                contents='Test'
                            )
                            
                            if response and response.text:
                                self.log_console(f"[API] ✓ NEW SDK validation successful")
                                success = True
                        
                        except ImportError:
                            # Fallback to OLD SDK (google-generativeai)
                            self.log_console(f"[API] NEW SDK not found, trying OLD SDK (google-generativeai)")
                            
                            import google.generativeai as genai
                            genai.configure(api_key=key)
                            
                            # Try list_models to verify API key works (universal compatibility)
                            try:
                                self.log_console(f"[API] Verifying with list_models()...")
                                models = list(genai.list_models())
                                model_count = len(models)
                                self.log_console(f"[API] ✓ Successfully listed {model_count} models")
                                success = True
                            except Exception as list_error:
                                # Last resort: try direct generation with first available model
                                self.log_console(f"[API] list_models failed, trying direct generation...")
                                for m in genai.list_models():
                                    if 'generateContent' in m.supported_generation_methods:
                                        self.log_console(f"[API] Using model: {m.name}")
                                        model = genai.GenerativeModel(m.name)
                                        response = model.generate_content("Test")
                                        if response:
                                            success = True
                                            break
                        
                        except Exception as sdk_error:
                            error_msg = str(sdk_error)
                            self.log_console(f"[API] SDK test failed: {error_msg}")
                            raise Exception(error_msg)
                    
                    elif provider == 'openai':
                        from openai import OpenAI
                        client = OpenAI(api_key=key)
                        # Test with simple completion
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": "Test"}],
                            max_tokens=5
                        )
                        if response:
                            success = True
                    
                    elif provider == 'claude':
                        import anthropic
                        client = anthropic.Anthropic(api_key=key)
                        # Test with simple message
                        response = client.messages.create(
                            model="claude-3-haiku-20240307",
                            max_tokens=5,
                            messages=[{"role": "user", "content": "Test"}]
                        )
                        if response:
                            success = True
                
                except Exception as api_error:
                    error_msg = str(api_error)
                    success = False
                
                # Update UI from main thread
                def update_ui():
                    if success:
                        status_label.config(text="✓ Verified", fg=self.colors['success'])
                        self.log_console(f"[API] ✅ {provider.capitalize()} key is valid and working!")
                        messagebox.showinfo(
                            "Key Verified",
                            f"✅ {provider.capitalize()} API key is VALID!\n\n" +
                            "The key was successfully tested with a live API call."
                        )
                    else:
                        status_label.config(text="✗ Invalid", fg=self.colors['error'])
                        self.log_console(f"[ERROR] {provider.capitalize()} key validation failed: {error_msg}")
                        messagebox.showerror(
                            "Invalid Key",
                            f"❌ {provider.capitalize()} API key is INVALID!\n\n" +
                            f"API Error: {error_msg}\n\n" +
                            "Please check your API key and try again."
                        )
                
                self.root.after(0, update_ui)
                
            except ValueError as e:
                def show_format_error():
                    status_label.config(text="✗ Invalid", fg=self.colors['error'])
                    self.log_console(f"[ERROR] {provider.capitalize()} key format invalid: {e}")
                    messagebox.showerror("Invalid Key Format", f"{provider.capitalize()} API key format error:\n\n{str(e)}")
                
                self.root.after(0, show_format_error)
            
            except Exception as e:
                def show_general_error():
                    status_label.config(text="⚠ Error", fg=self.colors['warning'])
                    self.log_console(f"[ERROR] Failed to test {provider} key: {e}")
                    messagebox.showerror("Test Failed", f"Failed to test API key:\n\n{str(e)}")
                
                self.root.after(0, show_general_error)
        
        # Run test in background
        import threading
        thread = threading.Thread(target=test_in_thread, daemon=True)
        thread.start()
    
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
        try:
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
            
            # Validate API key for selected provider using GUI key variables
            key_var_map = {
                'openai': getattr(self, 'api_key_openai', None),
                'gemini': getattr(self, 'api_key_gemini', None),
                'claude': getattr(self, 'api_key_claude', None),
            }
            key_var = key_var_map.get(provider)
            api_key = key_var.get().strip() if key_var and hasattr(key_var, 'get') else ''
            if not api_key:
                messagebox.showerror("API Key Required", 
                                   f"Please configure your {provider.upper()} API key in the API Keys tab first")
                return
            
            # Parse natural language query if provided
            nlp_query = self.ai_nlp_query_var.get().strip() if hasattr(self, 'ai_nlp_query_var') else ""
            
            from datetime import datetime
            
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
            
        except Exception as e:
            self.log_console(f"[ERROR] Failed to start AI analysis: {e}")
            messagebox.showerror("Error", f"Failed to start AI analysis:\n\n{str(e)}")
            if hasattr(self, 'ai_analysis_running'):
                self.ai_analysis_running = False
    
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
        from libs.api_key_manager import APIKeyManager
        # Import LLMAnalyzer from scanner-core
        import sys
        from pathlib import Path
        scanner_core_dir = Path(__file__).parent.parent / "services" / "scanner-core"
        if str(scanner_core_dir) not in sys.path:
            sys.path.insert(0, str(scanner_core_dir))
        from llm_analyzer import LLMAnalyzer
        
        self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 Initializing AI analyzer...")
        
        # Initialize LLM with GUI's saved API keys (FIXED: was creating empty APIKeyManager)
        api_mgr = APIKeyManager()
        key_map = {
            'openai': getattr(self, 'api_key_openai', None),
            'gemini': getattr(self, 'api_key_gemini', None),
            'claude': getattr(self, 'api_key_claude', None),
        }
        for provider_name, key_var in key_map.items():
            if key_var is not None:
                key_value = key_var.get().strip() if hasattr(key_var, 'get') else str(key_var).strip()
                if key_value:
                    api_mgr.add_key(provider_name, key_value)
        
        llm = LLMAnalyzer(api_mgr, provider)
        
        # ==========================================
        # PHASE 1: TARGET RECONNAISSANCE (15-30s)
        # ==========================================
        # Clear steps frame
        self._ai_clear_steps()
        self._ai_add_step("🔍", "Phase 1: Target Reconnaissance", "Running...", 'warning')
        
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
            # Show results in console
            self.ai_log_console(f"\n{'─'*50}")
            self.ai_log_console(f"📋 RECONNAISSANCE RESULTS:")
            self.ai_log_console(f"{'─'*50}")
            self.ai_log_console(recon_response)
            self.ai_log_console(f"{'─'*50}\n")
            self._ai_update_step(0, "🔍", "Phase 1: Reconnaissance", "Complete ✅", 'success')
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Reconnaissance failed: {e}")
            recon_response = "Unable to perform AI reconnaissance"
            self._ai_update_step(0, "🔍", "Phase 1: Reconnaissance", f"Failed: {e}", 'error')
        
        # ==========================================
        # PHASE 2: VULNERABILITY DETECTION (30-60s)
        # ==========================================
        self._ai_add_step("🔬", "Phase 2: Vulnerability Detection", "Running...", 'warning')
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
            self.ai_log_console(f"\n{'─'*50}")
            self.ai_log_console(f"🔬 VULNERABILITY DETECTION RESULTS:")
            self.ai_log_console(f"{'─'*50}")
            self.ai_log_console(vuln_response)
            self.ai_log_console(f"{'─'*50}\n")
            self._ai_update_step(1, "🔬", "Phase 2: Vulnerability Detection", "Complete ✅", 'success')
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Vulnerability analysis failed: {e}")
            vuln_response = "Unable to perform AI vulnerability analysis"
            self._ai_update_step(1, "🔬", "Phase 2: Vulnerability Detection", f"Failed: {e}", 'error')
        
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
            self.ai_log_console(f"\n{'─'*50}")
            self.ai_log_console(f"💡 RECOMMENDATIONS:")
            self.ai_log_console(f"{'─'*50}")
            self.ai_log_console(rec_response)
            self.ai_log_console(f"{'─'*50}\n")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Full AI analysis complete!")
            self._ai_update_step(2, "💡", "Phase 3: Recommendations", "Complete ✅", 'success')
            
        except Exception as e:
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Recommendation generation failed: {e}")
            self._ai_update_step(2, "💡", "Phase 3: Recommendations", f"Failed: {e}", 'error')
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
                self.ai_reasoning_text.see('1.0')
                self.ai_reasoning_text.config(state='disabled')
            
            # Execute on main thread
            self.root.after(0, update)
    
    def _ai_clear_steps(self):
        """Clear all step widgets from the AI steps frame (thread-safe)"""
        def clear():
            if hasattr(self, 'ai_steps_frame'):
                for widget in self.ai_steps_frame.winfo_children():
                    widget.destroy()
                if hasattr(self, 'ai_step_widgets'):
                    self.ai_step_widgets.clear()
        self.root.after(0, clear)
    
    def _ai_add_step(self, icon, title, status, color_key='text_secondary'):
        """Add a step card to the AI steps frame (thread-safe)"""
        colors = self.colors
        def add():
            if not hasattr(self, 'ai_steps_frame'):
                return
            step_frame = tk.Frame(self.ai_steps_frame, bg=colors.get('bg_tertiary', '#0b1222'))
            step_frame.pack(fill='x', padx=10, pady=4)
            
            label = tk.Label(
                step_frame,
                text=f"  {icon}  {title}",
                font=('Segoe UI', 10, 'bold'),
                fg=colors.get('text_primary', '#e6eef8'),
                bg=colors.get('bg_tertiary', '#0b1222'),
                anchor='w'
            )
            label.pack(side='left', padx=5, pady=5)
            
            status_label = tk.Label(
                step_frame,
                text=status,
                font=('Segoe UI', 9),
                fg=colors.get(color_key, '#9fb0c9'),
                bg=colors.get('bg_tertiary', '#0b1222'),
                anchor='e'
            )
            status_label.pack(side='right', padx=10, pady=5)
            
            if not hasattr(self, 'ai_step_widgets'):
                self.ai_step_widgets = []
            self.ai_step_widgets.append({'frame': step_frame, 'label': label, 'status': status_label})
        self.root.after(0, add)
    
    def _ai_update_step(self, index, icon, title, status, color_key='success'):
        """Update an existing step card's status (thread-safe)"""
        colors = self.colors
        def update():
            if hasattr(self, 'ai_step_widgets') and index < len(self.ai_step_widgets):
                step = self.ai_step_widgets[index]
                step['status'].config(text=status, fg=colors.get(color_key, '#10b981'))
        self.root.after(0, update)
    
    def download_ai_results(self):
        """Download AI analysis results as a report file"""
        from tkinter import filedialog, messagebox
        from datetime import datetime
        
        # Get reasoning content
        reasoning_text = ""
        if hasattr(self, 'ai_reasoning_text'):
            self.ai_reasoning_text.config(state='normal')
            reasoning_text = self.ai_reasoning_text.get('1.0', 'end').strip()
            self.ai_reasoning_text.config(state='disabled')
        
        # Get console content
        console_text = ""
        if hasattr(self, 'ai_console_text'):
            self.ai_console_text.config(state='normal')
            console_text = self.ai_console_text.get('1.0', 'end').strip()
            self.ai_console_text.config(state='disabled')
        
        if not reasoning_text and not console_text:
            messagebox.showwarning("No Results", "No AI analysis results to download.\nRun an AI analysis first.")
            return
        
        target = getattr(self, 'ai_target_var', None)
        target_url = target.get() if target else "Unknown"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        file_path = filedialog.asksaveasfilename(
            title="Save AI Analysis Report",
            initialfile=f"EMYUEL_AI_Report_{filename_ts}",
            defaultextension=".html",
            filetypes=[
                ("HTML Report", "*.html"),
                ("Markdown Report", "*.md"),
                ("Text Report", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else 'txt'
            
            if ext == 'html':
                content = self._gen_ai_html(target_url, timestamp, reasoning_text, console_text)
            elif ext == 'md':
                content = self._gen_ai_md(target_url, timestamp, reasoning_text, console_text)
            else:
                content = self._gen_ai_txt(target_url, timestamp, reasoning_text, console_text)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Report Saved", f"AI analysis report saved to:\n{file_path}")
            self.ai_log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Report saved: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")
    
    def _gen_ai_txt(self, target, ts, reasoning, console):
        lines = [
            "=" * 70,
            "  EMYUEL - AI Security Analysis Report",
            "=" * 70, "",
            f"Date:   {ts}",
            f"Target: {target}", "",
            "=" * 70,
            "  AI ANALYSIS RESULTS",
            "=" * 70, "",
            reasoning, "",
            "=" * 70,
            "  CONSOLE LOG",
            "=" * 70, "",
            console, "",
            "=" * 70,
            "Generated by EMYUEL - Enterprise AI Security Scanning & Remediation",
            "=" * 70
        ]
        return "\n".join(lines)
    
    def _gen_ai_md(self, target, ts, reasoning, console):
        return f"""# EMYUEL AI Security Analysis Report

**Date:** {ts}  
**Target:** `{target}`  

---

## AI Analysis Results

{reasoning}

---

## Console Log

```
{console}
```

---

> Generated by **EMYUEL** - Enterprise AI Security Scanning & Remediation Platform
"""
    
    def _gen_ai_html(self, target, ts, reasoning, console):
        import html as html_mod
        r = html_mod.escape(reasoning).replace('\n', '<br>\n')
        c = html_mod.escape(console).replace('\n', '<br>\n')
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EMYUEL AI Security Report - {html_mod.escape(target)}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0b1220;color:#e6eef8;padding:40px}}
.wrap{{max-width:900px;margin:0 auto}}
.hdr{{background:linear-gradient(135deg,#0f1724,#1a2332);border:1px solid #243244;border-radius:12px;padding:30px;margin-bottom:24px}}
.hdr h1{{color:#00d4ff;font-size:22px;margin-bottom:12px}}
.hdr .m{{color:#9fb0c9;font-size:13px;line-height:1.8}}
.hdr .m b{{color:#00d4ff}}
.sec{{background:#0f1724;border:1px solid #243244;border-radius:12px;padding:24px;margin-bottom:20px}}
.sec h2{{color:#00d4ff;font-size:17px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #243244}}
.sec pre{{background:#0b1222;padding:16px;border-radius:8px;overflow-x:auto;white-space:pre-wrap;word-wrap:break-word;font-size:12px;line-height:1.5;color:#9fb0c9}}
.body{{white-space:pre-wrap;line-height:1.7;font-size:13px}}
.ft{{text-align:center;color:#9fb0c9;font-size:11px;margin-top:30px;padding:20px;border-top:1px solid #243244}}
.ft b{{color:#7c3aed}}
.badge{{display:inline-block;background:#7c3aed;color:#fff;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:bold}}
</style>
</head>
<body>
<div class="wrap">
<div class="hdr">
<h1>🛡️ EMYUEL AI Security Analysis Report</h1>
<div class="m"><b>Date:</b> {ts}<br><b>Target:</b> {html_mod.escape(target)}<br><b>Tool:</b> <span class="badge">EMYUEL Scanner</span></div>
</div>
<div class="sec"><h2>📋 AI Analysis Results</h2><div class="body">{r}</div></div>
<div class="sec"><h2>📄 Console Log</h2><pre>{c}</pre></div>
<div class="ft">Generated by <b>EMYUEL</b> - Enterprise AI Security Scanning &amp; Remediation Platform</div>
</div>
</body>
</html>"""
    
    
    def generate_ai_report(self):
        """Generate AI-enhanced professional report"""
        self.log_console("[AI REPORT] Generating AI-enhanced report...")
        
        # Check for scan results - try last_scan_results first, then database
        scan_results = None
        
        if hasattr(self, 'last_scan_results') and self.last_scan_results is not None:
            scan_results = self.last_scan_results
            self.log_console("[AI REPORT] Using current scan results")
        elif self.db:
            # Try to load most recent scan from database
            try:
                scans = self.db.get_all_scans(limit=1)
                if scans:
                    scan_id = scans[0]['scan_id']
                    scan_data = self.db.get_scan_by_id(scan_id)
                    if scan_data:
                        # Convert database format to expected format
                        scan_results = {
                            'target': scan_data['target_url'],
                            'scan_type': scan_data['scan_type'],
                            'timestamp': scan_data['timestamp'],
                            'total_findings': scan_data['total_findings'],
                            'findings_by_severity': scan_data['findings_by_severity'],
                            'findings': scan_data['findings']
                        }
                        self.log_console(f"[AI REPORT] Loaded scan from database: {scan_id}")
            except Exception as e:
                self.log_console(f"[ERROR] Failed to load scan from database: {e}")
        
        if not scan_results:
            messagebox.showerror(
                "No Results", 
                "No scan results available.\n\n"
                "Please run a scan first or ensure scan history is not empty."
            )
            self.log_console("[ERROR] No scan results to generate report from")
            return
        
        try:
            from pathlib import Path
            
            parent_dir = Path(__file__).resolve().parent.parent
            
            # Import AI report formatter
            from libs.reporting.ai_report_formatter import AIReportFormatter
            from libs.api_key_manager import APIKeyManager  # Fixed import path
            from services.ai_planner import AIPlanner
            
            # Add scanner-core to path and import LLMAnalyzer
            import sys
            from pathlib import Path
            scanner_core_dir = Path(__file__).parent.parent / "services" / "scanner-core"
            if str(scanner_core_dir) not in sys.path:
                sys.path.insert(0, str(scanner_core_dir))
            from llm_analyzer import LLMAnalyzer
            
            # Get AI provider selection
            provider = self.ai_report_provider_var.get() if hasattr(self, 'ai_report_provider_var') else 'gemini'
            self.log_console(f"[AI REPORT] Using {provider.upper()} for report formatting...")
            
            # Initialize AI formatter
            api_mgr = APIKeyManager()
            
            # Set API keys from GUI
            for provider_name in ['openai', 'gemini', 'claude']:
                key_var = getattr(self, f'api_key_{provider_name}', None)
                if key_var:
                    key_value = key_var.get()
                    if key_value and key_value.strip():
                        api_mgr.add_key(provider_name, key_value.strip())
                        self.log_console(f"[DEBUG] Set {provider_name} key for AI report")
            
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
        """Generate raw JSON/HTML report from scan results"""
        try:
            if not hasattr(self, 'last_scan_results') or not self.last_scan_results:
                self.log_console("[ERROR] No scan results available to generate report")
                messagebox.showerror("Error", "No scan results available. Please run a scan first.")
                return
            
            from libs.reporting.report_generator import ReportGenerator
            from datetime import datetime
            from tkinter import filedialog
            import os
            
            self.log_console("[REPORT] Generating raw report...")
            
            # Ask user where to save the report
            target = self.last_scan_results.get('target', 'unknown')
            safe_target = target.replace('://', '_').replace('/', '_').replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"report_{safe_target}_{timestamp}.html"
            
            # Default directory
            default_dir = os.path.join(os.path.expanduser('~'), '.emyuel', 'reports')
            os.makedirs(default_dir, exist_ok=True)
            
            # Ask user for save location
            save_path = filedialog.asksaveasfilename(
                title="Save Report As",
                initialdir=default_dir,
                initialfile=default_filename,
                defaultextension=".html",
                filetypes=[("HTML Report", "*.html"), ("All Files", "*.*")]
            )
            
            if not save_path:
                self.log_console("[INFO] Report generation cancelled by user")
                return
            
            self.log_console(f"[INFO] Saving report to: {save_path}")
            
            # Generate report using ReportGenerator
            report_gen = ReportGenerator()
            
            # Create temp directory for generate_all
            import tempfile
            from pathlib import Path
            temp_dir = Path(tempfile.mkdtemp())
            
            try:
                # Generate HTML report
                result_paths = report_gen.generate_all(
                    self.last_scan_results,
                    output_dir=temp_dir,
                    formats=['html']
                )
                
                generated_html = result_paths.get('html')
                
                if not generated_html or not os.path.exists(generated_html):
                    raise Exception(f"Report generation failed - no file created at {generated_html}")
                
                # Copy to user-selected location
                import shutil
                shutil.copy2(generated_html, save_path)
                
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                self.log_console(f"[SUCCESS] Report generated: {save_path}")
                
                # Ask if user wants to open the report
                if messagebox.askyesno("Success", f"Report generated successfully!\n\nSaved to:\n{save_path}\n\nOpen report now?"):
                    # Open in browser
                    import webbrowser
                    webbrowser.open(f"file://{save_path}")
                    
            except Exception as e:
                self.log_console(f"[ERROR] Report generation failed: {e}")
                import traceback
                self.log_console(f"[ERROR] Traceback: {traceback.format_exc()}")
                messagebox.showerror("Error", f"Failed to generate report:\n{e}")
            
            # Refresh report history if tab exists
            if hasattr(self, 'refresh_report_history'):
                self.refresh_report_history()
                
        except Exception as e:
            self.log_console(f"[ERROR] Failed to generate report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_scan_history(self):
        """Load scan history from database"""
        if not self.db:
            return
            
        try:
            # Get recent scans from database
            scans = self.db.get_all_scans(limit=100)
            self.scan_history = scans
            
            count = len(scans)
            if count > 0:
                self.log_console(f"[DB] Loaded {count} previous scan(s) from database")
            
            # Update UI if scan history widget exists
            if hasattr(self, 'scan_history_listbox') and self.scan_history_listbox:
                self.refresh_scan_history_ui()
                
        except Exception as e:
            self.log_console(f"[DB] ⚠️ Failed to load scan history: {e}")
            self.scan_history = []
            import traceback
            traceback.print_exc()
    
    def refresh_scan_history_ui(self):
        """Refresh scan history listbox with database entries"""
        if not hasattr(self, 'scan_history_listbox') or not self.scan_history_listbox:
            return
            
        try:
            # Clear current list
            self.scan_history_listbox.delete(0, tk.END)
            self.scan_history_ids = []
            
            # Add each scan
            for scan in self.scan_history:
                scan_id = scan.get('scan_id', 'unknown')
                target = scan.get('target_url', 'unknown')
                total = scan.get('total_findings', 0)
                timestamp = scan.get('timestamp', '')
                
                # Format for display
                display_text = f"{timestamp[:16]} | {target[:40]} | {total} findings"
                self.scan_history_listbox.insert(tk.END, display_text)
                self.scan_history_ids.append(scan_id)
                
            # Update count label if exists
            if hasattr(self, 'scan_count_label'):
                self.scan_count_label.config(text=f"Total scans: {len(self.scan_history)}")
                
        except Exception as e:
            self.log_console(f"[UI] Failed to refresh scan history: {e}")
    
    def delete_selected_scan(self):
        """Delete selected scan from database"""
        if not hasattr(self, 'scan_history_listbox') or not self.scan_history_listbox:
            messagebox.showerror("Error", "Scan history not available")
            return
            
        selection = self.scan_history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a scan to delete")
            return
            
        try:
            # Get scan ID
            index = selection[0]
            scan_id = self.scan_history_ids[index]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", 
                                   f"Delete scan {scan_id}?\n\nThis will remove all findings and reports."):
                # Delete from database
                if self.db:
                    success = self.db.delete_scan(scan_id)
                    if success:
                        self.log_console(f"[DB] ✅ Deleted scan: {scan_id}")
                        
                        # Reload history
                        self.load_scan_history()
                        
                        messagebox.showinfo("Success", "Scan deleted successfully")
                    else:
                        messagebox.showerror("Error", "Failed to delete scan from database")
                else:
                    messagebox.showerror("Error", "Database not available")
                    
        except Exception as e:
            self.log_console(f"[ERROR] Failed to delete scan: {e}")
            messagebox.showerror("Error", f"Failed to delete scan: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
    
    def update_bug_monitoring_dashboard(self):
        """Update bug monitoring dashboard with discovered vulnerabilities (thread-safe)"""
        def _update():
            try:
                # Check if widgets exist
                if not (hasattr(self, 'bugs_total_count') and 
                       hasattr(self, 'bugs_scrollable_frame')):
                    return
                
                # Get findings from scan results
                if not hasattr(self, 'last_scan_results') or self.last_scan_results is None:
                    # No scan results - show empty state
                    total = critical = high = other = 0
                    findings = []
                else:
                    findings = self.last_scan_results.get('findings', [])
                    severity_counts = self.last_scan_results.get('findings_by_severity', {})
                    
                    total = len(findings)
                    critical = severity_counts.get('critical', 0)
                    high = severity_counts.get('high', 0)
                    medium = severity_counts.get('medium', 0)
                    low = severity_counts.get('low', 0)
                    other = medium + low
                
                # Update stat cards
                self.bugs_total_count.config(text=str(total))
                self.bugs_critical_count.config(text=str(critical))
                self.bugs_high_count.config(text=str(high))
                self.bugs_other_count.config(text=str(other))
                
                # Clear existing bug list
                for widget in self.bugs_scrollable_frame.winfo_children():
                    widget.destroy()
                
                if total == 0:
                    # Show empty state
                    self.bugs_empty_label = tk.Label(
                        self.bugs_scrollable_frame,
                        text="No vulnerabilities discovered yet.\nRun a scan to populate this dashboard.",
                        font=('Segoe UI', 10),
                        fg=self.colors['text_secondary'],
                        bg=self.colors['bg_tertiary'],
                        justify='center',
                        pady=40
                    )
                    self.bugs_empty_label.pack(fill='both', expand=True)
                else:
                    # Populate bug list
                    for idx, finding in enumerate(findings):
                        severity = finding.get('severity', 'unknown').upper()
                        vuln_type = finding.get('type', 'Unknown')
                        location = finding.get('file', finding.get('url', 'N/A'))
                        description = finding.get('description', finding.get('message', 'No description'))
                        
                        # Truncate long strings
                        if len(location) > 50:
                            location = location[:47] + "..."
                        if len(description) > 60:
                            description = description[:57] + "..."
                        
                        # Create row
                        row = tk.Frame(self.bugs_scrollable_frame, bg=self.colors['bg_tertiary'])
                        row.pack(fill='x', pady=1)
                        
                        # Severity color coding
                        severity_colors = {
                            'CRITICAL': self.colors['error'],
                            'HIGH': self.colors['warning'],
                            'MEDIUM': self.colors['accent_cyan'],
                            'LOW': self.colors['success']
                        }
                        sev_color = severity_colors.get(severity, self.colors['text_secondary'])
                        
                        # Severity badge
                        sev_frame = tk.Frame(row, bg=self.colors['bg_tertiary'], width=100)
                        sev_frame.pack(side='left', fill='y', padx=5)
                        sev_frame.pack_propagate(False)
                        
                        sev_badge = tk.Label(
                            sev_frame,
                            text=severity,
                            font=('Segoe UI', 8, 'bold'),
                            fg=sev_color,
                            bg=self.colors['bg_tertiary'],
                            anchor='w'
                        )
                        sev_badge.pack(fill='both', expand=True, padx=5, pady=5)
                        
                        # Type
                        type_frame = tk.Frame(row, bg=self.colors['bg_tertiary'])
                        type_frame.pack(side='left', fill='both', expand=True)
                        
                        tk.Label(
                            type_frame,
                            text=vuln_type,
                            font=('Segoe UI', 9),
                            fg=self.colors['text_primary'],
                            bg=self.colors['bg_tertiary'],
                            anchor='w'
                        ).pack(fill='both', padx=5, pady=5)
                        
                        # Location
                        loc_frame = tk.Frame(row, bg=self.colors['bg_tertiary'])
                        loc_frame.pack(side='left', fill='both', expand=True)
                        
                        tk.Label(
                            loc_frame,
                            text=location,
                            font=('Segoe UI', 9),
                            fg=self.colors['text_secondary'],
                            bg=self.colors['bg_tertiary'],
                            anchor='w'
                        ).pack(fill='both', padx=5, pady=5)
                        
                        # Description
                        desc_frame = tk.Frame(row, bg=self.colors['bg_tertiary'])
                        desc_frame.pack(side='left', fill='both', expand=True)
                        
                        tk.Label(
                            desc_frame,
                            text=description,
                            font=('Segoe UI', 8),
                            fg=self.colors['text_secondary'],
                            bg=self.colors['bg_tertiary'],
                            anchor='w'
                        ).pack(fill='both', padx=5, pady=5)
                        
                        # Alternating row colors
                        if idx % 2 == 1:
                            for frame in [row, sev_frame, type_frame, loc_frame, desc_frame]:
                                frame.config(bg=self.colors['bg_primary'])
                            sev_badge.config(bg=self.colors['bg_primary'])
                            for label in [type_frame, loc_frame, desc_frame]:
                                for child in label.winfo_children():
                                    if isinstance(child, tk.Label):
                                        child.config(bg=self.colors['bg_primary'])
                
                self.log_console(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Bug monitoring dashboard updated: {total} vulnerabilities")
                
            except Exception as e:
                self.log_console(f"[ERROR] Failed to update bug monitoring: {e}")
                import traceback
                traceback.print_exc()
        
        # Thread-safe update
        try:
            self.root.after(0, _update)
        except:
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
    
    # ============ SCAN HISTORY MANAGEMENT (Database) ============
    
    def refresh_scan_history(self):
        """Load scans from database and populate listbox"""
        if not self.db:
            self.log_console("[DB] ⚠️ Database not available")
            return
        
        # Check if UI widgets exist
        if not hasattr(self, 'scan_history_listbox') or not self.scan_history_listbox:
            return  # UI not ready yet
        
        try:
            # Clear listbox
            self.scan_history_listbox.delete(0, tk.END)
            self.scan_history_ids = []
            
            # Get scans from database
            scans = self.db.get_all_scans(limit=50)
            
            if not scans:
                self.scan_history_listbox.insert(tk.END, "No scans found - Run a scan to see history here")
                if self.selected_scan_details:
                    self.selected_scan_details.config(text="No scans in database yet")
                return
            
            # Populate listbox
            for scan in scans:
                # Format: URL | timestamp | findings count
                timestamp = scan.get('timestamp', 'Unknown').split('.')[0]  # Remove microseconds
                text = f"{scan['target_url']} | {timestamp} | {scan['total_findings']} findings"
                
                self.scan_history_listbox.insert(tk.END, text)
                self.scan_history_ids.append(scan['scan_id'])
            
            # Auto-select most recent (first item)
            if len(scans) > 0:
                self.scan_history_listbox.select_set(0)
                self.scan_history_listbox.event_generate('<<ListboxSelect>>')
            
            self.log_console(f"[DB] Loaded {len(scans)} scans from history")
            
        except Exception as e:
            self.log_console(f"[DB] ⚠️ Error loading scan history: {e}")
            print(f"[DB] Error: {e}")
    
    def on_scan_selected(self, event):
        """Handle scan selection from listbox"""
        if not self.db:
            return
        
        selection = self.scan_history_listbox.curselection()
        if not selection:
            return
        
        try:
            index = selection[0]
            
            # Check if this is the "no scans" message
            if not self.scan_history_ids:
                return
            
            if index >= len(self.scan_history_ids):
                return
            
            scan_id = self.scan_history_ids[index]
            
            # Load scan from database
            scan = self.db.get_scan_by_id(scan_id)
            
            if not scan:
                self.log_console(f"[DB] ⚠️ Scan not found: {scan_id}")
                return
            
            # Update details display
            timestamp = scan.get('timestamp', 'Unknown').split('.')[0]
            modules = ', '.join(scan.get('modules', []))
            
            details_text = f"""✅ Selected Scan Details:
Target: {scan['target_url']}
Scanned: {timestamp}
Total Findings: {scan['total_findings']} (Critical: {scan['critical_count']}, High: {scan['high_count']}, Medium: {scan['medium_count']}, Low: {scan['low_count']})
Modules: {modules}
Status: {scan['status']}"""
            
            self.selected_scan_details.config(text=details_text)
            
            # Enable delete button
            if hasattr(self, 'delete_scan_btn'):
                self.delete_scan_btn.config(state='normal')
            
            # Update report summary to show selected scan
            self.report_summary_label.config(text=details_text)
            
            # Update last_scan_results for report generation
            self.last_scan_results = {
                'target': scan['target_url'],
                'total_findings': scan['total_findings'],
                'findings': scan['findings'],
                'findings_by_severity': {
                    'critical': scan['critical_count'],
                    'high': scan['high_count'],
                    'medium': scan['medium_count'],
                    'low': scan['low_count'],
                    'info': scan['info_count']
                }
            }
            
            # Enable report buttons
            if hasattr(self, 'generate_ai_report_btn'):
                self.generate_ai_report_btn.config(state='normal')
            if hasattr(self, 'generate_raw_report_btn'):
                self.generate_raw_report_btn.config(state='normal')
            
            # Update bugs dashboard
            self._update_bugs_dashboard(scan['findings'])
            
            self.log_console(f"[DB] ✅ Loaded scan: {scan['target_url']} ({scan['total_findings']} findings)")
            
        except Exception as e:
            self.log_console(f"[DB] ⚠️ Error loading scan details: {e}")
            print(f"[DB] Error: {e}")
    
    def search_scans(self):
        """Search scans by target URL"""
        if not self.db:
            return
        
        query = self.scan_search_var.get().strip()
        
        if not query:
            # If empty, show all scans
            self.refresh_scan_history()
            return
        
        try:
            # Search database
            results = self.db.search_scans(query)
            
            # Clear listbox
            self.scan_history_listbox.delete(0, tk.END)
            self.scan_history_ids = []
            
            if not results:
                self.scan_history_listbox.insert(tk.END, f"No scans found matching '{query}'")
                return
            
            # Populate with search results
            for scan in results:
                timestamp = scan.get('timestamp', 'Unknown').split('.')[0]
                text = f"{scan['target_url']} | {timestamp} | {scan['total_findings']} findings"
                
                self.scan_history_listbox.insert(tk.END, text)
                self.scan_history_ids.append(scan['scan_id'])
            
            self.log_console(f"[DB] Found {len(results)} scans matching '{query}'")
            
        except Exception as e:
            self.log_console(f"[DB] ⚠️ Search error: {e}")
    
    def delete_selected_scan(self):
        """Delete selected scan from history"""
        if not self.db:
            return
        
        selection = self.scan_history_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a scan to delete")
            return
        
        try:
            index = selection[0]
            
            if index >= len(self.scan_history_ids):
                return
            
            scan_id = self.scan_history_ids[index]
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete", 
                "Are you sure you want to delete this scan from history?\n\n" +
                "This action cannot be undone."):
                return
            
            # Delete from database
            if self.db.delete_scan(scan_id):
                self.log_console(f"[DB] ✅ Deleted scan: {scan_id}")
                
                # Refresh list
                self.refresh_scan_history()
                
                # Clear selection details
                self.selected_scan_details.config(text="Scan deleted - Select another scan")
                
                # Disable delete button
                if hasattr(self, 'delete_scan_btn'):
                    self.delete_scan_btn.config(state='disabled')
            else:
                self.log_console(f"[DB] ⚠️ Failed to delete scan: {scan_id}")
                messagebox.showerror("Delete Failed", "Could not delete scan from database")
                
        except Exception as e:
            self.log_console(f"[DB] ⚠️ Delete error: {e}")
            messagebox.showerror("Error", f"Failed to delete scan: {e}")
    
    def _update_bugs_dashboard(self, findings):
        """Update bugs monitoring dashboard with findings"""
        if not hasattr(self, 'bugs_scrollable_frame'):
            return
        
        try:
            # Clear existing bugs
            for widget in self.bugs_scrollable_frame.winfo_children():
                widget.destroy()
            
            if not findings:
                # Show empty message
                tk.Label(
                    self.bugs_scrollable_frame,
                    text="No vulnerabilities in selected scan",
                    font=('Segoe UI', 10),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['bg_tertiary'],
                    justify='center',
                    pady=40
                ).pack(fill='both', expand=True)
                
                # Update counts
                if hasattr(self, 'bugs_total_count'):
                    self.bugs_total_count.config(text="0")
                if hasattr(self, 'bugs_critical_count'):
                    self.bugs_critical_count.config(text="0")
                if hasattr(self, 'bugs_high_count'):
                    self.bugs_high_count.config(text="0")
                if hasattr(self, 'bugs_other_count'):
                    self.bugs_other_count.config(text="0")
                return
            
            # Count by severity
            counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            for finding in findings:
                sev = finding.get('severity', 'info').lower()
                if sev in counts:
                    counts[sev] += 1
            
            # Update count labels
            if hasattr(self, 'bugs_total_count'):
                self.bugs_total_count.config(text=str(len(findings)))
            if hasattr(self, 'bugs_critical_count'):
                self.bugs_critical_count.config(text=str(counts['critical']))
            if hasattr(self, 'bugs_high_count'):
                self.bugs_high_count.config(text=str(counts['high']))
            if hasattr(self, 'bugs_other_count'):
                self.bugs_other_count.config(text=str(counts['medium'] + counts['low'] + counts['info']))
            
            # Add finding rows (limit for performance)
            for i, finding in enumerate(findings[:50]):  # Limit to 50
                row_frame = tk.Frame(self.bugs_scrollable_frame, bg=self.colors['bg_tertiary'])
                row_frame.pack(fill='x', pady=1)
                
                # Severity
                sev = finding.get('severity', 'info').lower()
                sev_icons = {
                    'critical': ('🔴', self.colors['critical']),
                    'high': ('🟠', self.colors['error']),
                    'medium': ('🟡', self.colors['warning']),
                    'low': ('🟢', self.colors['success']),
                    'info': ('ℹ️', self.colors['text_secondary'])
                }
                icon, color = sev_icons.get(sev, ('•', self.colors['text_secondary']))
                
                tk.Label(
                    row_frame,
                    text=f"{icon} {sev.upper()}",
                    font=('Segoe UI', 9),
                    fg=color,
                    bg=self.colors['bg_tertiary'],
                width=15
                ).pack(side='left', padx=5)
                
                tk.Label(
                    row_frame,
                    text=finding.get('vulnerability_type', finding.get('type', 'Unknown')),
                    font=('Segoe UI', 9),
                    fg=self.colors['text_primary'],
                    bg=self.colors['bg_tertiary'],
                    anchor='w',
                    width=20
                ).pack(side='left', padx=5)
                
                url_text = finding.get('url', '')[:40] + ('...' if len(finding.get('url', '')) > 40 else '')
                tk.Label(
                    row_frame,
                    text=url_text,
                    font=('Segoe UI', 9),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['bg_tertiary'],
                    anchor='w',
                    width=30
                ).pack(side='left', padx=5)
                
                desc = finding.get('description', finding.get('title', ''))[:30]
                tk.Label(
                    row_frame,
                    text=desc + ('...' if len(finding.get('description', '')) > 30 else ''),
                    font=('Segoe UI', 8),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['bg_tertiary'],
                    anchor='w'
                ).pack(side='left', padx=5, fill='x', expand=True)
                
        except Exception as e:
            print(f"[GUI] Error updating bugs dashboard: {e}")
    
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
