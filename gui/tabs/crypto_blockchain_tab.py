"""
Crypto & Blockchain Analysis Tab — EMYUEL
3 sub-tabs: Cryptography | Cryptocurrency | Blockchain (Smart Contract)
"""

import tkinter as tk
from tkinter import ttk, filedialog


# ─── Helper ──────────────────────────────────────────────────────────────────

def _label(parent, text, font=('Segoe UI', 10), fg_key='text_secondary', colors=None, **kw):
    return tk.Label(parent, text=text, font=font, fg=colors[fg_key], bg=colors['bg_secondary'], **kw)


def _entry(parent, textvar, colors, width=None, show=None):
    kw = dict(textvariable=textvar, font=('Segoe UI', 10),
              bg=colors['bg_tertiary'], fg=colors['text_primary'],
              insertbackground=colors['text_primary'], relief='flat', bd=8)
    if width:
        kw['width'] = width
    if show:
        kw['show'] = show
    return tk.Entry(parent, **kw)


def _section(parent, title, colors):
    """Titled card frame."""
    card = tk.Frame(parent, bg=colors['bg_secondary'], relief='flat', bd=0)
    card.pack(fill='x', padx=20, pady=(10, 0))
    tk.Label(card, text=title, font=('Segoe UI', 11, 'bold'),
             fg=colors['text_primary'], bg=colors['bg_secondary']).pack(anchor='w', padx=6, pady=(8, 4))
    inner = tk.Frame(card, bg=colors['bg_secondary'])
    inner.pack(fill='x', padx=6, pady=(0, 8))
    return inner


def _run_btn(parent, text, cmd, colors):
    return tk.Button(parent, text=text, font=('Segoe UI', 10, 'bold'),
                     bg=colors['accent_cyan'], fg=colors['bg_primary'],
                     activebackground=colors['accent_purple'], relief='flat',
                     cursor='hand2', command=cmd, padx=14, pady=8)


# ═══════════════════════════════════════════════════════════════════════════
# Sub-tab 1: Cryptography
# ═══════════════════════════════════════════════════════════════════════════

def _build_crypto_tab(parent, gui_instance, colors):
    """Cryptography sub-tab (SSL/TLS, JWT, cipher analysis)."""

    # ── Target ──────────────────────────────────────────────────────────────
    tgt = _section(parent, "🎯 Target (HTTPS URL / API Endpoint)", colors)
    tgt.grid_columnconfigure(0, weight=1)
    _entry(tgt, gui_instance.crypto_target_var, colors).grid(row=0, column=0, sticky='ew', pady=4)

    # ── Tool Selection ───────────────────────────────────────────────────────
    tools = _section(parent, "🔧 Tools", colors)
    tools.grid_columnconfigure(0, weight=1)
    tools.grid_columnconfigure(1, weight=1)

    CRYPTO_TOOLS = [
        ('sslscan',  '🔍 SSLScan — cipher suite & protocol tester',  'sslscan_var'),
        ('testssl',  '📋 TestSSL.sh — comprehensive TLS audit',        'testssl_var'),
        ('sslyze',   '🔬 SSLyze — Python TLS scanner (py lib)',         'sslyze_var'),
        ('jwt_tool', '🎫 JWT Tool — token algorithm & secret attacks',  'jwt_tool_var'),
    ]
    for i, (tid, label, varname) in enumerate(CRYPTO_TOOLS):
        var = getattr(gui_instance, varname, tk.BooleanVar(value=(i < 2)))
        setattr(gui_instance, varname, var)
        cb = tk.Checkbutton(tools, text=label, variable=var,
                            font=('Segoe UI', 9),
                            bg=colors['bg_secondary'], fg=colors['text_primary'],
                            selectcolor=colors['bg_tertiary'],
                            activebackground=colors['bg_secondary'])
        cb.grid(row=i // 2, column=i % 2, sticky='w', pady=2, padx=4)

    # ── JWT Token ────────────────────────────────────────────────────────────
    jwt_sec = _section(parent, "🎫 JWT Token (optional — paste raw token for analysis)", colors)
    _entry(jwt_sec, gui_instance.crypto_jwt_token_var, colors).pack(fill='x', pady=2)

    # ── Check Options ────────────────────────────────────────────────────────
    opts = _section(parent, "✅ Check Categories", colors)
    CHECK_OPTS = [
        ('opt_check_tls_version',  '☑ Old TLS (1.0/1.1)',           True),
        ('opt_check_weak_cipher',  '☑ Weak ciphers (RC4/DES/3DES)', True),
        ('opt_check_cert_expiry',  '☑ Certificate expiry',          True),
        ('opt_check_sha1_md5',     '☑ SHA1/MD5 cert fingerprint',   True),
        ('opt_check_hsts',         '☑ HSTS header missing',         True),
        ('opt_check_jwt_alg',      '☑ JWT algorithm confusion/none',True),
        ('opt_check_short_key',    '☑ Short RSA key (<2048)',        True),
    ]
    for row_i, (varname, label, default) in enumerate(CHECK_OPTS):
        var = getattr(gui_instance, varname, tk.BooleanVar(value=default))
        setattr(gui_instance, varname, var)
        tk.Checkbutton(opts, text=label, variable=var,
                       font=('Segoe UI', 9), bg=colors['bg_secondary'],
                       fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
                       activebackground=colors['bg_secondary']).pack(anchor='w', pady=1)

    # ── Action Buttons ────────────────────────────────────────────────────────
    btn_row = tk.Frame(parent, bg=colors['bg_secondary'])
    btn_row.pack(fill='x', padx=26, pady=14)
    _run_btn(btn_row, '▶ Run Crypto Analysis',
             lambda: gui_instance.start_crypto_scan('crypto'), colors).pack(side='left', padx=(0, 8))
    _run_btn(btn_row, '🤖 AI Analyze Results',
             lambda: gui_instance.crypto_ai_analyze('crypto'), colors).pack(side='left')


# ═══════════════════════════════════════════════════════════════════════════
# Sub-tab 2: Cryptocurrency
# ═══════════════════════════════════════════════════════════════════════════

def _build_coin_tab(parent, gui_instance, colors):
    """Cryptocurrency sub-tab (private key leak, exchange API, open RPC)."""

    # ── Target ──────────────────────────────────────────────────────────────
    tgt = _section(parent, "🎯 Target (URL / Repo Directory / API Endpoint)", colors)
    tgt.grid_columnconfigure(0, weight=1)
    tgt.grid_columnconfigure(1, weight=0)
    _entry(tgt, gui_instance.coin_target_var, colors).grid(row=0, column=0, sticky='ew', pady=4, padx=(0, 8))
    tk.Button(tgt, text='📁', font=('Segoe UI', 10), bg=colors['bg_tertiary'],
              fg=colors['text_primary'], relief='flat', cursor='hand2', padx=8, pady=6,
              command=lambda: _pick_dir(gui_instance.coin_target_var)).grid(row=0, column=1)

    # ── Tool Selection ───────────────────────────────────────────────────────
    tools = _section(parent, "🔧 Secret Scanning Tools", colors)
    COIN_TOOLS = [
        ('gitleaks',       '🔍 GitLeaks — git history secret scanner',       'coin_gitleaks_var'),
        ('trufflehog',     '🐽 TruffleHog — entropy-based secret finder',    'coin_trufflehog_var'),
        ('detect_secrets', '🕵 detect-secrets (pip) — pre-commit scanner',   'coin_detect_secrets_var'),
    ]
    for tid, label, varname in COIN_TOOLS:
        var = getattr(gui_instance, varname, tk.BooleanVar(value=True))
        setattr(gui_instance, varname, var)
        tk.Checkbutton(tools, text=label, variable=var,
                       font=('Segoe UI', 9), bg=colors['bg_secondary'],
                       fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
                       activebackground=colors['bg_secondary']).pack(anchor='w', pady=2)

    # ── Specific Checks ──────────────────────────────────────────────────────
    chk_sec = _section(parent, "✅ Specific Leak Patterns", colors)
    LEAK_OPTS = [
        ('opt_privkey_hex',    '☑ Private key (hex 64-char pattern)',        True),
        ('opt_mnemonic',       '☑ BIP-39 mnemonic phrase (12/24 words)',     True),
        ('opt_exchange_api',   '☑ Exchange API keys (Binance/Coinbase/OKX)', True),
        ('opt_open_rpc',       '☑ Open Ethereum RPC (eth_accounts/eth_call)',True),
        ('opt_wallet_addr',    '☑ Wallet address exposure in response body', False),
    ]
    for varname, label, default in LEAK_OPTS:
        var = getattr(gui_instance, varname, tk.BooleanVar(value=default))
        setattr(gui_instance, varname, var)
        tk.Checkbutton(chk_sec, text=label, variable=var,
                       font=('Segoe UI', 9), bg=colors['bg_secondary'],
                       fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
                       activebackground=colors['bg_secondary']).pack(anchor='w', pady=1)

    # ── Action Buttons ────────────────────────────────────────────────────────
    btn_row = tk.Frame(parent, bg=colors['bg_secondary'])
    btn_row.pack(fill='x', padx=26, pady=14)
    _run_btn(btn_row, '▶ Run Crypto Currency Scan',
             lambda: gui_instance.start_crypto_scan('crypto_coin'), colors).pack(side='left', padx=(0, 8))
    _run_btn(btn_row, '🤖 AI Analyze',
             lambda: gui_instance.crypto_ai_analyze('crypto_coin'), colors).pack(side='left')


# ═══════════════════════════════════════════════════════════════════════════
# Sub-tab 3: Blockchain (Smart Contract)
# ═══════════════════════════════════════════════════════════════════════════

def _build_blockchain_tab(parent, gui_instance, colors):
    """Blockchain / Smart Contract sub-tab (Slither, Mythril, Echidna)."""

    # ── Target ──────────────────────────────────────────────────────────────
    tgt = _section(parent, "🎯 Target (.sol file path or Contract Address 0x...)", colors)
    tgt.grid_columnconfigure(0, weight=1)
    tgt.grid_columnconfigure(1, weight=0)
    _entry(tgt, gui_instance.blockchain_target_var, colors).grid(
        row=0, column=0, sticky='ew', pady=4, padx=(0, 8))
    tk.Button(tgt, text='📄', font=('Segoe UI', 10), bg=colors['bg_tertiary'],
              fg=colors['text_primary'], relief='flat', cursor='hand2', padx=8, pady=6,
              command=lambda: _pick_sol(gui_instance.blockchain_target_var)).grid(row=0, column=1)

    # ── Etherscan / RPC ──────────────────────────────────────────────────────
    api_sec = _section(parent, "🔗 On-Chain Config (for contract address scan)", colors)
    api_sec.grid_columnconfigure(1, weight=1)

    _label(api_sec, 'Etherscan API Key:', colors=colors).grid(row=0, column=0, sticky='w', pady=4, padx=(0, 8))
    _entry(api_sec, gui_instance.etherscan_key_var, colors).grid(row=0, column=1, sticky='ew')

    _label(api_sec, 'Infura / RPC URL:', colors=colors).grid(row=1, column=0, sticky='w', pady=4, padx=(0, 8))
    _entry(api_sec, gui_instance.rpc_url_var, colors).grid(row=1, column=1, sticky='ew')

    tk.Label(api_sec, text='ℹ  Leave blank for local .sol file scan only',
             font=('Segoe UI', 8), fg=colors.get('text_secondary', '#888'),
             bg=colors['bg_secondary']).grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 4))

    # ── Tool Selection ───────────────────────────────────────────────────────
    tools = _section(parent, "🔧 Analysis Tools (run in venv_blockchain/)", colors)
    CHAIN_TOOLS = [
        ('slither',  '🐍 Slither — Solidity static analyzer',         'chain_slither_var'),
        ('mythril',  '🔥 Mythril — symbolic execution / vuln finder', 'chain_mythril_var'),
        ('echidna',  '🦔 Echidna — property-based fuzzer',            'chain_echidna_var'),
    ]
    for tid, label, varname in CHAIN_TOOLS:
        var = getattr(gui_instance, varname, tk.BooleanVar(value=(tid != 'echidna')))
        setattr(gui_instance, varname, var)
        tk.Checkbutton(tools, text=label, variable=var,
                       font=('Segoe UI', 9), bg=colors['bg_secondary'],
                       fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
                       activebackground=colors['bg_secondary']).pack(anchor='w', pady=2)

    # ── Vuln Categories ──────────────────────────────────────────────────────
    vuln_sec = _section(parent, "✅ Vulnerability Categories", colors)
    VULN_CATS = [
        ('opt_reentrancy',      '☑ Reentrancy',                     True),
        ('opt_int_overflow',    '☑ Integer Overflow/Underflow',      True),
        ('opt_tx_origin',       '☑ tx.origin Authentication',        True),
        ('opt_unchecked_ret',   '☑ Unchecked return values',         True),
        ('opt_selfdestruct',    '☑ Self-destruct abuse',             True),
        ('opt_flash_loan',      '☑ Flash loan / price manipulation', False),
        ('opt_access_ctrl',     '☑ Access control issues',           True),
    ]
    vuln_cols = tk.Frame(vuln_sec, bg=colors['bg_secondary'])
    vuln_cols.pack(fill='x')
    for i, (varname, label, default) in enumerate(VULN_CATS):
        var = getattr(gui_instance, varname, tk.BooleanVar(value=default))
        setattr(gui_instance, varname, var)
        tk.Checkbutton(vuln_cols, text=label, variable=var,
                       font=('Segoe UI', 9), bg=colors['bg_secondary'],
                       fg=colors['text_primary'], selectcolor=colors['bg_tertiary'],
                       activebackground=colors['bg_secondary']).grid(
            row=i // 2, column=i % 2, sticky='w', pady=1, padx=4)

    # ── Echidna timeout ──────────────────────────────────────────────────────
    ech_row = tk.Frame(parent, bg=colors['bg_secondary'])
    ech_row.pack(anchor='w', padx=26, pady=(4, 0))
    _label(ech_row, '⏱ Echidna timeout (sec):', colors=colors).pack(side='left', padx=(0, 8))
    tk.Spinbox(ech_row, from_=10, to=600, textvariable=gui_instance.echidna_timeout_var,
               width=5, font=('Segoe UI', 10), bg=colors['bg_tertiary'],
               fg=colors['text_primary'], relief='flat', bd=4).pack(side='left')

    # ── Action Buttons ────────────────────────────────────────────────────────
    btn_row = tk.Frame(parent, bg=colors['bg_secondary'])
    btn_row.pack(fill='x', padx=26, pady=14)
    _run_btn(btn_row, '▶ Run Contract Analysis',
             lambda: gui_instance.start_crypto_scan('blockchain'), colors).pack(side='left', padx=(0, 8))
    _run_btn(btn_row, '🤖 AI Analyze',
             lambda: gui_instance.crypto_ai_analyze('blockchain'), colors).pack(side='left')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _pick_dir(var):
    d = filedialog.askdirectory()
    if d:
        var.set(d)


def _pick_sol(var):
    f = filedialog.askopenfilename(filetypes=[('Solidity', '*.sol'), ('All', '*.*')])
    if f:
        var.set(f)


# ═══════════════════════════════════════════════════════════════════════════
# RESULTS OUTPUT (shared across all 3 sub-tabs)
# ═══════════════════════════════════════════════════════════════════════════

def _build_results_panel(parent, gui_instance, colors):
    """Scrollable results / findings panel."""

    res_frame = tk.Frame(parent, bg=colors['bg_secondary'], relief='flat', bd=0)
    res_frame.pack(fill='both', expand=True, padx=20, pady=(10, 16))

    # Summary bar
    summary_row = tk.Frame(res_frame, bg=colors['bg_secondary'])
    summary_row.pack(fill='x', pady=(6, 4))

    gui_instance.crypto_severity_labels = {}
    for sev, color, icon in [
        ('critical', '#ef4444', '🔴'),
        ('high',     '#f97316', '🟠'),
        ('medium',   '#eab308', '🟡'),
        ('low',      '#22c55e', '🟢'),
        ('info',     '#94a3b8', 'ℹ'),
    ]:
        lbl = tk.Label(summary_row, text=f'{icon} {sev.capitalize()}: 0',
                       font=('Segoe UI', 9, 'bold'), fg=color,
                       bg=colors['bg_secondary'])
        lbl.pack(side='left', padx=(0, 16))
        gui_instance.crypto_severity_labels[sev] = lbl

    # Progress / status label
    gui_instance.crypto_status_label = tk.Label(
        res_frame, text='Ready', font=('Segoe UI', 9),
        fg=colors['text_secondary'], bg=colors['bg_secondary'])
    gui_instance.crypto_status_label.pack(anchor='w', pady=(0, 4))

    # Console output
    from tkinter import scrolledtext
    gui_instance.crypto_console = scrolledtext.ScrolledText(
        res_frame, font=('Consolas', 9), bg='#0d1117', fg='#e6edf3',
        relief='flat', bd=0, height=18, wrap='word',
        state='disabled')
    gui_instance.crypto_console.pack(fill='both', expand=True)

    # Export row
    export_row = tk.Frame(res_frame, bg=colors['bg_secondary'])
    export_row.pack(fill='x', pady=(8, 0))
    tk.Button(export_row, text='📥 Export JSON', font=('Segoe UI', 9),
              bg=colors['bg_tertiary'], fg=colors['text_primary'],
              relief='flat', cursor='hand2', padx=10, pady=6,
              command=lambda: gui_instance.crypto_export_report('json')).pack(side='left', padx=(0, 8))
    tk.Button(export_row, text='📄 Export PDF', font=('Segoe UI', 9),
              bg=colors['bg_tertiary'], fg=colors['text_primary'],
              relief='flat', cursor='hand2', padx=10, pady=6,
              command=lambda: gui_instance.crypto_export_report('pdf')).pack(side='left')


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def setup_crypto_blockchain_tab(parent, gui_instance):
    """
    Build the full Crypto & Blockchain Analysis tab.
    Called from emyuel_gui.py during tab setup.
    """
    colors = gui_instance.colors

    # ── Init shared vars ────────────────────────────────────────────────────
    _init_vars(gui_instance)

    # ── Scrollable outer wrapper ────────────────────────────────────────────
    try:
        scrollable_frame, _ = gui_instance.create_scrollable_frame(parent)
    except Exception:
        scrollable_frame = tk.Frame(parent, bg=colors['bg_primary'])
        scrollable_frame.pack(fill='both', expand=True)

    # ── Page header ─────────────────────────────────────────────────────────
    header = tk.Frame(scrollable_frame, bg=colors['bg_secondary'])
    header.pack(fill='x', padx=20, pady=(16, 8))
    tk.Label(header, text='🔐 Crypto & Blockchain Analysis',
             font=('Segoe UI', 14, 'bold'),
             fg=colors['text_primary'], bg=colors['bg_secondary']).pack(anchor='w', padx=6, pady=(8, 2))
    tk.Label(header,
             text='Cryptography audit · Cryptocurrency secret scan · Smart contract vulnerability analysis',
             font=('Segoe UI', 9), fg=colors['text_secondary'],
             bg=colors['bg_secondary']).pack(anchor='w', padx=6, pady=(0, 8))

    # ── Inner notebook (3 sub-tabs) ──────────────────────────────────────────
    style = ttk.Style()
    style.configure('CryptoNB.TNotebook', background=colors['bg_primary'],
                    tabmargins=[2, 2, 2, 0])
    style.configure('CryptoNB.TNotebook.Tab',
                    font=('Segoe UI', 10, 'bold'),
                    padding=[14, 6])

    inner_nb = ttk.Notebook(scrollable_frame, style='CryptoNB.TNotebook')
    inner_nb.pack(fill='x', padx=20, pady=(0, 6))

    def _sub(icon, title):
        f = tk.Frame(inner_nb, bg=colors['bg_secondary'])
        inner_nb.add(f, text=f'{icon}  {title}')
        return f

    crypto_frame     = _sub('🔏', 'Cryptography')
    coin_frame       = _sub('₿',  'Cryptocurrency')
    blockchain_frame = _sub('⛓',  'Blockchain')

    _build_crypto_tab(crypto_frame, gui_instance, colors)
    _build_coin_tab(coin_frame, gui_instance, colors)
    _build_blockchain_tab(blockchain_frame, gui_instance, colors)

    # ── Results panel (shared) ───────────────────────────────────────────────
    _build_results_panel(scrollable_frame, gui_instance, colors)


def _init_vars(gui_instance):
    """Initialise tk.Var attributes on gui_instance (idempotent)."""
    import tkinter as tk

    defaults = {
        # Shared targets
        'crypto_target_var':     (tk.StringVar, 'https://'),
        'coin_target_var':       (tk.StringVar, ''),
        'blockchain_target_var': (tk.StringVar, ''),
        # JWT
        'crypto_jwt_token_var':  (tk.StringVar, ''),
        # Blockchain API keys
        'etherscan_key_var':     (tk.StringVar, ''),
        'rpc_url_var':           (tk.StringVar, 'https://mainnet.infura.io/v3/YOUR_KEY'),
        # Echidna timeout
        'echidna_timeout_var':   (tk.IntVar, 60),
    }
    for attr, (vtype, default) in defaults.items():
        if not hasattr(gui_instance, attr):
            setattr(gui_instance, attr, vtype(value=default))
