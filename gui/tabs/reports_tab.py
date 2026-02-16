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
    
    # Initial refresh
    gui_instance.refresh_report_history()
