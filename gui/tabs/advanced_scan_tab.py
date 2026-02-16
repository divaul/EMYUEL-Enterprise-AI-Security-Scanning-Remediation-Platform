"""
Advanced Scan Tab - GUI Module (responsive)
Module for advanced security scanning configuration with detailed options
"""

import tkinter as tk
from tkinter import ttk


def setup_advanced_tab(parent, gui_instance):
    """Setup advanced scan configuration tab (responsive-friendly)"""
    colors = gui_instance.colors

    # Create scrollable container (uses helper from main GUI)
    try:
        scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    except Exception:
        # fallback: create simple frame if helper not available
        scrollable_frame = tk.Frame(parent, bg=colors['bg_primary'])
        scrollable_frame.pack(fill='both', expand=True)
        canvas = None

    # Make parent/grid responsive where possible
    try:
        scrollable_frame.grid_columnconfigure(0, weight=1)
    except Exception:
        pass

    # ---------- Target selection ----------
    target_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=0)
    target_frame.pack(fill='x', padx=20, pady=16)

    target_label = tk.Label(
        target_frame,
        text="🎯 Scan Target",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    target_label.pack(anchor='w', padx=6, pady=(6, 4))

    target_hint = tk.Label(
        target_frame,
        text="Enter URL (https://...) or local directory path",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    target_hint.pack(anchor='w', padx=6, pady=(0, 8))

    target_input_frame = tk.Frame(target_frame, bg=colors['bg_secondary'])
    target_input_frame.pack(fill='x', padx=6)

    # Use grid so entry expands and button stays to the right
    target_input_frame.grid_columnconfigure(0, weight=1)
    target_input_frame.grid_columnconfigure(1, weight=0)

    gui_instance.target_entry = tk.Entry(
        target_input_frame,
        textvariable=gui_instance.target_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief='flat',
        bd=8
    )
    gui_instance.target_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8), pady=4)

    # Add placeholder behavior
    if not gui_instance.target_var.get():
        gui_instance.target_entry.insert(0, "https://example.com or /path/to/directory")
        gui_instance.target_entry.config(fg=colors['text_secondary'])

    gui_instance.target_entry.bind('<FocusIn>', gui_instance.on_target_focus_in)
    gui_instance.target_entry.bind('<FocusOut>', gui_instance.on_target_focus_out)

    browse_btn = tk.Button(
        target_input_frame,
        text="📁 Browse",
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.browse_target,
        padx=12,
        pady=8
    )
    browse_btn.grid(row=0, column=1, sticky='e')

    # Quick actions
    quick_actions_frame = tk.Frame(target_frame, bg=colors['bg_secondary'])
    quick_actions_frame.pack(fill='x', padx=6, pady=(10, 0))

    scan_all_btn = tk.Button(
        quick_actions_frame,
        text="🌐 Scan All (Full Website/Directory)",
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.set_scan_all_mode,
        padx=12,
        pady=8
    )
    scan_all_btn.pack(side='left')

    gui_instance.target_type_label = tk.Label(
        quick_actions_frame,
        text="",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.target_type_label.pack(side='left', padx=(12, 0))

    # ---------- Scan options (responsive grid) ----------
    options_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=0)
    options_frame.pack(fill='x', padx=20, pady=(10, 18))

    options_label = tk.Label(
        options_frame,
        text="⚙ Scan Configuration",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    options_label.pack(anchor='w', padx=6, pady=(6, 12))

    # Use a grid container for provider/profile/mode so columns share space
    cfg_container = tk.Frame(options_frame, bg=colors['bg_secondary'])
    cfg_container.pack(fill='x', padx=6)
    cfg_container.grid_columnconfigure(0, weight=1, uniform='cfg')
    cfg_container.grid_columnconfigure(1, weight=1, uniform='cfg')

    # Left column: Provider & Profile
    left_col = tk.Frame(cfg_container, bg=colors['bg_secondary'])
    left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

    # Right column: Mode & advanced toggles
    right_col = tk.Frame(cfg_container, bg=colors['bg_secondary'])
    right_col.grid(row=0, column=1, sticky='nsew', padx=(8, 0))

    # Provider selection (left_col)
    provider_label = tk.Label(
        left_col,
        text="LLM Provider:",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    provider_label.pack(anchor='w', pady=(0, 6))

    provider_frame = tk.Frame(left_col, bg=colors['bg_secondary'])
    provider_frame.pack(fill='x')

    providers = ['openai', 'gemini', 'claude']
    # make radiobuttons wrap if needed by using pack in row
    for provider in providers:
        rb = tk.Radiobutton(
            provider_frame,
            text=provider.capitalize(),
            variable=gui_instance.provider_var,
            value=provider,
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan']
        )
        rb.pack(side='left', padx=(0, 8), pady=4)

    # Profile selection (left_col)
    profile_label = tk.Label(
        left_col,
        text="Scan Profile:",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    profile_label.pack(anchor='w', pady=(12, 6))

    profile_frame = tk.Frame(left_col, bg=colors['bg_secondary'])
    profile_frame.pack(fill='x')

    profiles = ['quick', 'standard', 'comprehensive']
    for profile in profiles:
        rb = tk.Radiobutton(
            profile_frame,
            text=profile.capitalize(),
            variable=gui_instance.profile_var,
            value=profile,
            font=('Segoe UI', 10),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan']
        )
        rb.pack(side='left', padx=(0, 8), pady=4)

    # Mode selection (right_col)
    mode_label = tk.Label(
        right_col,
        text="Scan Mode:",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    mode_label.pack(anchor='w', pady=(0, 6))

    mode_frame = tk.Frame(right_col, bg=colors['bg_secondary'])
    mode_frame.pack(fill='x')

    tk.Radiobutton(
        mode_frame,
        text="Full Scan (All Modules)",
        variable=gui_instance.scan_mode_var,
        value="full",
        font=('Segoe UI', 10),
        bg=colors['bg_secondary'],
        fg=colors['text_primary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary'],
        activeforeground=colors['accent_cyan']
    ).pack(side='left', padx=(0, 8), pady=4)

    tk.Radiobutton(
        mode_frame,
        text="Targeted Scan",
        variable=gui_instance.scan_mode_var,
        value="targeted",
        font=('Segoe UI', 10),
        bg=colors['bg_secondary'],
        fg=colors['text_primary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary'],
        activeforeground=colors['accent_cyan']
    ).pack(side='left', padx=(0, 8), pady=4)

    # Advanced toggles area (right_col)
    adv_label = tk.Label(
        right_col,
        text="Advanced Options:",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    adv_label.pack(anchor='w', pady=(12, 6))

    adv_frame = tk.Frame(right_col, bg=colors['bg_secondary'])
    adv_frame.pack(fill='x')

    # Example advanced options as checkboxes
    gui_instance.opt_recursive_var = tk.BooleanVar(value=True)
    gui_instance.opt_follow_links_var = tk.BooleanVar(value=False)
    gui_instance.opt_bypass_waf_var = tk.BooleanVar(value=False)

    tk.Checkbutton(
        adv_frame, text="Recursive Crawling", variable=gui_instance.opt_recursive_var,
        bg=colors['bg_secondary'], fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary']
    ).pack(anchor='w', pady=2)

    tk.Checkbutton(
        adv_frame, text="Follow Links", variable=gui_instance.opt_follow_links_var,
        bg=colors['bg_secondary'], fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary']
    ).pack(anchor='w', pady=2)

    tk.Checkbutton(
        adv_frame, text="Attempt WAF Bypass (risky)", variable=gui_instance.opt_bypass_waf_var,
        bg=colors['bg_secondary'], fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary']
    ).pack(anchor='w', pady=2)

    # ---------- Control buttons (responsive) ----------
    control_frame = tk.Frame(scrollable_frame, bg=colors['bg_primary'])
    control_frame.pack(fill='x', padx=20, pady=18)

    # Use grid so left and right actions share the row
    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(1, weight=0)

    actions_left = tk.Frame(control_frame, bg=colors['bg_primary'])
    actions_left.grid(row=0, column=0, sticky='w')

    actions_right = tk.Frame(control_frame, bg=colors['bg_primary'])
    actions_right.grid(row=0, column=1, sticky='e')

    gui_instance.start_btn = tk.Button(
        actions_left,
        text="▶ Start Scan",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['success'],
        fg='white',
        relief='flat',
        cursor='hand2',
        command=gui_instance.start_advanced_scan,
        padx=14,
        pady=10
    )
    gui_instance.start_btn.pack(side='left', padx=(0, 8))

    gui_instance.pause_btn = tk.Button(
        actions_left,
        text="⏸ Pause",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['warning'],
        fg='white',
        relief='flat',
        cursor='hand2',
        command=gui_instance.pause_scan,
        padx=14,
        pady=10,
        state='disabled'
    )
    gui_instance.pause_btn.pack(side='left', padx=(0, 8))

    gui_instance.report_btn = tk.Button(
        actions_right,
        text="📊 Generate Report",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['accent_purple'],
        fg='white',
        relief='flat',
        cursor='hand2',
        command=gui_instance.generate_report,
        padx=14,
        pady=10
    )
    gui_instance.report_btn.pack(side='right')

    # Ensure scrollable canvas updates on size changes (helps responsiveness)
    if canvas is not None:
        def _on_parent_resize(event):
            try:
                canvas.configure(width=event.width)
            except Exception:
                pass
        parent.bind("<Configure>", _on_parent_resize)

    # A small hint area at bottom
    hint_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'])
    hint_frame.pack(fill='x', padx=20, pady=(0, 26))

    hint_label = tk.Label(
        hint_frame,
        text="Tip: Gunakan 'Targeted Scan' untuk menguji endpoint tertentu, dan 'Full Scan' untuk analisa menyeluruh.",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        wraplength=900,
        justify='left'
    )
    hint_label.pack(anchor='w')
