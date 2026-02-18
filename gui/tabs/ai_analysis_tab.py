"""
ai_analysis_tab.py

AI Analysis tab setup - responsive layout + cross-platform mousewheel support.

Usage:
    Replace your existing ai_analysis_tab.py with this file (or copy the function
    setup_ai_analysis_tab into your project). This code expects a `gui_instance`
    object that provides:
      - colors (dict)
      - start_ai_analysis (callable)
      - create_scrollable_frame(parent) optional helper (if present, this will be used)
      - attributes like ai_target_var, ai_nlp_query_var, ai_depth_var, etc. will be set on gui_instance
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext


def setup_ai_analysis_tab(parent, gui_instance):
    """
    Setup AI-driven autonomous security analysis tab (responsive + cross-platform scroll)

    Args:
        parent: Parent frame for this tab
        gui_instance: Reference to main GUI instance for colors and callbacks
    """
    colors = getattr(gui_instance, "colors", {
        'bg_primary': '#0b1220',
        'bg_secondary': '#0f1724',
        'bg_tertiary': '#0b1222',
        'text_primary': '#e6eef8',
        'text_secondary': '#9fb0c9',
        'accent_cyan': '#00d4ff',
        'accent_purple': '#7c3aed',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'border': '#243244'
    })

    # If gui_instance provides a helper to create a standard scrollable frame, use it
    try:
        scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
        # `create_scrollable_frame` should return (frame, canvas). If it doesn't, fallback below.
        if not isinstance(scrollable_frame, tk.Frame):
            raise Exception("create_scrollable_frame did not return expected frame")
        # If the helper provided a canvas, try to find the internal canvas_window if needed later
        canvas_window = None
    except Exception:
        # Fallback: build our own canvas + scrollbar + scrollable_frame
        canvas = tk.Canvas(parent, bg=colors['bg_primary'], highlightthickness=0, borderwidth=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                                bg=colors['bg_secondary'],
                                troughcolor=colors['bg_primary'],
                                activebackground=colors['accent_cyan'])
        scrollable_frame = tk.Frame(canvas, bg=colors['bg_primary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Auto-resize canvas width to parent frame width on configure
        def _on_parent_resize(event):
            try:
                new_width = max(100, event.width - scrollbar.winfo_width() - 8)
                canvas.itemconfig(canvas_window, width=new_width)
                canvas.configure(width=new_width)
            except Exception:
                pass

        parent.bind("<Configure>", _on_parent_resize)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Ensure parent expands where possible
    try:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
    except Exception:
        pass

    # -------------------------
    # Cross-platform mousewheel
    # -------------------------
    def _on_mousewheel(event):
        """Scroll handler supporting Windows, macOS, and Linux."""
        try:
            # Linux: event.num == 4 (up), 5 (down)
            if hasattr(event, "num") and (event.num == 4 or event.num == 5):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                else:
                    canvas.yview_scroll(1, "units")
            else:
                # Windows and macOS: event.delta positive or negative
                # On Windows event.delta is multiples of 120; on macOS it can be various small values
                delta = 0
                try:
                    delta = int(event.delta / 120)
                except Exception:
                    # fallback if delta not divisible by 120 (macOS often)
                    delta = 1 if event.delta > 0 else -1
                if delta == 0:
                    delta = 1 if event.delta > 0 else -1
                # We negate delta so that positive wheel (away from user) scrolls down
                canvas.yview_scroll(-delta, "units")
        except Exception:
            # swallow any exceptions from event handling to avoid breaking UI
            return "break"

    def _bind_mousewheel(widget):
        """
        Bind enter/leave events on `widget` so that mousewheel events are only
        captured when pointer is over this widget. This avoids interfering with other widgets.
        """
        def _on_enter(e):
            if sys.platform.startswith("linux"):
                # X11 / many linux distros generate Button-4/5 for wheel
                widget.bind_all("<Button-4>", _on_mousewheel)
                widget.bind_all("<Button-5>", _on_mousewheel)
            else:
                # Windows & Mac use MouseWheel
                widget.bind_all("<MouseWheel>", _on_mousewheel)
                # Also try momentum events on some macOS builds:
                widget.bind_all("<Shift-MouseWheel>", _on_mousewheel)

        def _on_leave(e):
            try:
                if sys.platform.startswith("linux"):
                    widget.unbind_all("<Button-4>")
                    widget.unbind_all("<Button-5>")
                else:
                    widget.unbind_all("<MouseWheel>")
                    widget.unbind_all("<Shift-MouseWheel>")
            except Exception:
                pass

        widget.bind("<Enter>", _on_enter)
        widget.bind("<Leave>", _on_leave)

    # Bind to the scrollable_frame and canvas (if available) for reliability
    try:
        _bind_mousewheel(scrollable_frame)
        if canvas is not None:
            _bind_mousewheel(canvas)
    except Exception:
        pass

    # -------------------------
    # Build UI inside scrollable_frame
    # -------------------------

    header_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    header_frame.pack(fill='x', padx=15, pady=10)

    tk.Label(
        header_frame,
        text="🤖 AI-Driven Autonomous Security Analysis",
        font=('Segoe UI', 13, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(10, 3))

    tk.Label(
        header_frame,
        text="AI analyzes targets and generates custom testing strategies",
        font=('Segoe UI', 8),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(0, 10))

    # Target URL Section - RESPONSIVE
    url_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    url_frame.pack(fill='both', expand=True, padx=15, pady=(0, 10))

    tk.Label(
        url_frame,
        text="🎯 Target URL",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(10, 8))

    # Grid layout for responsive input
    url_input_container = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_input_container.pack(fill='x', padx=15, pady=(0, 10))
    url_input_container.grid_columnconfigure(0, weight=1)  # Entry expands
    url_input_container.grid_columnconfigure(1, weight=0)

    # Prepare vars on gui_instance
    gui_instance.ai_target_var = getattr(gui_instance, 'ai_target_var', tk.StringVar(value='https://testphp.vulnweb.com'))
    gui_instance.ai_nlp_query_var = getattr(gui_instance, 'ai_nlp_query_var', tk.StringVar())
    gui_instance.ai_depth_var = getattr(gui_instance, 'ai_depth_var', tk.StringVar(value='Standard'))
    gui_instance.ai_provider_var = getattr(gui_instance, 'ai_provider_var', tk.StringVar(value='Google Gemini'))

    url_entry = tk.Entry(
        url_input_container,
        textvariable=gui_instance.ai_target_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=0
    )
    url_entry.grid(row=0, column=0, sticky='ew', ipady=10, padx=(0, 10))

    # Start Analysis Button - responsive placement (no fixed width)
    start_btn = tk.Button(
        url_input_container,
        text="🚀 Start AI Analysis",
        font=('Segoe UI', 10, 'bold'),
        bg=colors['accent_cyan'],
        fg='#000000',
        activebackground=colors['accent_purple'],
        activeforeground='#ffffff',
        relief='flat',
        cursor='hand2',
        command=getattr(gui_instance, 'start_ai_analysis', lambda: None),
        padx=16,
        pady=8
    )
    start_btn.grid(row=0, column=1, sticky='e')

    # Natural Language Query Section
    nlp_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    nlp_frame.pack(fill='x', padx=15, pady=(0, 10))

    nlp_header = tk.Frame(nlp_frame, bg=colors['bg_secondary'])
    nlp_header.pack(fill='x', padx=15, pady=(10, 5))

    tk.Label(
        nlp_header,
        text="💬 Natural Language Query",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(side='left')

    tk.Label(
        nlp_header,
        text="(Optional)",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='left', padx=(5, 0))

    tk.Label(
        nlp_frame,
        text="Contoh: 'test keamanan databasenya' atau 'find SQL injection'",
        font=('Segoe UI', 8, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(0, 8))

    # Grid layout for responsive input
    nlp_input_container = tk.Frame(nlp_frame, bg=colors['bg_secondary'])
    nlp_input_container.pack(fill='x', padx=15, pady=(0, 8))
    nlp_input_container.grid_columnconfigure(0, weight=1)  # Input expands

    nlp_entry = tk.Entry(
        nlp_input_container,
        textvariable=gui_instance.ai_nlp_query_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=0
    )
    nlp_entry.grid(row=0, column=0, sticky='ew', ipady=10)

    # Quick example buttons
    examples_frame = tk.Frame(nlp_frame, bg=colors['bg_secondary'])
    examples_frame.pack(fill='x', padx=15, pady=(0, 10))

    tk.Label(
        examples_frame,
        text="Quick examples:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='left', padx=(0, 10))

    example_queries = [
        ("🗄️ Database", "test keamanan databasenya"),
        ("⚡ XSS", "cari celah XSS"),
        ("🔍 Full Scan", "scan semua kerentanan")
    ]

    for label, query in example_queries:
        btn = tk.Button(
            examples_frame,
            text=label,
            font=('Segoe UI', 9),
            bg=colors['bg_tertiary'],
            fg=colors['accent_cyan'],
            activebackground=colors['accent_purple'],
            activeforeground='#ffffff',
            relief='flat',
            cursor='hand2',
            command=lambda q=query: gui_instance.ai_nlp_query_var.set(q),
            padx=12,
            pady=6
        )
        btn.pack(side='left', padx=5)

    # AI Configuration Section - RESPONSIVE GRID LAYOUT
    config_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    config_frame.pack(fill='x', padx=15, pady=(0, 10))

    tk.Label(
        config_frame,
        text="⚙️ AI Configuration",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(10, 8))

    # Grid container for responsive layout
    config_container = tk.Frame(config_frame, bg=colors['bg_secondary'])
    config_container.pack(fill='both', expand=True, padx=15, pady=(0, 10))

    # Configure grid weights for responsive resizing (two columns share space)
    config_container.grid_columnconfigure(0, weight=1, uniform='cfg')
    config_container.grid_columnconfigure(1, weight=1, uniform='cfg')

    # Left column - Analysis Depth
    tk.Label(
        config_container,
        text="Analysis Depth:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).grid(row=0, column=0, sticky='w', pady=(0, 5), padx=(0, 10))

    depth_options = ['Quick', 'Standard', 'Deep', 'Comprehensive']

    depth_frame = tk.Frame(config_container, bg=colors['bg_tertiary'], relief='flat', bd=1)
    depth_frame.grid(row=1, column=0, sticky='ew', pady=(0, 5), padx=(0, 10))

    depth_combo = ttk.Combobox(
        depth_frame,
        textvariable=gui_instance.ai_depth_var,
        values=depth_options,
        state='readonly',
        font=('Segoe UI', 9)
    )
    depth_combo.pack(fill='x', padx=5, pady=5)

    # Right column - AI Provider
    tk.Label(
        config_container,
        text="AI Model Provider:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).grid(row=0, column=1, sticky='w', pady=(0, 5), padx=(10, 0))

    provider_options = ['OpenAI GPT-4', 'Google Gemini', 'Anthropic Claude']

    provider_frame = tk.Frame(config_container, bg=colors['bg_tertiary'], relief='flat', bd=1)
    provider_frame.grid(row=1, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))

    provider_combo = ttk.Combobox(
        provider_frame,
        textvariable=gui_instance.ai_provider_var,
        values=provider_options,
        state='readonly',
        font=('Segoe UI', 9)
    )
    provider_combo.pack(fill='x', padx=5, pady=5)

    # Progress Section
    progress_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    progress_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    tk.Label(
        progress_frame,
        text="📊 Analysis Progress",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(15, 10))

    # Steps container with styled scroll - RESPONSIVE
    steps_canvas = tk.Canvas(
        progress_frame,
        bg=colors['bg_tertiary'],
        highlightthickness=0,
        borderwidth=0
    )
    steps_scroll = tk.Scrollbar(
        progress_frame,
        orient="vertical",
        command=steps_canvas.yview,
        bg=colors['bg_secondary'],
        troughcolor=colors['bg_primary'],
        activebackground=colors['accent_cyan']
    )
    gui_instance.ai_steps_frame = tk.Frame(steps_canvas, bg=colors['bg_tertiary'])

    gui_instance.ai_steps_frame.bind(
        "<Configure>",
        lambda e: steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))
    )

    steps_canvas_window = steps_canvas.create_window((0, 0), window=gui_instance.ai_steps_frame, anchor="nw")

    def _configure_steps_canvas_width(event):
        try:
            steps_canvas.itemconfig(steps_canvas_window, width=max(100, event.width - 8))
        except Exception:
            pass

    steps_canvas.bind('<Configure>', _configure_steps_canvas_width)
    steps_canvas.configure(yscrollcommand=steps_scroll.set)

    steps_canvas.config(height=200)

    steps_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
    steps_scroll.pack(side="right", fill="y", pady=(0, 15), padx=(0, 20))

    # Initial placeholder
    tk.Label(
        gui_instance.ai_steps_frame,
        text="No analysis started. Enter a URL above and click 'Start AI Analysis'",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary']
    ).pack(padx=15, pady=30)

    # Action buttons row
    analyze_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'])
    analyze_frame.pack(fill='x', padx=10, pady=12)

    analyze_btn = tk.Button(
        analyze_frame,
        text="🤖 Analyze with AI",
        font=('Segoe UI', 12, 'bold'),
        bg=colors['accent_cyan'],
        fg=colors['bg_primary'],
        activebackground=colors['accent_purple'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.start_ai_analysis,
        padx=20,
        pady=10
    )
    analyze_btn.pack(side='left', padx=5)

    download_btn = tk.Button(
        analyze_frame,
        text="📥 Download Report",
        font=('Segoe UI', 12, 'bold'),
        bg=colors['accent_purple'],
        fg='#ffffff',
        activebackground=colors['accent_cyan'],
        activeforeground='#000000',
        relief='flat',
        cursor='hand2',
        command=getattr(gui_instance, 'download_ai_results', lambda: None),
        padx=20,
        pady=10
    )
    download_btn.pack(side='left', padx=5)

    gui_instance.resume_scan_btn_ai = tk.Button(
        analyze_frame,
        text="▶️ Resume Scan",
        font=('Segoe UI', 12, 'bold'),
        bg=colors['success'],
        fg=colors['bg_primary'],
        activebackground=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.resume_scan,
        padx=20,
        pady=10,
        state='disabled'
    )
    # Don't pack initially - shown by pause_scan()

    # RESULT SECTION 1: AI Text Analysis
    # ═══════════════════════════════════════════════════════════
    result1_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    result1_frame.pack(fill='x', padx=20, pady=(0, 10))

    result1_header = tk.Frame(result1_frame, bg=colors['bg_secondary'])
    result1_header.pack(fill='x', padx=20, pady=(15, 5))

    tk.Label(
        result1_header,
        text="① 📋 Hasil Analisis AI",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(side='left')

    tk.Label(
        result1_header,
        text="Recon • Vulnerability • Recommendations",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='right')

    gui_instance.ai_reasoning_text = tk.Text(
        result1_frame,
        height=18,
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        wrap='word',
        state='disabled',
        padx=10,
        pady=10
    )
    gui_instance.ai_reasoning_text.pack(fill='x', padx=20, pady=(5, 15))

    # ═══════════════════════════════════════════════════════════
    # RESULT SECTION 2: Executable Protocols
    # ═══════════════════════════════════════════════════════════
    exec_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    exec_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))

    exec_header = tk.Frame(exec_frame, bg=colors['bg_secondary'])
    exec_header.pack(fill='x', padx=20, pady=(15, 5))

    tk.Label(
        exec_header,
        text="② ⚡ Protokol Eksekusi Sistem",
        font=('Segoe UI', 12, 'bold'),
        fg='#f59e0b',
        bg=colors['bg_secondary']
    ).pack(side='left')

    # Execute All button
    exec_all_btn = tk.Button(
        exec_header,
        text="▶ Execute All Steps",
        font=('Segoe UI', 9, 'bold'),
        bg=colors['success'],
        fg='#000000',
        activebackground=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=getattr(gui_instance, 'ai_run_all_exec_steps', lambda: None),
        padx=12,
        pady=4
    )
    exec_all_btn.pack(side='right', padx=(5, 0))

    exec_desc = tk.Label(
        exec_frame,
        text="Test protokol yang di-generate AI — dapat dijalankan langsung ke target",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    exec_desc.pack(anchor='w', padx=20, pady=(0, 2))

    # Status label
    gui_instance.ai_exec_status_label = tk.Label(
        exec_frame,
        text="Jalankan AI Analysis terlebih dahulu untuk generate test steps",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.ai_exec_status_label.pack(anchor='w', padx=20, pady=(0, 5))

    # Scrollable exec steps container
    exec_canvas = tk.Canvas(exec_frame, bg=colors['bg_tertiary'], highlightthickness=0, borderwidth=0, height=280)
    exec_scrollbar = tk.Scrollbar(exec_frame, orient="vertical", command=exec_canvas.yview,
                                   bg=colors['bg_secondary'], troughcolor=colors['bg_primary'],
                                   activebackground=colors['accent_cyan'])
    gui_instance.ai_exec_steps_frame = tk.Frame(exec_canvas, bg=colors['bg_tertiary'])

    gui_instance.ai_exec_steps_frame.bind(
        "<Configure>",
        lambda e: exec_canvas.configure(scrollregion=exec_canvas.bbox("all"))
    )

    exec_canvas_window = exec_canvas.create_window((0, 0), window=gui_instance.ai_exec_steps_frame, anchor="nw")

    def _configure_exec_canvas(event):
        try:
            exec_canvas.itemconfig(exec_canvas_window, width=max(100, event.width - 8))
        except Exception:
            pass

    exec_canvas.bind('<Configure>', _configure_exec_canvas)
    exec_canvas.configure(yscrollcommand=exec_scrollbar.set)

    exec_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
    exec_scrollbar.pack(side="right", fill="y", pady=(0, 15), padx=(0, 20))

    try:
        _bind_mousewheel(exec_canvas)
    except Exception:
        pass

    # Initialize exec state
    gui_instance.ai_exec_step_data = []
    gui_instance.ai_exec_step_widgets = []

    # Live Console
    console_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    console_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    console_header = tk.Frame(console_frame, bg=colors['bg_secondary'])
    console_header.pack(fill='x', padx=20, pady=(15, 10))

    tk.Label(
        console_header,
        text="📄 Live Console",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(side='left')

    clear_console_btn = tk.Button(
        console_header,
        text="🗑️ Clear",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_secondary'],
        activebackground=colors['error'],
        activeforeground='#ffffff',
        relief='flat',
        cursor='hand2',
        command=lambda: gui_instance.ai_console_text.delete('1.0', tk.END),
        padx=12,
        pady=4
    )
    clear_console_btn.pack(side='right')

    gui_instance.ai_console_text = scrolledtext.ScrolledText(
        console_frame,
        height=15,
        font=('Consolas', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        wrap='word',
        state='disabled'
    )
    gui_instance.ai_console_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    # ─── Tool Manager Section ───────────────────────────────────
    tools_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    tools_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    tools_header = tk.Frame(tools_frame, bg=colors['bg_secondary'])
    tools_header.pack(fill='x', padx=20, pady=(15, 10))

    tk.Label(
        tools_header,
        text="🔧 Security Tools Manager",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(side='left')

    # Scan tools button
    scan_tools_btn = tk.Button(
        tools_header,
        text="🔍 Detect Tools",
        font=('Segoe UI', 9, 'bold'),
        bg=colors['accent_cyan'],
        fg='#000000',
        activebackground=colors['accent_purple'],
        relief='flat',
        cursor='hand2',
        command=getattr(gui_instance, 'scan_installed_tools', lambda: None),
        padx=10,
        pady=3
    )
    scan_tools_btn.pack(side='right', padx=(5, 0))

    # Install All Missing button
    install_all_btn = tk.Button(
        tools_header,
        text="📦 Install All Missing",
        font=('Segoe UI', 9, 'bold'),
        bg=colors['success'],
        fg='#000000',
        activebackground=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=getattr(gui_instance, 'install_all_missing_tools', lambda: None),
        padx=10,
        pady=3
    )
    install_all_btn.pack(side='right', padx=(5, 0))

    gui_instance.tools_status_label = tk.Label(
        tools_frame,
        text="Click 'Detect Tools' to scan installed security tools",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.tools_status_label.pack(anchor='w', padx=20, pady=(0, 5))

    # Tools grid canvas
    tools_canvas = tk.Canvas(tools_frame, bg=colors['bg_tertiary'], highlightthickness=0,
                              borderwidth=0, height=200)
    tools_scrollbar = tk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview,
                                    bg=colors['bg_secondary'], troughcolor=colors['bg_primary'],
                                    activebackground=colors['accent_cyan'])
    gui_instance.tools_list_frame = tk.Frame(tools_canvas, bg=colors['bg_tertiary'])

    gui_instance.tools_list_frame.bind(
        "<Configure>",
        lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
    )

    tools_canvas_window = tools_canvas.create_window((0, 0), window=gui_instance.tools_list_frame, anchor="nw")

    def _configure_tools_canvas(event):
        try:
            tools_canvas.itemconfig(tools_canvas_window, width=max(100, event.width - 8))
        except Exception:
            pass

    tools_canvas.bind('<Configure>', _configure_tools_canvas)
    tools_canvas.configure(yscrollcommand=tools_scrollbar.set)

    tools_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
    tools_scrollbar.pack(side="right", fill="y", pady=(0, 15), padx=(0, 20))

    try:
        _bind_mousewheel(tools_canvas)
    except Exception:
        pass

    # Initialize states
    gui_instance.ai_analysis_running = False
    gui_instance.ai_step_widgets = []
    gui_instance.tool_widgets = {}
