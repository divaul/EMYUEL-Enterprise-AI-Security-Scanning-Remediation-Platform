"""Results tab setup - Scan results and analytics display"""

import tkinter as tk
from tkinter import ttk, scrolledtext


def setup_results_tab(parent, gui_instance):
    """
    Setup scan results tab with progress, statistics, and console output
    
    Args:
        parent: Parent frame for this tab
        gui_instance: Reference to main EMYUELGUI instance for colors and callbacks
    """
    colors = gui_instance.colors
    
    # Create scrollable container
    scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    
    # Header Section
    header_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    header_frame.pack(fill='x', padx=20, pady=20)
    
    tk.Label(
        header_frame,
        text="📊 Scan Results & Analytics",
        font=('Segoe UI', 14, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(15, 5))
    
    tk.Label(
        header_frame,
        text="Real-time scan progress, findings statistics, and detailed console output",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    ).pack(anchor='w', padx=20, pady=(0, 15))
    
    # Progress section
    progress_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    progress_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    progress_label = tk.Label(
        progress_frame,
        text="⏳ Scan Progress",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    progress_label.pack(anchor='w', padx=20, pady=(15, 10))
    
    # Progress bar container
    progress_container = tk.Frame(progress_frame, bg=colors['bg_tertiary'])
    progress_container.pack(fill='x', padx=20, pady=(0, 10))
    
    gui_instance.progress_var = tk.DoubleVar()
    gui_instance.progress_bar = ttk.Progressbar(
        progress_container,
        variable=gui_instance.progress_var,
        maximum=100,
        mode='determinate',
        length=400
    )
    gui_instance.progress_bar.pack(fill='x', padx=10, pady=10)
    
    gui_instance.progress_label = tk.Label(
        progress_frame,
        text="No active scan",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    gui_instance.progress_label.pack(anchor='w', padx=20, pady=(0, 15))
    
    # Statistics
    stats_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    stats_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    stats_label = tk.Label(
        stats_frame,
        text="📈 Vulnerability Findings",
        font=('Segoe UI', 12, 'bold'),
        fg=colors['text_primary'],
        bg=colors['bg_secondary']
    )
    stats_label.pack(anchor='w', padx=20, pady=(15, 10))
    
    stats_inner = tk.Frame(stats_frame, bg=colors['bg_secondary'])
    stats_inner.pack(fill='x', padx=20, pady=(0, 15))
    
    # Create stat boxes with improved styling
    gui_instance.create_stat_box(stats_inner, "Critical", "0", colors['critical'], "🔴")
    gui_instance.create_stat_box(stats_inner, "High", "0", colors['error'], "🟠")
    gui_instance.create_stat_box(stats_inner, "Medium", "0", colors['warning'], "🟡")
    gui_instance.create_stat_box(stats_inner, "Low", "0", colors['success'], "🟢")
    gui_instance.create_stat_box(stats_inner, "Info", "0", colors['text_secondary'], "ℹ️")
    
    # Console output
    console_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    console_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
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
        height=15
    )
    gui_instance.console_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    # ========================================================================
    # 📊 SCAN HISTORY SECTION (NEW - Database Integration)
    # ========================================================================
    
    history_frame = tk.Frame(scrollable_frame, bg=colors['bg_secondary'], relief='flat', bd=2)
    history_frame.pack(fill='both', expand=True, padx=20, pady=(20, 20))
    
    # Header
    header_container = tk.Frame(history_frame, bg=colors['bg_secondary'])
    header_container.pack(fill='x', padx=15, pady=(15, 10))
    
    tk.Label(
        header_container,
        text="📊 Scan History",
        font=('Segoe UI', 14, 'bold'),
        fg=colors['accent_cyan'],
        bg=colors['bg_secondary']
    ).pack(side='left')
    
    # Scan count label
    scan_count_label = tk.Label(
        header_container,
        text="Total scans: 0",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    scan_count_label.pack(side='right', padx=10)
    gui_instance.scan_count_label = scan_count_label
    
    # Description
    tk.Label(
        history_frame,
        text="View and manage your previous security scans. All scans are automatically saved to database.",
        font=('Segoe UI', 9),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary'],
        wraplength=700,
        justify='left'
    ).pack(anchor='w', padx=15, pady=(0, 10))
    
    # Listbox container with scrollbar
    listbox_container = tk.Frame(history_frame, bg=colors['bg_primary'])
    listbox_container.pack(fill='both', expand=True, padx=15, pady=10)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(listbox_container, orient='vertical')
    scrollbar.pack(side='right', fill='y')
    
    # Listbox for scan history
    scan_history_listbox = tk.Listbox(
        listbox_container,
        height=8,
        bg=colors['bg_primary'],
        fg=colors['text_primary'],
        selectbackground=colors['accent_cyan'],
        selectforeground=colors['bg_primary'],
        font=('Consolas', 9),
        selectmode='single',
        yscrollcommand=scrollbar.set,
        relief='flat',
        bd=0,
        highlightthickness=1,
        highlightbackground=colors['border'],
        highlightcolor=colors['accent_cyan']
    )
    scan_history_listbox.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=scan_history_listbox.yview)
    
    # Store reference in gui_instance for database integration
    gui_instance.scan_history_listbox = scan_history_listbox
    
    # Placeholder text when empty
    if not hasattr(gui_instance, 'scan_history') or not gui_instance.scan_history:
        scan_history_listbox.insert(tk.END, "No scans in history yet.")
        scan_history_listbox.insert(tk.END, "Run a scan to see it saved here automatically.")
    
    # Button container
    btn_container = tk.Frame(history_frame, bg=colors['bg_secondary'])
    btn_container.pack(fill='x', padx=15, pady=(5, 15))
    
    # Delete button
    delete_btn = tk.Button(
        btn_container,
        text="🗑️ Delete Selected",
        command=gui_instance.delete_selected_scan,
        bg=colors['error'],  # Fixed: Use 'error' instead of 'danger'
        fg='white',
        font=('Segoe UI', 9, 'bold'),
        relief='flat',
        cursor='hand2',
        padx=15,
        pady=8
    )
    delete_btn.pack(side='left', padx=(0, 10))
    
    # Refresh button
    refresh_btn = tk.Button(
        btn_container,
        text="🔄 Refresh",
        command=gui_instance.load_scan_history,
        bg=colors['accent_cyan'],
        fg=colors['bg_primary'],
        font=('Segoe UI', 9, 'bold'),
        relief='flat',
        cursor='hand2',
        padx=15,
        pady=8
    )
    refresh_btn.pack(side='left', padx=(0, 10))
    
    # Info label
    info_label = tk.Label(
        btn_container,
        text="💡 Tip: Scans are automatically saved after completion",
        font=('Segoe UI', 8),
        fg=colors['text_secondary'],
        bg=colors['bg_secondary']
    )
    info_label.pack(side='right', padx=10)
    
    # Initial load of scan history if database available
    if gui_instance.db and hasattr(gui_instance, 'scan_history'):
        gui_instance.refresh_scan_history_ui()
