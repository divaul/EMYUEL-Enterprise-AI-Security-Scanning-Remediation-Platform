"""
Reports Tab - Professional report generation with AI enhancement
Provides both AI-formatted and raw report options with report history
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import webbrowser
from datetime import datetime


def setup_reports_tab(parent, gui_instance):
    """
    Setup reports tab with AI-enhanced and raw report generation
    
    Args:
        parent: Parent frame for this tab
        gui_instance: Reference to main EMYUELGUI instance
    """
    colors = gui_instance.colors
    
    # Create scrollable container
    scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    
    #  ──────── HEADER ────────
    header_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    header_frame.pack(fill='x', padx=20, pady=20)
    
    tk.Label(
        header_frame,
        text="📊 Report Generation",
        font=('Segoe UI', 16, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(15, 5))
    
    tk.Label(
        header_frame,
        text="Generate professional cybersecurity reports following international standards (OWASP, NIST, ISO 27001)",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        wraplength=800,
        justify='left'
    ).pack(anchor='w', padx=20, pady=(0, 15))
    
    # ──────── BUG MONITORING DASHBOARD ────────
    monitoring_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    monitoring_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    tk.Label(
        monitoring_frame,
        text="🐛 Bug Monitoring Dashboard",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(15, 10))
    
    # Stats cards row
    stats_container = tk.Frame(monitoring_frame, bg=colors['bg_secondary'])
    stats_container.pack(fill='x', padx=20, pady=(0, 15))
    
    # Create 4 stat cards
    for i in range(4):
        stats_container.grid_columnconfigure(i, weight=1, uniform='stat')
    
    # Card 1: Total Bugs
    card1 = tk.Frame(stats_container, bg=colors['bg_tertiary'], relief='flat', bd=1, highlightthickness=1, highlightbackground=colors['border'])
    card1.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=5)
    
    gui_instance.bugs_total_count = tk.Label(
        card1,
        text="0",
        font=('Segoe UI', 24, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_tertiary']
    )
    gui_instance.bugs_total_count.pack(pady=(15, 5))
    
    tk.Label(
        card1,
        text="Total Bugs",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary']
    ).pack(pady=(0, 15))
    
    # Card 2: Critical
    card2 = tk.Frame(stats_container, bg=colors['bg_tertiary'], relief='flat', bd=1, highlightthickness=1, highlightbackground=colors['error'])
    card2.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=5)
    
    gui_instance.bugs_critical_count = tk.Label(
        card2,
        text="0",
        font=('Segoe UI', 24, 'bold'),
        fg=colors['error'],
        bg=colors['bg_tertiary']
    )
    gui_instance.bugs_critical_count.pack(pady=(15, 5))
    
    tk.Label(
        card2,
        text="Critical",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary']
    ).pack(pady=(0, 15))
    
    # Card 3: High
    card3 = tk.Frame(stats_container, bg=colors['bg_tertiary'], relief='flat', bd=1, highlightthickness=1, highlightbackground=colors['warning'])
    card3.grid(row=0, column=2, sticky='nsew', padx=(0, 10), pady=5)
    
    gui_instance.bugs_high_count = tk.Label(
        card3,
        text="0",
        font=('Segoe UI', 24, 'bold'),
        fg=colors['warning'],
        bg=colors['bg_tertiary']
    )
    gui_instance.bugs_high_count.pack(pady=(15, 5))
    
    tk.Label(
        card3,
        text="High",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary']
    ).pack(pady=(0, 15))
    
    # Card 4: Medium/Low
    card4 = tk.Frame(stats_container, bg=colors['bg_tertiary'], relief='flat', bd=1, highlightthickness=1, highlightbackground=colors['success'])
    card4.grid(row=0, column=3, sticky='nsew', pady=5)
    
    gui_instance.bugs_other_count = tk.Label(
        card4,
        text="0",
        font=('Segoe UI', 24, 'bold'),
        fg=colors['success'],
        bg=colors['bg_tertiary']
    )
    gui_instance.bugs_other_count.pack(pady=(15, 5))
    
    tk.Label(
        card4,
        text="Medium/Low",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary']
    ).pack(pady=(0, 15))
    
    # Bug List Table
    tk.Label(
        monitoring_frame,
        text="📋 Discovered Vulnerabilities",
        font=('Segoe UI', 11, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(10, 8))
    
    # Create table with scrollbar
    table_container = tk.Frame(monitoring_frame, bg=colors['bg_tertiary'])
    table_container.pack(fill='both', expand=True, padx=20, pady=(0, 15))
    
    # Table headers
    headers_frame = tk.Frame(table_container, bg=colors['bg_tertiary'])
    headers_frame.pack(fill='x', pady=(10, 0))
    
    headers = [
        ("Severity", 0.15),
        ("Type", 0.25),
        ("Location", 0.35),
        ("Description", 0.25)
    ]
    
    for header, weight in headers:
        col_frame = tk.Frame(headers_frame, bg=colors['bg_tertiary'])
        col_frame.pack(side='left', fill='both', expand=True)
        if weight:
            col_frame.pack_configure(fill='both', expand=True)
        
        tk.Label(
            col_frame,
            text=header,
            font=('Segoe UI', 9, 'bold'),
            fg=colors['accent_cyan'],
            bg=colors['bg_tertiary'],
            anchor='w',
            padx=10
        ).pack(fill='x')
    
    # Scrollable bug list
    bugs_list_frame = tk.Frame(table_container, bg=colors['bg_tertiary'])
    bugs_list_frame.pack(fill='both', expand=True)
    
    bugs_canvas = tk.Canvas(
        bugs_list_frame,
        bg=colors['bg_tertiary'],
        highlightthickness=0,
        height=200
    )
    bugs_scrollbar = tk.Scrollbar(bugs_list_frame, orient="vertical", command=bugs_canvas.yview)
    bugs_scrollable = tk.Frame(bugs_canvas, bg=colors['bg_tertiary'])
    
    bugs_scrollable.bind(
        "<Configure>",
        lambda e: bugs_canvas.configure(scrollregion=bugs_canvas.bbox("all"))
    )
    
    bugs_canvas.create_window((0, 0), window=bugs_scrollable, anchor="nw")
    bugs_canvas.configure(yscrollcommand=bugs_scrollbar.set)
    
    bugs_canvas.pack(side="left", fill="both", expand=True)
    bugs_scrollbar.pack(side="right", fill="y")
    
    # Store reference for updating
    gui_instance.bugs_scrollable_frame = bugs_scrollable
    
    # Empty state message
    gui_instance.bugs_empty_label = tk.Label(
        bugs_scrollable,
        text="No vulnerabilities discovered yet.\nRun a scan to populate this dashboard.",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary'],
        justify='center',
        pady=40
    )
    gui_instance.bugs_empty_label.pack(fill='both', expand=True)
    
    # ──────── SCAN HISTORY SELECTION ────────
    history_select_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    history_select_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    history_header = tk.Frame(history_select_frame, bg=colors['bg_secondary'])
    history_header.pack(fill='x', padx=20, pady=(15, 10))
    
    tk.Label(
        history_header,
        text="📋 Scan History - Select Scan to View/Export",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(side='left')
    
    # Refresh button
    refresh_history_btn = tk.Button(
        history_header,
        text="🔄 Refresh",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_secondary'],
        activebackground=colors['accent_cyan'],
        activeforeground='white',
        relief='flat',
        cursor='hand2',
        command=lambda: gui_instance.refresh_scan_history(),
        padx=12,
        pady=5
    )
    refresh_history_btn.pack(side='right')
    
    # Search box
    search_frame = tk.Frame(history_select_frame, bg=colors['bg_secondary'])
    search_frame.pack(fill='x', padx=20, pady=(0, 10))
    
    tk.Label(
        search_frame,
        text="🔍 Search:",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(side='left', padx=(0, 5))
    
    gui_instance.scan_search_var = tk.StringVar()
    gui_instance.scan_search_var.trace('w', lambda *args: gui_instance.search_scans())
    
    search_entry = tk.Entry(
        search_frame,
        textvariable=gui_instance.scan_search_var,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        relief='flat',
        bd=5
    )
    search_entry.pack(side='left', fill='x', expand=True, padx=5)
    
    # Listbox for scan history
    list_container = tk.Frame(history_select_frame, bg=colors['bg_tertiary'])
    list_container.pack(fill='both', expand=True, padx=20, pady=(0, 10))
    
    scrollbar = tk.Scrollbar(list_container)
    scrollbar.pack(side='right', fill='y')
    
    gui_instance.scan_history_listbox = tk.Listbox(
        list_container,
        yscrollcommand=scrollbar.set,
        font=('Segoe UI', 10),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        selectbackground=colors['accent_cyan'],
        selectforeground='white',
        selectmode='single',
        relief='flat',
        height=6
    )
    gui_instance.scan_history_listbox.pack(fill='both', expand=True, padx=5, pady=5)
    scrollbar.config(command=gui_instance.scan_history_listbox.yview)
    
    # Bind selection event
    gui_instance.scan_history_listbox.bind('<<ListboxSelect>>', gui_instance.on_scan_selected)
    
    # Store scan IDs mapping
    gui_instance.scan_history_ids = []  # List of scan_ids corresponding to listbox items
    
    # Action buttons for selected scan
    action_frame = tk.Frame(history_select_frame, bg=colors['bg_secondary'])
    action_frame.pack(fill='x', padx=20, pady=(0, 15))
    
    gui_instance.delete_scan_btn = tk.Button(
        action_frame,
        text="🗑️ Delete Selected",
        font=('Segoe UI', 9),
        bg=colors['error'],
        fg='white',
        activebackground='#c0392b',
        relief='flat',
        cursor='hand2',
        command=gui_instance.delete_selected_scan,
        padx=15,
        pady=5,
        state='disabled'
    )
    gui_instance.delete_scan_btn.pack(side='right', padx=5)
    
    # Selected scan details display
    gui_instance.selected_scan_details = tk.Label(
        history_select_frame,
        text="No scan selected - Select from history above",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        justify='left',
        anchor='w',
        padx=20
    )
    gui_instance.selected_scan_details.pack(fill='x', padx=20, pady=(0, 15))
    
    # ──────── SCAN SUMMARY ────────

    summary_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    summary_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    tk.Label(
        summary_frame,
        text="📋 Last Scan Summary",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(15, 10))
    
    # Summary content
    summary_content = tk.Frame(summary_frame, bg=colors['bg_tertiary'], relief='flat')
    summary_content.pack(fill='x', padx=20, pady=(0, 15))
    
    gui_instance.report_summary_label = tk.Label(
        summary_content,
        text="No scan completed yet. Run a scan first to generate reports.",
        font=('Segoe UI', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_tertiary'],
        justify='left',
        anchor='w',
        padx=15,
        pady=15
    )
    gui_instance.report_summary_label.pack(fill='x')

    
    # ──────── REPORT TYPE SELECTION ────────
    report_types_frame = tk.Frame(scrollable_frame, bg=colors['bg_primary'])
    report_types_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    tk.Label(
        report_types_frame,
        text="Select Report Type:",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_primary']
    ).pack(anchor='w', pady=(0, 10))
    
    # Two-column layout for report options
    options_container = tk.Frame(report_types_frame, bg=colors['bg_primary'])
    options_container.pack(fill='x')
    options_container.grid_columnconfigure(0, weight=1,uniform='report')
    options_container.grid_columnconfigure(1, weight=1, uniform='report')
    
    # ──── LEFT: AI-Enhanced Report ────
    ai_card = tk.Frame(options_container, bg=colors['accent_purple'], relief='flat', bd=2)
    ai_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10), pady=5)
    
    tk.Label(
        ai_card,
        text="🤖 AI-Enhanced Report",
        font=('Segoe UI', 13, 'bold'),
        fg='white',
        bg=colors['accent_purple']
    ).pack(anchor='w', padx=15, pady=(15, 8))
    
    tk.Label(
        ai_card,
        text="Professional report following international cybersecurity standards:",
        font=('Segoe UI', 9),
        fg='white',
        bg=colors['accent_purple'],
        wraplength=350,
        justify='left'
    ).pack(anchor='w', padx=15)
    
    features_ai = [
        "✓ OWASP Testing Guide format",
        "✓ NIST SP 800-115 methodology",
        "✓ ISO/IEC 27001:2022 compliance",
        "✓ Executive summary",
        "✓ Risk assessment matrix",
        "✓ CVSS scoring",
        "✓ Detailed remediation steps",
        "✓ Compliance considerations"
    ]
    
    for feature in features_ai:
        tk.Label(
            ai_card,
            text=feature,
            font=('Segoe UI', 8),
            fg='#e0e0e0',
            bg=colors['accent_purple']
        ).pack(anchor='w', padx=20, pady=1)
    
    # AI Provider selection
    tk.Label(
        ai_card,
        text="\nAI Provider:",
        font=('Segoe UI', 9, 'bold'),
        fg='white',
        bg=colors['accent_purple']
    ).pack(anchor='w', padx=15, pady=(10, 5))
    
    provider_frame = tk.Frame(ai_card, bg=colors['accent_purple'])
    provider_frame.pack(fill='x', padx=15, pady=(0, 15))
    
    gui_instance.ai_report_provider_var = tk.StringVar(value='gemini')
    
    providers = [
        ('Gemini', 'gemini'),
        ('OpenAI', 'openai'),
        ('Claude', 'claude')
    ]
    
    for label, value in providers:
        tk.Radiobutton(
            provider_frame,
            text=label,
            variable=gui_instance.ai_report_provider_var,
            value=value,
            font=('Segoe UI', 9),
            fg='white',
            bg=colors['accent_purple'],
            selectcolor=colors['bg_tertiary'],
            activebackground=colors['accent_purple'],
            activeforeground='white'
        ).pack(side='left', padx=(0, 10))
    
    # Generate AI button
    gui_instance.generate_ai_report_btn = tk.Button(
        ai_card,
        text="🚀 Generate AI-Enhanced Report",
        font=('Segoe UI', 11, 'bold'),
        bg='white',
        fg=colors['accent_purple'],
        activebackground='#f0f0f0',
        relief='flat',
        cursor='hand2',
        command=gui_instance.generate_ai_report,
        padx=20,
        pady=12,
        state='disabled'
    )
    gui_instance.generate_ai_report_btn.pack(fill='x', padx=15, pady=(5, 15))
    
    # ──── RIGHT: Raw Report ────
    raw_card = tk.Frame(options_container, bg=colors['accent_cyan'], relief='flat', bd=2)
    raw_card.grid(row=0, column=1, sticky='nsew', padx=(10, 0), pady=5)
    
    tk.Label(
        raw_card,
        text="📄 Raw Technical Report",
        font=('Segoe UI', 13, 'bold'),
        fg='white',
        bg=colors['accent_cyan']
    ).pack(anchor='w', padx=15, pady=(15, 8))
    
    tk.Label(
        raw_card,
        text="Complete technical data export with full details:",
        font=('Segoe UI', 9),
        fg='white',
        bg=colors['accent_cyan'],
        wraplength=350,
        justify='left'
    ).pack(anchor='w', padx=15)
    
    features_raw = [
        "✓ JSON export (machine-readable)",
        "✓ HTML report (interactive)",
        "✓ Complete vulnerability data",
        "✓ All technical details",
        "✓ Code snippets & evidence",
        "✓ Network requests/responses",
        "✓ File paths & line numbers",
        "✓ Instant generation"
    ]
    
    for feature in features_raw:
        tk.Label(
            raw_card,
            text=feature,
            font=('Segoe UI', 8),
            fg='#e0e0e0',
            bg=colors['accent_cyan']
        ).pack(anchor='w', padx=20, pady=1)
    
    # Spacer to align button
    tk.Label(
        raw_card,
        text="",
        bg=colors['accent_cyan'],
        height=3
    ).pack()
    
    # Generate Raw button
    gui_instance.generate_raw_report_btn = tk.Button(
        raw_card,
        text="⚡ Generate Raw Report",
        font=('Segoe UI', 11, 'bold'),
        bg='white',
        fg=colors['accent_cyan'],
        activebackground='#f0f0f0',
        relief='flat',
        cursor='hand2',
        command=gui_instance.generate_raw_report,
        padx=20,
        pady=12,
        state='disabled'
    )
    gui_instance.generate_raw_report_btn.pack(fill='x', padx=15, pady=(15, 15))
    
    # ──────── REPORT HISTORY ────────
    history_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    history_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    history_header = tk.Frame(history_frame, bg=colors['bg_secondary'])
    history_header.pack(fill='x', padx=20, pady=(15, 10))
    
    tk.Label(
        history_header,
        text="📚 Report History",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    ).pack(side='left')
    
    # Refresh button
    refresh_btn = tk.Button(
        history_header,
        text="🔄 Refresh",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_secondary'],
        activebackground=colors['accent_cyan'],
        activeforeground='white',
        relief='flat',
        cursor='hand2',
        command=lambda: gui_instance.refresh_report_history(),
        padx=12,
        pady=5
    )
    refresh_btn.pack(side='right')
    
    # Report history list
    history_container = tk.Frame(history_frame, bg=colors['bg_tertiary'])
    history_container.pack(fill='both', expand=True, padx=20, pady=(0, 15))
    
    # Scrollable list
    gui_instance.report_history_text = scrolledtext.ScrolledText(
        history_container,
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        state='disabled',
        wrap='word',
        height=8
    )
    gui_instance.report_history_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    # ──────── LEGACY: CONSOLE OUTPUT (for compatibility) ────────
    # This is needed because other parts of the code reference console_text
    console_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    console_frame.pack(fill='both', expand=True, padx=20, pady=(20, 20))
    
    console_header = tk.Frame(console_frame, bg=colors['bg_secondary'])
    console_header.pack(fill='x', padx=20, pady=(15, 10))
    
    console_label = tk.Label(
        console_header,
        text="💻 Console Output",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    console_label.pack(side='left')
    
    # Clear console button
    clear_btn = tk.Button(
        console_header,
        text="🗑️ Clear",
        font=('Segoe UI', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_secondary'],
        activebackground=colors['error'],
        activeforeground='#ffffff',
        relief='flat',
        cursor='hand2',
        command=gui_instance.clear_console,
        padx=15,
        pady=5
    )
    clear_btn.pack(side='right')
    
    gui_instance.console_text = scrolledtext.ScrolledText(
        console_frame,
        font=('Consolas', 9),
        bg=colors['bg_tertiary'],
        fg=colors['text_primary'],
        insertbackground=colors['accent_cyan'],
        relief='flat',
        state='disabled',
        wrap='word',
        height=10
    )
    gui_instance.console_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    # Initial refresh
    gui_instance.refresh_report_history()
