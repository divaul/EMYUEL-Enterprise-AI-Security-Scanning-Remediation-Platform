# Dokumentasi Program EMYUEL

## 🎯 Gambaran Umum

**EMYUEL** (Enterprise Multi-LLM Security Scanner) adalah platform keamanan siber berbasis AI yang dirancang untuk melakukan penetration testing otomatis pada aplikasi web dan kode sumber. Program ini menggunakan Large Language Models (LLM) dari berbagai provider untuk menganalisis kerentanan keamanan secara mendalam.

### Tujuan Utama

- **Otomasi Security Testing**: Menggantikan penetration testing manual yang memakan waktu
- **Deteksi Dini**: Menemukan kerentanan sebelum di-deploy ke production
- **Analisis Cerdas**: Menggunakan AI untuk deteksi vulnerability yang kompleks
- **Laporan Professional**: Menghasilkan report berbagai format (JSON, HTML, PDF)

### Keunggulan

✅ **Dual Interface**: CLI (Command-Line) dan GUI (Graphical User Interface)  
✅ **Multi-Provider LLM**: OpenAI GPT-4, Google Gemini, Anthropic Claude  
✅ **Auto-Recovery**: Penanganan error API key secara otomatis  
✅ **Pause/Resume**: Kemampuan menjeda dan melanjutkan scan  
✅ **Professional Reports**: Laporan dengan desain modern dan detail  

---

## 🏗️ Arsitektur Sistem

### Komponen Utama

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│  ┌──────────────────┐      ┌──────────────────────┐    │
│  │   CLI (Rich)     │      │   GUI (Tkinter)      │    │
│  └──────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Core Libraries                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  API Key     │  │    State     │  │   Report     │  │
│  │  Manager     │  │   Manager    │  │  Generator   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              LLM Orchestrator                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   OpenAI     │  │    Gemini    │  │    Claude    │  │
│  │  Provider    │  │   Provider   │  │   Provider   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Scanner Core Engine                     │
│  (Vulnerability Detection & Analysis)                    │
└─────────────────────────────────────────────────────────┘
```

### Alur Kerja

1. **Input**: User memilih target (file/direktori/URL) melalui CLI atau GUI
2. **Initialization**: System load API keys dan konfigurasi
3. **Scanning**: 
   - Scanner membaca kode sumber
   - Mengirim ke LLM untuk analisis
   - Mendeteksi vulnerability patterns
4. **Recovery**: Jika API key error, auto-switch atau prompt user
5. **Output**: Generate laporan dalam format JSON/HTML/PDF
6. **State Management**: Save progress untuk resume capability

---

## 🚀 Instalasi dan Setup

### Persyaratan Sistem

- **Python**: 3.10 atau lebih tinggi
- **OS**: Windows, Linux, atau macOS
- **RAM**: Minimal 4GB
- **Storage**: 500MB untuk dependencies

### Langkah Instalasi

#### Windows

```batch
# 1. Clone atau download project
cd c:\Users\divau\Documents\cyber\emyuel

# 2. Jalankan script setup
setup.bat

# 3. Aktifkan virtual environment
venv\Scripts\activate.bat

# 4. Verifikasi instalasi
python -m cli.emyuel_cli --help
```

#### Linux

```bash
# 1. Clone atau download project
cd ~/emyuel

# 2. Jalankan script setup
chmod +x setup.sh
./setup.sh

# 3. Aktifkan virtual environment
source venv/bin/activate

# 4. Verifikasi instalasi
python -m cli.emyuel_cli --help
```

### Konfigurasi API Keys

EMYUEL memerlukan API key dari salah satu LLM provider:

```bash
# Metode 1: File .env
cp .env.example .env
# Edit .env dan tambahkan:
OPENAI_API_KEY=sk-your-key-here
GOOGLE_AI_API_KEY=AI-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Metode 2: CLI Configuration
python -m cli.emyuel_cli config --provider openai --key sk-xxxxx

# Metode 3: Interactive (akan prompt otomatis saat dibutuhkan)
python -m cli.emyuel_cli scan --target /path/to/code
# Program akan meminta key jika belum dikonfigurasi
```

---

## 💻 Cara Penggunaan

### Mode CLI (Command-Line Interface)

CLI mode cocok untuk:
- Otomasi dan CI/CD pipeline
- Remote server tanpa display
- Scripting dan batch processing
- Users yang prefer terminal

#### Perintah Dasar

**1. Scan Penuh (Full Scan)**
```bash
python -m cli.emyuel_cli scan --target /path/to/your/code
```

**2. Scan Tertarget (Specific Modules)**
```bash
# Hanya test SQL Injection dan XSS
python -m cli.emyuel_cli scan --target /path/to/code --modules sqli,xss

# Semua modules:
# - sqli: SQL Injection
# - xss: Cross-Site Scripting
# - ssrf: Server-Side Request Forgery
# - rce: Remote Code Execution
# - auth: Authentication/Authorization issues
# - csrf: Cross-Site Request Forgery
```

**3. Pilih Provider LLM**
```bash
# Gunakan OpenAI GPT-4
python -m cli.emyuel_cli scan --target /path --provider openai

# Gunakan Google Gemini
python -m cli.emyuel_cli scan --target /path --provider gemini

# Gunakan Anthropic Claude
python -m cli.emyuel_cli scan --target /path --provider claude
```

**4. Pilih Profile Scan**
```bash
# Quick scan (cepat, basic checks)
python -m cli.emyuel_cli scan --target /path --profile quick

# Standard scan (balanced)
python -m cli.emyuel_cli scan --target /path --profile standard

# Comprehensive scan (mendalam, semua checks)
python -m cli.emyuel_cli scan --target /path --profile comprehensive
```

**5. Pause dan Resume**
```bash
# Mulai scan, tekan Ctrl+C untuk pause
python -m cli.emyuel_cli scan --target /path/to/code
# ... scanning ...
# ^C (Ctrl+C untuk pause)
# Scan paused. State saved.

# Lihat daftar scan yang bisa di-resume
python -m cli.emyuel_cli list

# Resume scan
python -m cli.emyuel_cli resume --scan-id scan_20260207_184500
```

**6. Generate Report**
```bash
# Generate semua format (JSON, HTML, PDF)
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --format all

# Generate hanya PDF
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --format pdf

# Specify output directory
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --output-dir ./my-reports
```

**7. Konfigurasi API Keys**
```bash
# Configure OpenAI key
python -m cli.emyuel_cli config --provider openai

# Configure dengan key langsung
python -m cli.emyuel_cli config --provider openai --key sk-xxxxx

# Add backup key
python -m cli.emyuel_cli config --provider openai --backup
```

#### Output CLI

CLI menggunakan library **Rich** untuk terminal UI yang menarik:

```
🛡️ EMYUEL Security Scanner

Scan Mode: Full Scan (all modules)

Starting scan: scan_20260207_184500
Target: /home/user/myapp

Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:02:34

✓ Scan completed successfully!

╭─────────────────────────────────╮
│         Scan Summary            │
├─────────────┬───────────────────┤
│ Critical    │         2         │
│ High        │         5         │
│ Medium      │         8         │
│ Low         │         3         │
╰─────────────┴───────────────────╯

✓ Reports saved to: reports/
```

---

### Mode GUI (Graphical User Interface)

GUI mode cocok untuk:
- Desktop users
- Visual monitoring
- Interactive configuration
- Pemula yang belum familiar dengan CLI

#### Menjalankan GUI

```bash
python -m gui.emyuel_gui
```

#### Fitur GUI

**Panel Konfigurasi (Kiri)**
- 📁 **Target Selection**: Browse folder atau input manual
- 🎯 **Scan Mode**: Radio button untuk Full/Targeted scan
- 🔧 **Modules Input**: Comma-separated modules untuk targeted scan
- 🤖 **LLM Provider**: Dropdown untuk pilih OpenAI/Gemini/Claude
- ⚙️ **Scan Profile**: Dropdown untuk pilih Quick/Standard/Comprehensive
- ▶️ **Start Button**: Tombol hijau untuk mulai scan
- ⏸️ **Pause Button**: Tombol kuning untuk pause scan
- ⏯️ **Resume Button**: Tombol biru untuk resume scan

**Panel Results (Kanan)**
- 📊 **Progress Bar**: Real-time progress indicator
- 📄 **Console Log**: Scrollable log output dengan syntax highlighting
- 📈 **Statistics Cards**: Color-coded vulnerability count
  - 🔴 Critical (merah)
  - 🟠 High (oranye)
  - 🟡 Medium (kuning)
  - 🟢 Low (hijau)
- 📄 **Generate Report Button**: Create all format reports
- 📂 **Open Reports Folder Button**: Quick access ke reports directory

**Status Bar (Bawah)**
- Status real-time: "Ready", "Scanning...", "Paused", "Completed"

---

## 🔑 API Key Error Handling

EMYUEL memiliki sistem error handling yang robust untuk masalah API key.

### Skenario Error yang Ditangani

#### 1. Quota Exceeded (Kuota Habis)

**Error Messages:**
- "quota exceeded"
- "insufficient_quota"
- "billing_hard_limit_reached"

**Tindakan Otomatis:**
```
[DETECTED] Quota exceeded for OpenAI primary key
[ACTION] Switching to backup key #1...
[RESULT] ✓ Scan continues with backup key
```

Jika backup key tidak ada:
```
[ERROR] OpenAI quota exceeded
[PROMPT] Enter backup API key: _
[INPUT] sk-xxxxx
[ACTION] Validating new key...
[RESULT] ✓ Key validated. Retrying request...
```

#### 2. Rate Limit (Terlalu Banyak Request)

**Error Messages:**
- "rate_limit_exceeded"
- "too many requests"
- "429 Too Many Requests"

**Tindakan Otomatis:**
```
[DETECTED] Rate limit exceeded
[ACTION] Exponential backoff: waiting 5 seconds...
[PROMPT] Continue waiting or enter new key? [w/k]: _
```

User dapat:
- `w`: Wait (tunggu sampai rate limit reset)
- `k`: Masukkan key baru

#### 3. Invalid/Expired Key

**Error Messages:**
- "invalid_api_key"
- "authentication_error"
- "api_key_expired"

**Tindakan Otomatis:**
```
[ERROR] Invalid API key detected
[PROMPT] Enter valid OpenAI API key: _
[INPUT] sk-xxxxx
[ACTION] Testing key...
[RESULT] ✓ Key is valid. Continuing scan...
```

#### 4. Permission Denied

**Error Messages:**
- "permission_denied"
- "insufficient_permissions"

**CLI Mode:**
```bash
┌──────────────────────────────────────────────┐
│  API Key Error                               │
├──────────────────────────────────────────────┤
│  Your key doesn't have permission           │
│  to access this model.                       │
│                                              │
│  Options:                                    │
│  1. Enter key with appropriate permissions   │
│  2. Switch to different provider             │
└──────────────────────────────────────────────┘

Your choice [1/2]: _
```

**GUI Mode:**
```
┌─────────────────────────────────────┐
│  ⚠️ API Key Permission Error        │
│                                     │
│  Your API key doesn't have          │
│  permission to access GPT-4.        │
│                                     │
│  [ Enter New Key ] [ Change Model ] │
└─────────────────────────────────────┘
```

---

## ⏸️ Pause/Resume Functionality

### Cara Kerja

**State File Location:**
```
~/.emyuel/states/
├── scan_20260207_120000.json
├── scan_20260207_143000.json
└── scan_20260207_184500.json
```

**State File Structure:**
```json
{
  "scan_id": "scan_20260207_184500",
  "target": "/home/user/myapp",
  "status": "paused",
  "provider": "openai",
  "profile": "standard",
  "modules": ["sqli", "xss", "ssrf"],
  "progress": {
    "total_files": 156,
    "completed_files": 89,
    "current_file": "/home/user/myapp/api/auth.py",
    "current_line": 234,
    "modules_completed": ["sqli", "xss"],
    "current_module": "ssrf"
  },
  "findings": [...],  // Vulnerability sudah ditemukan
  "started_at": "2026-02-07T18:45:00",
  "paused_at": "2026-02-07T18:52:30"
}
```

### Penggunaan

**CLI:**
```bash
# Scan sedang berjalan...
# Tekan Ctrl+C untuk pause

^C
Scan interrupted by user
State saved. Resume with: emyuel resume --scan-id scan_20260207_184500

# List resumable scans
$ python -m cli.emyuel_cli list

╭─────────────────────────────────────────────────────────╮
│                  Resumable Scans                        │
├──────────────────┬─────────────┬──────────┬────────────┤
│ Scan ID          │ Target      │ Progress │ Started At │
├──────────────────┼─────────────┼──────────┼────────────┤
│ scan_20260207... │ /home/user  │ 89/156   │ 18:45:00   │
│                  │ /myapp      │ (57.1%)  │            │
╰──────────────────┴─────────────┴──────────┴────────────╯

# Resume
$ python -m cli.emyuel_cli resume --scan-id scan_20260207_184500

Resuming scan: scan_20260207_184500
Target: /home/user/myapp
Progress: 89/156 files (57.1%)
Resuming from: /home/user/myapp/api/auth.py:234

Scanning... ━━━━━━━━━━━╺━━━━━━━━━━ 57% 0:01:23
```

**GUI:**
- Klik tombol **⏸ Pause** untuk pause
- Klik tombol **⏯ Resume** untuk melanjutkan
- State otomatis tersimpan

---

## 📄 Report Generation

### Format Report

EMYUEL menghasilkan 3 format report:

#### 1. JSON Report

**File**: `report.json`

Format machine-readable untuk integrasi dengan tools lain.

```json
{
  "scan_id": "scan_20260207_184500",
  "target": "/home/user/myapp",
  "start_time": "2026-02-07T18:45:00",
  "end_time": "2026-02-07T18:53:45",
  "duration_seconds": 525.3,
  "files_scanned": 156,
  "total_findings": 18,
  "findings_by_severity": {
    "critical": 2,
    "high": 5,
    "medium": 8,
    "low": 3
  },
  "findings": [
    {
      "id": "VULN-001",
      "title": "SQL Injection in User Authentication",
      "type": "sqli",
      "severity": "critical",
      "cvss_score": 9.8,
      "file_path": "/home/user/myapp/api/auth.py",
      "line_number": 45,
      "code_snippet": "query = f\"SELECT * FROM users WHERE email='{email}'\"",
      "description": "User input directly concatenated into SQL query without sanitization...",
      "remediation": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE email=?', (email,))",
      "references": [
        "https://owasp.org/www-community/attacks/SQL_Injection"
      ]
    }
  ]
}
```

#### 2. HTML Report

**File**: `report.html`

Report interaktif dengan desain modern.

**Fitur:**
- 🎨 Design gradient modern (purple/blue)
- 📊 Severity bars dengan animasi
- 🔍 Detailed findings dengan code highlighting
- 📱 Responsive (mobile-friendly)
- 🖨️ Print-ready CSS
- 💡 Remediation recommendations dalam box berwarna

**Sections:**
1. **Header**: Scan ID dan title
2. **Summary Cards**: Target, Date, Duration, Files, Findings
3. **Vulnerability Distribution**: Bar charts by severity
4. **Detailed Findings**: 
   - Finding cards dengan hover effects
   - Code snippets dengan dark theme
   - CVSS scores
   - Remediation recommendations

#### 3. PDF Report

**File**: `report.pdf`

Executive summary untuk presentasi.

**Contents:**
1. **Cover Page**: EMYUEL logo dan scan info
2. **Executive Summary**: 
   - Scan metadata table
   - Vulnerability statistics table
3. **Critical Findings**: 
   - Top 5 critical vulnerabilities
   - File paths dan descriptions
4. **Footer**: Generated timestamp dan EMYUEL branding

### Report Directory Structure

```
reports/
└── 20260207_184500_myapp/
    ├── report.json           # Full data
    ├── report.html          # Interactive report
    ├── report.pdf           # Executive summary
    ├── metadata.json        # Scan metadata
    └── evidence/            # Supporting files
        ├── screenshot_1.png
        ├── payload_log.txt
        └── api_response.json
```

### Generate Report

**CLI:**
```bash
# All formats
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --format all

# Specific format
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --format pdf

# Custom output directory
python -m cli.emyuel_cli report --scan-id scan_20260207_184500 --output-dir ./custom-reports
```

**GUI:**
- Klik button **📄 Generate Report**
- Pilih output directory
- Reports akan di-generate otomatis

**Programmatic:**
```python
from libs.reporting import ReportGenerator

generator = ReportGenerator()
output_files = generator.generate_all(
    scan_results=results_dict,
    output_dir='reports',
    formats=['json', 'html', 'pdf']
)

print(f"JSON: {output_files['json']}")
print(f"HTML: {output_files['html']}")
print(f"PDF: {output_files['pdf']}")
```

---

## 🗂️ Struktur Project

```
emyuel/
├── cli/                          # Command-Line Interface
│   ├── __init__.py
│   └── emyuel_cli.py            # Main CLI with Rich
│
├── gui/                          # Graphical User Interface
│   ├── __init__.py
│   └── emyuel_gui.py            # Main GUI with Tkinter
│
├── libs/                         # Core Libraries
│   ├── api_key_manager.py       # API key error handling
│   ├── scanner_state.py         # Pause/resume state management
│   └── reporting/               # Report generation
│       ├── __init__.py
│       ├── report_generator.py
│       └── templates/
│           └── html_report_template.html
│
├── services/                     # Backend Services
│   ├── llm-orchestrator/        # LLM provider abstraction
│   │   └── providers/
│   │       ├── base.py          # Abstract interface
│   │       ├── openai_provider.py
│   │       ├── gemini_provider.py
│   │       └── claude_provider.py
│   │
│   └── scanner_core/            # Vulnerability scanner
│       └── (to be implemented)
│
├── configs/                      # Configuration files
├── database/                     # Database schemas
├── docs/                         # Documentation
├── integrations/                 # External integrations
├── monitoring/                   # Prometheus/Grafana
├── infrastructure/              # Docker/K8s configs
│
├── bin/
│   └── emyuel                   # CLI entry point
│
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── setup.bat                    # Windows setup script
├── setup.sh                     # Linux setup script
├── README.md                    # Project overview
├── QUICKSTART.md               # Quick start guide
└── DOKUMENTASI_PROGRAM.md      # This file
```

---

## 🔧 Troubleshooting

### Problem: "Python not found"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Install Python dari [python.org](https://python.org)
2. Saat install, centang "Add Python to PATH"
3. Restart terminal/command prompt
4. Test: `python --version`

---

### Problem: "Module not found"

**Symptoms:**
```
ModuleNotFoundError: No module named 'rich'
```

**Solution:**
```bash
# Pastikan virtual environment aktif
# Windows:
venv\Scripts\activate.bat

# Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Problem: "API key not configured"

**Symptoms:**
```
[ERROR] No API key found for OpenAI
```

**Solution:**

**Option 1 - Environment Variable:**
```bash
# Windows
set OPENAI_API_KEY=sk-your-key-here

# Linux
export OPENAI_API_KEY=sk-your-key-here
```

**Option 2 - CLI Config:**
```bash
python -m cli.emyuel_cli config --provider openai
```

**Option 3 - .env File:**
```bash
cp .env.example .env
# Edit .env dan tambahkan API key
```

---

### Problem: GUI tidak bisa dibuka

**Symptoms:**
```
ModuleNotFoundError: No module named '_tkinter'
```

**Solution:**

**Windows:**
- Tkinter sudah include di Python installer
- Re-install Python dan pastikan "tcl/tk and IDLE" di-check

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

### Problem: "Permission denied" saat generate report

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'reports/'
```

**Solution:**
```bash
# Buat direktori reports manual
mkdir reports

# Atau specify output directory yang writable
python -m cli.emyuel_cli report --scan-id scan_xxx --output-dir ./my-reports
```

---

### Problem: Scan sangat lambat

**Possible Causes & Solutions:**

1. **Target terlalu besar**
   - Solution: Gunakan `--profile quick` untuk scan cepat
   - Atau target scan ke specific directory saja

2. **Rate limiting dari LLM provider**
   - Solution: Tambahkan backup key dengan `config --backup`
   - Atau switch ke provider lain

3. **Network connectivity**
   - Solution: Check koneksi internet
   - Test: `curl https://api.openai.com/v1/models`

---

## 📚 Referensi API

### CLI API

```python
from cli.emyuel_cli import EMYUELCLI

cli = EMYUELCLI()
await cli.run(['scan', '--target', '/path/to/code'])
```

### API Key Manager API

```python
from libs.api_key_manager import APIKeyManager, RecoveryMode

# Initialize
manager = APIKeyManager(recovery_mode=RecoveryMode.CLI)

# Add keys
manager.add_key('openai', 'sk-xxxxx', is_primary=True)
manager.add_key('openai', 'sk-yyyyy', is_primary=False)  # backup

# Get working key
key = manager.get_key('openai')

# Handle error
try:
    response = await call_api(key)
except Exception as e:
    recovered_key = await manager.handle_error('openai', str(e))
```

### State Manager API

```python
from libs.scanner_state import StateManager, ScanState

manager = StateManager()

# Save state
state = ScanState(
    scan_id='scan_123',
    target='/path/to/code',
    status='paused',
    progress={'completed': 50, 'total': 100}
)
manager.save_state(state)

# Load state
loaded = manager.load_state('scan_123')

# List resumable
scans = manager.get_resumable_scans()
```

### Report Generator API

```python
from libs.reporting import ReportGenerator

generator = ReportGenerator()

scan_results = {
    'scan_id': 'scan_123',
    'target': '/path',
    'findings': [...],
    'total_findings': 10,
    # ...
}

# Generate all formats
output = generator.generate_all(
    scan_results=scan_results,
    output_dir='reports',
    formats=['json', 'html', 'pdf']
)
```

---

## 📞 Dukungan dan Kontribusi

### Mendapatkan Bantuan

- **Documentation**: Baca [README.md](file:///c:/Users/divau/Documents/cyber/emyuel/README.md)
- **Quick Start**: Lihat [QUICKSTART.md](file:///c:/Users/divau/Documents/cyber/emyuel/QUICKSTART.md)
- **Architecture**: Refer to [ARCHITECTURE.md](file:///c:/Users/divau/Documents/cyber/emyuel/docs/ARCHITECTURE.md)

### Melaporkan Bug

Jika menemukan bug, harap sertakan informasi:
1. Versi Python: `python --version`
2. OS dan versi
3. Langkah untuk reproduce bug
4. Error message lengkap
5. Log file jika ada

### Kontribusi

Contributions are welcome! See [CONTRIBUTING.md](file:///c:/Users/divau/Documents/cyber/emyuel/CONTRIBUTING.md)

---

## 📝 Changelog

### Version 1.0.0 (2026-02-07)

**Initial Release:**
- ✅ CLI interface dengan Rich terminal UI
- ✅ GUI interface dengan Tkinter
- ✅ API Key Manager dengan auto-recovery
- ✅ State Manager untuk pause/resume
- ✅ Report Generator (JSON/HTML/PDF)
- ✅ LLM provider abstraction (OpenAI, Gemini, Claude)
- ✅ Comprehensive documentation

---

## 📄 Lisensi

MIT License - See [LICENSE](file:///c:/Users/divau/Documents/cyber/emyuel/LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4 API
- **Google** - Gemini API
- **Anthropic** - Claude API
- **Rich** - Beautiful terminal formatting
- **Jinja2** - HTML templating
- **ReportLab** - PDF generation

---

**Dibuat dengan ❤️ oleh Tim EMYUEL**

*Terakhir diupdate: 2026-02-07*
