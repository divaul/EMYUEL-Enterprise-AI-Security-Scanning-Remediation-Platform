"""
Quick Scan Tab - GUI Module
Module for quick security scanning with website URL input and natural language queries
"""

import tkinter as tk
from tkinter import scrolledtext


def setup_quick_scan_tab(parent, gui_instance):
    """Setup quick scan tab with website URL input and natural language query"""
    colors = gui_instance.colors
    
    # Create scrollable container
    scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    
    # Website URL Section (NEW - Priority #1)
    url_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    url_frame.pack(fill='x', padx=20, pady=20)
    
    url_title = tk.Label(
        url_frame,
        text="🌐 Website URL Scanner",
        font=('Segoe UI', 14, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    url_title.pack(anchor='w', padx=20, pady=(20, 10))
    
    url_subtitle = tk.Label(
        url_frame,
        text="Enter a website URL to scan for security vulnerabilities",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    url_subtitle.pack(anchor='w', padx=20, pady=(0, 15))
    
    # URL input with scan button
    url_input_frame = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_input_frame.pack(fill='x', padx=20, pady=(0, 10))
    
    gui_instance.url_entry = tk.Entry(
        url_input_frame,
        textvariable=gui_instance.target_var,
        font=('Segoe UI', 12),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        bd=12
    )
    gui_instance.url_entry.pack(fill='x', side='left', expand=True)
    gui_instance.url_entry.bind('<Return>', lambda e: gui_instance.quick_scan_url())
    
    # Placeholder
    gui_instance.url_entry.insert(0, 'https://example.com')
    gui_instance.url_entry.config(fg=colors['text_secondary'])
    gui_instance.url_entry.bind('<FocusIn>', gui_instance.on_url_focus_in)
    gui_instance.url_entry.bind('<FocusOut>', gui_instance.on_url_focus_out)
    
    # Quick Scan button
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
        padx=30,
        pady=12
    )
    quick_scan_btn.pack(side='right', padx=(10, 0))
    
    # URL Examples
    url_examples_label = tk.Label(
        url_frame,
        text="Quick Examples:",
        font=('Segoe UI', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    url_examples_label.pack(anchor='w', padx=20, pady=(10, 5))
    
    url_examples = [
        "https://example.com",
        "https://testphp.vulnweb.com",
        "http://demo.testfire.net"
    ]
    
    url_ex_container = tk.Frame(url_frame, bg=colors['bg_secondary'])
    url_ex_container.pack(anchor='w', padx=40, pady=(0, 15))
    
    for url_example in url_examples:
        ex_btn = tk.Label(
            url_ex_container,
            text=f"🔗 {url_example}",
            font=('Segoe UI', 9),
            fg=colors['accent_cyan'],
            bg=colors['bg_secondary'],
            cursor='hand2'
        )
        ex_btn.pack(side='left', padx=(0, 15))
        ex_btn.bind('<Button-1>', lambda e, url=url_example: gui_instance.set_url_example(url))
    
    # Vulnerability Selection Section
    vuln_selection_label = tk.Label(
        url_frame,
        text="Select Vulnerabilities to Scan:",
        font=('Segoe UI', 10, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    vuln_selection_label.pack(anchor='w', padx=20, pady=(15, 8))
    
    # Checkbox container
    checkbox_container = tk.Frame(url_frame, bg=colors['bg_secondary'])
    checkbox_container.pack(anchor='w', padx=40, pady=(0, 15))
    
    # Create checkboxes for vulnerability types
    gui_instance.vuln_vars = {}
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
    col1 = tk.Frame(checkbox_container, bg=colors['bg_secondary'])
    col1.pack(side='left', padx=(0, 30))
    
    col2 = tk.Frame(checkbox_container, bg=colors['bg_secondary'])
    col2.pack(side='left')
    
    for i, (vuln_id, vuln_label, default) in enumerate(vulnerabilities):
        var = tk.BooleanVar(value=default)
        gui_instance.vuln_vars[vuln_id] = var
        
        container = col1 if i < 4 else col2
        
        cb = tk.Checkbutton(
            container,
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
        cb.pack(anchor='w', pady=2)
    
    url_frame.pack_propagate(False)
    url_frame.configure(height=320)
    
    # Divider
    divider = tk.Frame(parent, bg=colors['border'], height=1)
    divider.pack(fill='x', padx=40, pady=10)
    
    # Natural Language Query Section (ALTERNATIVE METHOD)
    query_frame = tk.Frame(parent, bg=colors['bg_secondary'], relief='flat', bd=2)
    query_frame.pack(fill='x', padx=20, pady=20)
    
    query_title = tk.Label(
        query_frame,
        text="🔍 Natural Language Query (Alternative)",
        font=('Segoe UI', 13, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    query_title.pack(anchor='w', padx=20, pady=(20, 10))
    
    query_subtitle = tk.Label(
        query_frame,
        text="Or describe what you want to scan in plain English or Indonesian",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    query_subtitle.pack(anchor='w', padx=20, pady=(0, 15))
    
    # Query input
    query_input_frame = tk.Frame(query_frame, bg=colors['bg_secondary'])
    query_input_frame.pack(fill='x', padx=20, pady=(0, 10))
    
    gui_instance.query_entry = tk.Entry(
        query_input_frame,
        textvariable=gui_instance.query_var,
        font=('Arial', 12),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief='flat',
        bd=10
    )
    gui_instance.query_entry.pack(fill='x', side='left', expand=True)
    gui_instance.query_entry.bind('<Return>', lambda e: gui_instance.analyze_query())
    
    # Placeholder text
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
        padx=30,
        pady=10
    )
    analyze_btn.pack(side='right', padx=(10, 0))
    
    # Examples
    examples_label = tk.Label(
        query_frame,
        text="Examples:",
        font=('Arial', 9, 'bold'),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
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
            fg=colors['text_secondary'],
            bg=colors['bg_secondary'],
            cursor='hand2'
        )
        ex_label.pack(anchor='w', padx=40, pady=2)
        # Make clickable
        ex_label.bind('<Button-1>', lambda e, text=example[2:]: gui_instance.set_query_example(text))
    
    query_frame.pack_propagate(False)
    query_frame.configure(height=280)
    
    # Parsed Results Section
    results_frame = tk.Frame(parent, bg=colors['bg_secondary'], relief='flat', bd=2)
    results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    results_title = tk.Label(
        results_frame,
        text="📋 Parsed Parameters",
        font=('Arial', 14, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    results_title.pack(anchor='w', padx=20, pady=(20, 10))
    
    # Parsed output text
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
    gui_instance.parsed_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    # Action buttons
    action_frame = tk.Frame(results_frame, bg=colors['bg_secondary'])
    action_frame.pack(fill='x', padx=20, pady=(0, 20))
    
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
        padx=40,
        pady=12,
        state='disabled'
    )
    gui_instance.quick_scan_btn.pack(side='right')
