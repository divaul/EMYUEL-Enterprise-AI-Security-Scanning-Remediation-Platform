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
