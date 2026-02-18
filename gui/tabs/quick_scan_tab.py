"""
Quick Scan Tab - GUI Module (responsive)
Module for quick security scanning with website URL input and natural language queries
"""

import tkinter as tk
from tkinter import scrolledtext


def setup_quick_scan_tab(parent, gui_instance):
    """Setup quick scan tab with website URL input and natural language query (responsive)"""
    colors = gui_instance.colors

    # Create scrollable container (uses helper from main GUI - same as other tabs)
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

    # -------------------------
    # Build UI inside scrollable_frame
    # -------------------------

    # --- Website URL Section (responsive) ---
    url_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    url_frame.pack(fill='x', padx=20, pady=20)

    url_title = tk.Label(
        url_frame,
        text="🌐 Website URL Scanner",
        font=('Segoe UI', 14, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    url_title.pack(anchor='w', padx=10, pady=(10, 8))

    url_subtitle = tk.Label(
        url_frame,
        text="Enter a website URL to scan for security vulnerabilities",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    url_subtitle.pack(anchor='w', padx=10, pady=(0, 12))

    # URL input with scan button — use grid so entry expands
    url_input_frame = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_input_frame.pack(fill='x', padx=10, pady=(0, 10))
    url_input_frame.grid_columnconfigure(0, weight=1)

    gui_instance.url_entry = tk.Entry(
        url_input_frame,
        textvariable=gui_instance.target_var,
        font=('Segoe UI', 12),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=8
    )
    gui_instance.url_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10), pady=4)
    gui_instance.url_entry.bind('<Return>', lambda e: gui_instance.quick_scan_url())

    # placeholder & focus behavior
    if not gui_instance.target_var.get():
        try:
            gui_instance.url_entry.insert(0, 'https://example.com')
            gui_instance.url_entry.config(fg=colors['text_secondary'])
        except Exception:
            pass
    gui_instance.url_entry.bind('<FocusIn>', gui_instance.on_url_focus_in)
    gui_instance.url_entry.bind('<FocusOut>', gui_instance.on_url_focus_out)

    # Quick Scan button — no fixed width, placed in column 1
    quick_scan_btn = tk.Button(
        url_input_frame,
        text="⚡ Quick Scan",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['accent_cyan'],
        fg=colors['bg_primary'],
        activebackground=colors['accent_purple'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.quick_scan_url,
        padx=16,
        pady=8
    )
    quick_scan_btn.grid(row=0, column=1, sticky='e')
    
    # Resume Scan button (hidden by default, shown when paused)
    gui_instance.resume_scan_btn_quick = tk.Button(
        url_input_frame,
        text="▶️ Resume Scan",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['success'],
        fg=colors['bg_primary'],
        activebackground=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.resume_scan,
        padx=16,
        pady=8,
        state='disabled'  # Initially disabled
    )
    gui_instance.resume_scan_btn_quick.grid(row=0, column=2, sticky='e', padx=(5, 0))
    gui_instance.resume_scan_btn_quick.grid_remove()  # Hide initially
    
    # URL Examples — flow-friendly (wrap as space allows)
    url_examples_label = tk.Label(
        url_frame,
        text="Quick Examples:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    url_examples_label.pack(anchor='w', padx=10, pady=(8, 6))

    url_ex_container = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_ex_container.pack(fill='x', padx=12, pady=(0, 10))
    url_ex_container.grid_columnconfigure(0, weight=1)

    url_examples = [
        "https://example.com",
        "https://testphp.vulnweb.com",
        "http://demo.testfire.net"
    ]

    for i, url_example in enumerate(url_examples):
        ex_btn = tk.Button(
            url_ex_container,
            text=f"🔗 {url_example}",
            font=('Segoe UI', 9),
            fg=colors['accent_cyan'],
            bg=colors['bg_secondary'],
            activebackground=colors['bg_tertiary'],
            relief='flat',
            cursor='hand2',
            command=lambda u=url_example: gui_instance.set_url_example(u)
        )
        ex_btn.grid(row=0, column=i, padx=(0, 8))

    # --- SSL Verification Option (NEW) ---
    ssl_frame = tk.Frame(url_frame, bg=colors['bg_secondary'])
    ssl_frame.pack(fill='x', padx=10, pady=(10, 8))

    gui_instance.quick_scan_skip_ssl_var = getattr(gui_instance, 'quick_scan_skip_ssl_var', tk.BooleanVar(value=False))

    ssl_checkbox = tk.Checkbutton(
        ssl_frame,
        text="⚠️ Skip SSL Verification (for sites with invalid/self-signed certificates)",
        variable=gui_instance.quick_scan_skip_ssl_var,
        font=('Segoe UI', 9, 'bold'),
        fg=colors['warning'],
        bg=colors['bg_secondary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_secondary'],
        cursor='hand2'
    )
    ssl_checkbox.pack(anchor='w')

    # --- Vulnerability Selection Section (responsive two-column grid) ---
    vuln_selection_label = tk.Label(
        url_frame,
        text="Select Vulnerabilities to Scan:",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    vuln_selection_label.pack(anchor='w', padx=10, pady=(12, 6))

    checkbox_container = tk.Frame(url_frame, bg=colors['bg_secondary'])
    checkbox_container.pack(fill='x', padx=12, pady=(0, 10))
    checkbox_container.grid_columnconfigure(0, weight=1)
    checkbox_container.grid_columnconfigure(1, weight=1)

    # vulnerability list
    gui_instance.vuln_vars = getattr(gui_instance, 'vuln_vars', {})
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

    for idx, (vuln_id, vuln_label, default) in enumerate(vulnerabilities):
        row = idx // 2
        col = idx % 2
        var = tk.BooleanVar(value=default)
        gui_instance.vuln_vars[vuln_id] = var

        cb = tk.Checkbutton(
            checkbox_container,
            text=vuln_label,
            variable=var,
            font=('Segoe UI', 9),
            fg=colors['text_primary'],
            bg=colors['bg_secondary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan'],
            cursor='hand2',
            command=lambda vid=vuln_id: gui_instance.on_vuln_checkbox_change(vid)
        )
        cb.grid(row=row, column=col, sticky='w', padx=6, pady=4)

    # --- Divider ---
    divider = tk.Frame(scrollable_frame, bg=colors['border'], height=1)
    divider.pack(fill='x', padx=20, pady=10)

    # --- Natural Language Query Section (responsive) ---
    query_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    query_frame.pack(fill='x', padx=20, pady=10)

    query_title = tk.Label(
        query_frame,
        text="🔍 Natural Language Query (Alternative)",
        font=('Segoe UI', 13, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    query_title.pack(anchor='w', padx=10, pady=(10, 6))

    query_subtitle = tk.Label(
        query_frame,
        text="Or describe what you want to scan in plain English or Indonesian",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    query_subtitle.pack(anchor='w', padx=10, pady=(0, 10))

    query_input_frame = tk.Frame(query_frame, bg=colors['bg_secondary'])
    query_input_frame.pack(fill='x', padx=10, pady=(0, 10))
    query_input_frame.grid_columnconfigure(0, weight=1)

    gui_instance.query_entry = tk.Entry(
        query_input_frame,
        textvariable=gui_instance.query_var,
        font=('Arial', 12),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief='flat',
        bd=8
    )
    gui_instance.query_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10), pady=4)
    gui_instance.query_entry.bind('<Return>', lambda e: gui_instance.analyze_query())

    gui_instance.query_entry.insert(0, 'e.g., "find XSS in login page" or "cari celah di website editor"')
    gui_instance.query_entry.config(fg=colors['text_secondary'])
    gui_instance.query_entry.bind('<FocusIn>', gui_instance.on_query_focus_in)
    gui_instance.query_entry.bind('<FocusOut>', gui_instance.on_query_focus_out)

    analyze_btn = tk.Button(
        query_input_frame,
        text="Analyze",
        font=('Arial', 11, 'bold'),
        bg=colors['accent_cyan'],
        fg=colors['bg_primary'],
        activebackground=colors['accent_purple'],
        relief='flat',
        cursor='hand2',
        command=gui_instance.analyze_query,
        padx=14,
        pady=6
    )
    analyze_btn.grid(row=0, column=1, sticky='e')

    # Examples — vertical list that remains compact
    examples_frame = tk.Frame(query_frame, bg=colors['bg_secondary'])
    examples_frame.pack(fill='x', padx=10, pady=(6, 8))

    examples = [
        "find SQL injection vulnerabilities",
        "scan login page for XSS",
        "cari celah keamanan di admin panel",
        "check all security issues in website"
    ]

    for ex in examples:
        ex_label = tk.Label(
            examples_frame,
            text=f"• {ex}",
            font=('Arial', 9),
            fg=colors['text_secondary'],
            bg=colors['bg_secondary'],
            cursor='hand2'
        )
        ex_label.pack(anchor='w', pady=2)
        ex_label.bind('<Button-1>', lambda e, text=ex: gui_instance.set_query_example(text))

    # --- Parsed Results Section (expandable) ---
    results_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    results_frame.pack(fill='both', expand=True, padx=20, pady=(6, 20))

    results_title = tk.Label(
        results_frame,
        text="📋 Parsed Parameters",
        font=('Arial', 14, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    results_title.pack(anchor='w', padx=10, pady=(10, 8))

    gui_instance.parsed_text = scrolledtext.ScrolledText(
        results_frame,
        font=('Courier New', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief='flat',
        height=10,
        state='disabled'
    )
    gui_instance.parsed_text.pack(fill='both', expand=True, padx=10, pady=(0, 12))

    # Action buttons aligned to the right and responsive
    action_frame = tk.Frame(results_frame, bg=colors['bg_secondary'])
    action_frame.pack(fill='x', padx=10, pady=(0, 10))

    gui_instance.quick_scan_btn = tk.Button(
        action_frame,
        text="▶ Start Scan",
        font=('Arial', 12, 'bold'),
        bg=colors['success'],
        fg='white',
        activebackground='#059669',
        relief='flat',
        cursor='hand2',
        command=gui_instance.start_quick_scan,
        padx=18,
        pady=8,
        state='disabled'
    )
    gui_instance.quick_scan_btn.pack(side='right')

    # ─── External Tools Section ─────────────────────────────────
    from gui.security_tools import get_tools_for_tab, get_categories
    
    ext_tools_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    ext_tools_frame.pack(fill='x', padx=20, pady=(10, 20))

    ext_header = tk.Frame(ext_tools_frame, bg=colors['bg_secondary'])
    ext_header.pack(fill='x', padx=10, pady=(10, 5))

    tk.Label(
        ext_header,
        text="🔧 External Security Tools",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(side='left')

    tk.Label(
        ext_header,
        text="(enable tools to run alongside built-in scanner)",
        font=('Segoe UI', 9, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='left', padx=(8, 0))

    # Live count of selected tools
    quick_count_label = tk.Label(
        ext_header,
        text="0 selected",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    quick_count_label.pack(side='right', padx=(0, 10))

    # Status indicator
    gui_instance.quick_tool_status = tk.Label(
        ext_tools_frame,
        text="Select tools to use during scan — unavailable tools will be skipped",
        font=('Segoe UI', 8, 'italic'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.quick_tool_status.pack(anchor='w', padx=10, pady=(0, 5))

    # Tool checkboxes grid — organized by category
    tools_grid = tk.Frame(ext_tools_frame, bg=colors['bg_secondary'])
    tools_grid.pack(fill='x', padx=10, pady=(0, 10))
    tools_grid.grid_columnconfigure(0, weight=1, uniform='qtool')
    tools_grid.grid_columnconfigure(1, weight=1, uniform='qtool')
    tools_grid.grid_columnconfigure(2, weight=1, uniform='qtool')

    quick_tools = get_tools_for_tab('quick')
    gui_instance.quick_ext_tool_vars = {}
    
    row_idx = 0
    col_idx = 0
    for tool_id, info in quick_tools.items():
        var = tk.BooleanVar(value=False)
        gui_instance.quick_ext_tool_vars[tool_id] = var

        cb = tk.Checkbutton(
            tools_grid,
            text=f"{info['icon']} {info['name']}",
            variable=var,
            font=('Segoe UI', 9),
            fg=colors['text_primary'],
            bg=colors['bg_secondary'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['bg_secondary'],
            activeforeground=colors['accent_cyan'],
            cursor='hand2'
        )
        cb.grid(row=row_idx, column=col_idx, sticky='w', padx=4, pady=2)

        col_idx += 1
        if col_idx >= 3:
            col_idx = 0
            row_idx += 1

    # Live count updater
    def _update_quick_count(*args):
        count = sum(1 for v in gui_instance.quick_ext_tool_vars.values() if v.get())
        quick_count_label.config(
            text=f"{count} selected",
            fg=colors['accent_cyan'] if count > 0 else colors['text_secondary']
        )

    for var in gui_instance.quick_ext_tool_vars.values():
        var.trace_add('write', _update_quick_count)

    # Select All / None buttons
    quick_tool_btns = tk.Frame(ext_tools_frame, bg=colors['bg_secondary'])
    quick_tool_btns.pack(fill='x', padx=10, pady=(0, 10))

    def _select_all_quick():
        for v in gui_instance.quick_ext_tool_vars.values():
            v.set(True)

    def _select_none_quick():
        for v in gui_instance.quick_ext_tool_vars.values():
            v.set(False)

    tk.Button(
        quick_tool_btns,
        text="✅ Select All",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['accent_cyan'],
        relief='flat',
        cursor='hand2',
        command=_select_all_quick,
        padx=10,
        pady=4
    ).pack(side='left', padx=(0, 5))

    tk.Button(
        quick_tool_btns,
        text="❌ Clear All",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_secondary'],
        relief='flat',
        cursor='hand2',
        command=_select_none_quick,
        padx=10,
        pady=4
    ).pack(side='left')
