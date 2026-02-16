"""AI Analysis tab setup - AI-driven autonomous security analysis"""

import tkinter as tk
from tkinter import ttk, scrolledtext


def setup_ai_analysis_tab(parent, gui_instance):
    """
    Setup AI-driven autonomous security analysis tab
    
    Args:
        parent: Parent frame for this tab
        gui_instance: Reference to main EMYUELGUI instance for colors and callbacks
    """
    colors = gui_instance.colors
   
    # Scrollable container
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
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Header
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
    
    # Target URL Section
    url_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    url_frame.pack(fill='x', padx=15, pady=(0, 10))
    
    tk.Label(
        url_frame,
        text="🎯 Target URL",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(10, 8))
    
    url_input_frame = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_input_frame.pack(fill='x', padx=15, pady=(0, 10))
    
    gui_instance.ai_target_var = tk.StringVar(value='https://testphp.vulnweb.com')
    
    url_entry = tk.Entry(
        url_input_frame,
        textvariable=gui_instance.ai_target_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=0
    )
    url_entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(0, 10))
    
    # Start Analysis Button
    start_btn = tk.Button(
        url_input_frame,
        text="🚀 Start AI Analysis",
        font=('Segoe UI', 10, 'bold'),
        bg=colors['accent_cyan'],
        fg='#000000',
        activebackground=colors['accent_purple'],
        activeforeground='#ffffff',
        relief='flat',
        cursor='hand2',
        command=gui_instance.start_ai_analysis,
        padx=25,
        pady=10
    )
    start_btn.pack(side='right')
    
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
    
    nlp_input_frame = tk.Frame(nlp_frame, bg=colors['bg_secondary'])
    nlp_input_frame.pack(fill='x', padx=15, pady=(0, 8))
    
    gui_instance.ai_nlp_query_var = tk.StringVar()
    
    nlp_entry = tk.Entry(
        nlp_input_frame,
        textvariable=gui_instance.ai_nlp_query_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=0
    )
    nlp_entry.pack(fill='x', ipady=10)
    
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
    
    # AI Configuration Section
    config_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    config_frame.pack(fill='x', padx=15, pady=(0, 10))
    
    tk.Label(
        config_frame,
        text="⚙️ AI Configuration",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=15, pady=(10, 8))
    
    # Two-column layout
    config_container = tk.Frame(config_frame, bg=colors['bg_secondary'])
    config_container.pack(fill='x', padx=15, pady=(0, 10))
    
    # Left column - Analysis Depth
    left_col = tk.Frame(config_container, bg=colors['bg_secondary'])
    left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    tk.Label(
        left_col,
        text="Analysis Depth:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', pady=(0, 5))
    
    depth_options = ['Quick', 'Standard', 'Deep', 'Comprehensive']
    gui_instance.ai_depth_var = tk.StringVar(value='Standard')
    
    depth_frame = tk.Frame(left_col, bg=colors['bg_tertiary'], relief='flat', bd=1)
    depth_frame.pack(fill='x', pady=(0, 5))
    
    depth_combo = ttk.Combobox(
        depth_frame,
        textvariable=gui_instance.ai_depth_var,
        values=depth_options,
        state='readonly',
        font=('Segoe UI', 9),
        width=25
    )
    depth_combo.pack(padx=5, pady=5)
    
    # Right column - AI Provider
    right_col = tk.Frame(config_container, bg=colors['bg_secondary'])
    right_col.pack(side='left', fill='both', expand=True, padx=(10, 0))
    
    tk.Label(
        right_col,
        text="AI Model Provider:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', pady=(0, 5))
    
    provider_options = ['OpenAI GPT-4', 'Google Gemini', 'Anthropic Claude']
    gui_instance.ai_provider_var = tk.StringVar(value='OpenAI GPT-4')
    
    provider_frame = tk.Frame(right_col, bg=colors['bg_tertiary'], relief='flat', bd=1)
    provider_frame.pack(fill='x', pady=(0, 5))
    
    provider_combo = ttk.Combobox(
        provider_frame,
        textvariable=gui_instance.ai_provider_var,
        values=provider_options,
        state='readonly',
        font=('Segoe UI', 9),
        width=25
    )
    provider_combo.pack(padx=5, pady=5)
    
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
    
    # Steps container with styled scroll
    steps_canvas = tk.Canvas(
        progress_frame, 
        bg=colors['bg_tertiary'], 
        height=250, 
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
    
    steps_canvas.create_window((0, 0), window=gui_instance.ai_steps_frame, anchor="nw", width=700)
    steps_canvas.configure(yscrollcommand=steps_scroll.set)
    
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
    
    # AI Reasoning Section
    reasoning_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    reasoning_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    reasoning_header = tk.Frame(reasoning_frame, bg=colors['bg_secondary'])
    reasoning_header.pack(fill='x', padx=20, pady=(15, 10))
    
    tk.Label(
        reasoning_header,
        text="🧠 AI Reasoning",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(side='left')
    
    tk.Label(
        reasoning_header,
        text="AI's thought process and decision making",
        font=('Segoe UI', 8, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='left', padx=(10, 0))
    
    gui_instance.ai_reasoning_text = tk.Text(
        reasoning_frame,
        height=5,
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
    gui_instance.ai_reasoning_text.pack(fill='x', padx=20, pady=(0, 15))
    
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
    
    # Clear button
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
        height=10,
        font=('Consolas', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        wrap='word',
        state='disabled'
    )
    gui_instance.ai_console_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    # Initialize AI analysis state
    gui_instance.ai_analysis_running = False
    gui_instance.ai_step_widgets = []
