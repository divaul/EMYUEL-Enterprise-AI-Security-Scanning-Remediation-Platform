"""API Keys tab setup - API configuration for LLM providers"""

import tkinter as tk
from tkinter import ttk


def setup_api_tab(parent, gui_instance):
    """
    Setup API configuration tab for OpenAI, Gemini, and Claude
    
    Args:
        parent: Parent frame for this tab
        gui_instance: Reference to main EMYUELGUI instance for colors and callbacks
    """
    colors = gui_instance.colors
    
    # Create scrollable container
    scrollable_frame, canvas = gui_instance.create_scrollable_frame(parent)
    
    info_label = tk.Label(
        scrollable_frame,
        text="Configure your LLM provider API keys below. Keys are stored securely on your local machine.",
        font=('Arial', 10),
        fg=colors['text_secondary'],
        bg=colors['bg_primary'],
        wraplength=800,
        justify='left'
    )
    info_label.pack(anchor='w', padx=30, pady=20)
    
    # OpenAI
    gui_instance.create_api_key_section(scrollable_frame, "OpenAI", gui_instance.api_key_openai, "openai")
    
    # Google Gemini
    gui_instance.create_api_key_section(scrollable_frame, "Google Gemini", gui_instance.api_key_gemini, "gemini")
    
    # Anthropic Claude
    gui_instance.create_api_key_section(scrollable_frame, "Anthropic Claude", gui_instance.api_key_claude, "claude")

    # ── Blockchain API Keys ─────────────────────────────────────────────────
    colors_bg = colors['bg_secondary']
    bc_frame = tk.Frame(scrollable_frame, bg=colors_bg, relief='flat', bd=0)
    bc_frame.pack(fill='x', padx=30, pady=(10, 0))

    tk.Label(bc_frame, text='🔗 Blockchain API Keys',
             font=('Segoe UI', 12, 'bold'), fg=colors['text_primary'],
             bg=colors_bg).pack(anchor='w', pady=(8, 2))
    tk.Label(bc_frame,
             text='Optional — required only for on-chain smart contract scanning via Mythril.',
             font=('Segoe UI', 9), fg=colors['text_secondary'],
             bg=colors_bg).pack(anchor='w', pady=(0, 8))

    # Init vars if not already set (idempotent — crypto_blockchain_tab also inits these)
    if not hasattr(gui_instance, 'etherscan_key_var'):
        gui_instance.etherscan_key_var = tk.StringVar(value='')
    if not hasattr(gui_instance, 'rpc_url_var'):
        gui_instance.rpc_url_var = tk.StringVar(value='https://mainnet.infura.io/v3/YOUR_KEY')

    def _row(parent, label, var, placeholder=''):
        row = tk.Frame(parent, bg=colors_bg)
        row.pack(fill='x', pady=4)
        row.grid_columnconfigure(1, weight=1)
        tk.Label(row, text=label, font=('Segoe UI', 10), width=22, anchor='w',
                 fg=colors['text_secondary'], bg=colors_bg).grid(row=0, column=0, sticky='w')
        ent = tk.Entry(row, textvariable=var, font=('Segoe UI', 10), show='*',
                       bg=colors['bg_tertiary'], fg=colors['text_primary'],
                       insertbackground=colors['text_primary'], relief='flat', bd=8)
        ent.grid(row=0, column=1, sticky='ew', padx=(8, 0))
        return ent

    _row(bc_frame, 'Etherscan API Key:', gui_instance.etherscan_key_var)
    _row(bc_frame, 'Infura / Alchemy RPC:', gui_instance.rpc_url_var)

    # Show/Hide toggle
    show_frame = tk.Frame(scrollable_frame, bg=colors['bg_primary'])
    show_frame.pack(fill='x', padx=30, pady=20)

    show_check = tk.Checkbutton(
        show_frame,
        text="Show API Keys",
        variable=gui_instance.show_key_var,
        font=('Arial', 10),
        bg=colors['bg_primary'],
        fg=colors['text_secondary'],
        selectcolor=colors['bg_tertiary'],
        activebackground=colors['bg_primary'],
        activeforeground=colors['text_primary'],
        command=gui_instance.toggle_show_keys
    )
    show_check.pack(side='left')

    # Save button
    save_frame = tk.Frame(scrollable_frame, bg=colors['bg_primary'])
    save_frame.pack(fill='x', padx=30, pady=20)

    save_btn = tk.Button(
        save_frame,
        text="💾 Save API Keys",
        font=('Arial', 12, 'bold'),
        bg=colors['success'],
        fg='white',
        activebackground='#059669',
        relief='flat',
        cursor='hand2',
        command=gui_instance.save_api_keys,
        padx=30,
        pady=12
    )
    save_btn.pack()

    # Note: load_api_keys() should be called in main class __init__

