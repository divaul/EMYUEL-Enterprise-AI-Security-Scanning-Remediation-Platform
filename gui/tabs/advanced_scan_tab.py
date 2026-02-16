"""
Advanced Scan Tab - GUI Module
Module for advanced security scanning configuration with detailed options
"""

import tkinter as tk


def setup_advanced_tab(parent, gui_instance):
    """Setup advanced scan configuration tab"""
    colors = gui_instance.colors
    
    # Create scrollable container
    scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    
    # Target selection
    target_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    target_frame.pack(fill='x', padx=20, pady=20)
    
    target_label = tk.Label(
        target_frame,
        text="🎯 Scan Target",
        font=('Arial', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    target_label.pack(anchor='w', padx=20, pady=(15, 5))
    
    target_hint = tk.Label(
        target_frame,
        text="Enter URL (https://...) or local directory path",
        font=('Arial', 8),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    target_hint.pack(anchor='w', padx=20, pady=(0, 10))
    
    target_input_frame = tk.Frame(target_frame, bg=colors['bg_secondary'])
    target_input_frame.pack(fill='x', padx=20, pady=(0, 10))
    
    gui_instance.target_entry = tk.Entry(
        target_input_frame,
        textvariable=gui_instance.target_var,
        font=('Arial', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief='flat',
        bd=10
    )
    gui_instance.target_entry.pack(fill='x', side='left', expand=True)
    
    # Add placeholder
    gui_instance.target_entry.insert(0, "https://example.com or /path/to/directory")
    gui_instance.target_entry.config(fg=colors['text_secondary'])
    gui_instance.target_entry.bind('<FocusIn>', gui_instance.on_target_focus_in)
    gui_instance.target_entry.bind('<FocusOut>', gui_instance.on_target_focus_out)
    
    browse_btn = tk.Button(
        target_input_frame,
        text="📁 Browse",
        font=('Arial', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.browse_target,
        padx=20,
        pady=8
    )
    browse_btn.pack(side='right', padx=(10, 0))
    
    # Quick actions
    quick_actions_frame = tk.Frame(target_frame, bg=colors['bg_secondary'])
    quick_actions_frame.pack(fill='x', padx=20, pady=(0, 15))
    
    scan_all_btn = tk.Button(
        quick_actions_frame,
        text="🌐 Scan All (Full Website/Directory)",
        font=('Arial', 9),
        bg=colors['bg_tertiary'],
        fg=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.set_scan_all_mode,
        padx=15,
        pady=8
    )
    scan_all_btn.pack(side='left', padx=(0, 10))
    
    gui_instance.target_type_label = tk.Label(
        quick_actions_frame,
        text="",
        font=('Arial', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.target_type_label.pack(side='left', padx=10)
    
    # Scan options
    options_frame = tk.Frame(parent, bg=colors['bg_secondary'], relief='flat', bd=2)
    options_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    options_label = tk.Label(
        options_frame,
        text="⚙ Scan Configuration",
        font=('Arial', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    options_label.pack(anchor='w', padx=20, pady=(15, 15))
    
    # Provider selection
    provider_frame = tk.Frame(options_frame, bg=colors['bg_secondary'])
    provider_frame.pack(fill='x', padx=40, pady=5)
    
    provider_label = tk.Label(
        provider_frame,
        text="LLM Provider:",
        font=('Arial', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        width=15,
        anchor='w'
    )
    provider_label.pack(side='left')
    
    providers = ['openai', 'gemini', 'claude']
    for provider in providers:
        rb = tk.Radiobutton(
            provider_frame,
            text=provider.capitalize(),
            variable=gui_instance.provider_var,
            value=provider,
            font=('Arial', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan']
        )
        rb.pack(side='left', padx=10)
    
    # Profile selection
    profile_frame = tk.Frame(options_frame, bg=colors['bg_secondary'])
    profile_frame.pack(fill='x', padx=40, pady=5)
    
    profile_label = tk.Label(
        profile_frame,
        text="Scan Profile:",
        font=('Arial', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        width=15,
        anchor='w'
    )
    profile_label.pack(side='left')
    
    profiles = ['quick', 'standard', 'comprehensive']
    for profile in profiles:
        rb = tk.Radiobutton(
            profile_frame,
            text=profile.capitalize(),
            variable=gui_instance.profile_var,
            value=profile,
            font=('Arial', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan']
        )
        rb.pack(side='left', padx=10)
    
    # Scan mode
    mode_frame = tk.Frame(options_frame, bg=colors['bg_secondary'])
    mode_frame.pack(fill='x', padx=40, pady=(5, 15))
    
    mode_label = tk.Label(
        mode_frame,
        text="Scan Mode:",
        font=('Arial', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        width=15,
        anchor='w'
    )
    mode_label.pack(side='left')
    
    tk.Radiobutton(
        mode_frame,
        text="Full Scan (All Modules)",
        variable=gui_instance.scan_mode_var,
        value="full",
        font=('Arial', 10),
        bg=colors['bg_secondary'],
        fg=colors['text_primary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary'],
        activeforeground=colors['accent_cyan']
    ).pack(side='left', padx=10)
    
    tk.Radiobutton(
        mode_frame,
        text="Targeted Scan",
        variable=gui_instance.scan_mode_var,
        value="targeted",
        font=('Arial', 10),
        bg=colors['bg_secondary'],
        fg=colors['text_primary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary'],
        activeforeground=colors['accent_cyan']
    ).pack(side='left', padx=10)
    
    # Control buttons
    control_frame = tk.Frame(parent, bg=colors['bg_primary'])
    control_frame.pack(fill='x', padx=20, pady=20)
    
    gui_instance.start_btn = tk.Button(
        control_frame,
        text="▶ Start Scan",
        font=('Arial', 12, 'bold'),
        bg=colors['success'],
        fg='white',
        activebackground='#059669',
        relief='flat',
        cursor='hand2',
        command=gui_instance.start_advanced_scan,
        padx=30,
        pady=12
    )
    gui_instance.start_btn.pack(side='left', padx=5)
    
    gui_instance.pause_btn = tk.Button(
        control_frame,
        text="⏸ Pause",
        font=('Arial', 12, 'bold'),
        bg=colors['warning'],
        fg='white',
        relief='flat',
        cursor='hand2',
        command=gui_instance.pause_scan,
        padx=30,
        pady=12,
        state='disabled'
    )
    gui_instance.pause_btn.pack(side='left', padx=5)
    
    gui_instance.report_btn = tk.Button(
        control_frame,
        text="📊 Generate Report",
        font=('Arial', 12, 'bold'),
        bg=colors['accent_purple'],
        fg='white',
        relief='flat',
        cursor='hand2',
        command=gui_instance.generate_report,
        padx=30,
        pady=12
    )
    gui_instance.report_btn.pack(side='right', padx=5)
