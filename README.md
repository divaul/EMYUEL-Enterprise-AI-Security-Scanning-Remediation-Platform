# EMYUEL - Enterprise Security Scanning & Remediation Platform

<div align="center">

![EMYUEL Logo](docs/assets/logo.png)

**LLM-Powered Security Scanning with Multi-Provider Support**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

[Documentation](docs/) | [Quick Start](#quick-start) | [Architecture](docs/ARCHITECTURE.md) | [API Reference](docs/API_REFERENCE.md)

</div>

## 🚀 Overview

EMYUEL is an enterprise-grade security scanning and remediation platform that leverages Large Language Models (LLMs) to provide intelligent vulnerability detection and code-level remediation suggestions. Unlike traditional security scanners, EMYUEL uses advanced AI to perform data flow analysis, detect complex multi-step vulnerabilities, and generate actionable remediation patches.

### Key Features

- **🖥️ Dual Interface** - Feature-rich CLI with Rich terminal UI + Modern GUI with Tkinter
- **🤖 Multi-LLM Provider Support** - OpenAI GPT-4, Google Gemini Pro, Anthropic Claude 3 with automatic fallback
- **� Robust API Key Management** - Auto-detection & recovery for quota limits, rate limits, invalid/expired keys
- **⏸️ Pause/Resume Capability** - Save scan state and resume from exact checkpoint
- **📄 Professional Reports** - JSON (machine-readable), HTML (interactive), PDF (executive summary)
- **�🔍 Advanced Vulnerability Detection** - Data flow analysis, multi-step vulnerability chains, privilege escalation
- **📊 CVSS v3 Scoring** - Automatic severity scoring for all findings
- **🛠️ Code-Level Remediation** - AI-generated patch suggestions with code examples
- **🔐 Enterprise Security** - RBAC, SSO/SAML, immutable audit logs
- **📈 Compliance Reporting** - OWASP Top 10, PCI-DSS, SOC 2 templates
- **🔌 Rich Integrations** - Jira, Linear, ServiceNow, Slack, GitHub Actions, GitLab CI, Jenkins
- **☁️ Flexible Deployment** - Docker Compose, Kubernetes (Helm), Cloud (Terraform)

## 🏗️ Architecture

EMYUEL uses a **microservices architecture** for scalability and maintainability:

```
┌──────────────────────────────────────────────┐
│          User Interfaces                     │
│  ┌──────────────┐      ┌──────────────┐     │
│  │ CLI (Rich)   │      │ GUI (Tkinter)│     │
│  └──────────────┘      └──────────────┘     │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────┐
│          Core Libraries                      │
│  ┌──────────────┐  ┌──────────────┐         │
│  │  API Key     │  │    State     │         │
│  │  Manager     │  │   Manager    │         │
│  └──────────────┘  └──────────────┘         │
│  ┌──────────────────────────────────┐       │
│  │    Report Generator              │       │
│  │  (JSON/HTML/PDF)                 │       │
│  └──────────────────────────────────┘       │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────┐
│          LLM Orchestrator                    │
│      Provider Abstraction Layer              │
└────────────────┬─────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐  ┌────▼────┐  ┌───▼────┐
│OpenAI │  │ Gemini  │  │ Claude │
│GPT-4  │  │  Pro    │  │   3    │
└───────┘  └─────────┘  └────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ 
- API key for at least one LLM provider (OpenAI, Google AI, or Anthropic)
- (Optional) Docker & Docker Compose for containerized deployment

### Installation

#### Quick Setup (Windows)

```batch
# Navigate to project directory
cd c:\Users\divau\Documents\cyber\emyuel

# Run setup script
setup.bat

# Activate virtual environment
venv\Scripts\activate.bat
```

#### Quick Setup (Linux)

```bash
# Navigate to project directory
cd ~/emyuel

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

#### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate.bat
# Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Your First Scan

#### CLI Mode

```bash
# Full scan with default provider
python -m cli.emyuel_cli scan --target /path/to/your/code

# Targeted scan with specific modules
python -m cli.emyuel_cli scan \
  --target /path/to/code \
  --modules sqli,xss,ssrf \
  --provider openai \
  --profile comprehensive

# Configure API key
python -m cli.emyuel_cli config --provider openai
```

#### GUI Mode

```bash
# Launch graphical interface
python -m gui.emyuel_gui
```

Then:
1. Click "Browse" to select target directory
2. Choose scan mode (Full/Targeted)
3. Select LLM provider and profile
4. Click "Start Scan"

See [QUICKSTART.md](QUICKSTART.md) for detailed examples and [DOKUMENTASI_PROGRAM.md](DOKUMENTASI_PROGRAM.md) for comprehensive documentation in Bahasa Indonesia.

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Program Documentation (Bahasa Indonesia)](DOKUMENTASI_PROGRAM.md)** - Comprehensive guide in Indonesian
- **[Implementation Walkthrough](.gemini/antigravity/brain/3bec1fec-09d3-4276-b9ca-fff91f7c3822/walkthrough.md)** - Detailed implementation overview

### Technical Documentation
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Integration Guides](docs/INTEGRATION_GUIDES.md)
- [Development Setup](docs/DEVELOPMENT.md)
- [Support & SLA](docs/SUPPORT.md)

## 🔧 Configuration

### LLM Provider Configuration

EMYUEL supports multiple LLM providers with automatic fallback:

```yaml
# config.yaml
llm:
  primary_provider: openai  # openai, gemini, or claude
  fallback_enabled: true
  providers:
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4-turbo-preview
    gemini:
      api_key: ${GOOGLE_AI_API_KEY}
      model: gemini-pro
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-3-opus-20240229
```

### Scan Profiles

```yaml
# Quick Scan (5-10 minutes)
scan:
  profile: quick
  detectors:
    - injection
    - xss
  depth: shallow

# Comprehensive Scan (30-60 minutes)
scan:
  profile: comprehensive
  detectors: all
  depth: deep
  dynamic_analysis: true
```

See [CONFIGURATION.md](docs/CONFIGURATION.md) for full reference.

## �️ User Interfaces

### CLI Mode (Command-Line Interface)

EMYUEL CLI provides a feature-rich terminal interface powered by the **Rich** library:

**Features:**
- 🎨 Colored output with progress bars and spinners
- 📊 Real-time scan progress tracking
- 📋 Interactive table displays for results
- 🔧 Complete command structure (scan, resume, list, report, config)
- 💬 Interactive prompts for API key recovery

**Commands:**
```bash
# Start new scan
python -m cli.emyuel_cli scan --target /path/to/code

# Targeted scan
python -m cli.emyuel_cli scan --target /path --modules sqli,xss,ssrf

# Pause and resume
# Press Ctrl+C to pause, then:
python -m cli.emyuel_cli resume --scan-id scan_20260207_184500

# List resumable scans
python -m cli.emyuel_cli list

# Generate reports
python -m cli.emyuel_cli report --scan-id scan_123 --format all

# Configure API keys
python -m cli.emyuel_cli config --provider openai
```

### GUI Mode (Graphical User Interface)

Modern desktop application with professional design:

**Features:**
- 🎯 Intuitive point-and-click interface
- 📁 File browser for target selection
- 📈 Real-time progress bar and console logging
- 🔴🟠🟡🟢 Color-coded severity statistics (Critical/High/Medium/Low)
- ⏸️ Start/Pause/Resume controls
- 📄 One-click report generation

**Launch:**
```bash
python -m gui.emyuel_gui
```

## 🔑 API Key Error Handling

EMYUEL features robust, automatic error detection and recovery for API key issues:

### Auto-Detected Errors

**Quota Exceeded**
```
[DETECTED] Quota exceeded for primary key
[ACTION] Switching to backup key automatically
[RESULT] ✓ Scan continues without interruption
```

**Rate Limiting**
```
[DETECTED] Rate limit exceeded
[ACTION] Exponential backoff: waiting 5 seconds...
[OPTION] Continue waiting or enter new key? [w/k]:
```

**Invalid/Expired Key**
```
[ERROR] Invalid API key detected
[PROMPT] Enter valid OpenAI API key: _
[ACTION] Validating new key...
[RESULT] ✓ Key is valid. Continuing scan...
```

**Permission Denied**
```
[ERROR] API key doesn't have required permissions
[OPTIONS]
  1. Enter key with appropriate permissions
  2. Switch to different provider
Your choice [1/2]: _
```

### Recovery Modes

- **CLI Mode**: Interactive terminal prompts with Rich formatting
- **GUI Mode**: Dialog boxes with user-friendly error messages
- **Automatic Failover**: Switches to backup keys when available
- **Provider Fallback**: Can switch between OpenAI/Gemini/Claude

## ⏸️ Pause & Resume

Save scan state and resume from exact checkpoint:

### Features
- 💾 Automatic state saving to `~/.emyuel/states/`
- 📍 Resume from exact file and line number
- 📊 Progress tracking (files scanned, modules completed)
- 🔄 List all resumable scans
- 🗑️ Auto-cleanup of old state files

### Usage

**CLI:**
```bash
# During scan, press Ctrl+C to pause
^C
Scan interrupted by user
State saved. Resume with: emyuel resume --scan-id scan_20260207_184500

# Resume later
python -m cli.emyuel_cli resume --scan-id scan_20260207_184500
```

**GUI:**
- Click "⏸ Pause" button to pause
- Click "⏯ Resume" button to continue

## 📄 Report Generation

Generate professional security reports in multiple formats:

### Supported Formats

**JSON** - Machine-readable format for integrations
- Complete scan data
- All findings with full details
- Metadata and timestamps

**HTML** - Interactive web report
- Modern gradient design
- Severity distribution charts
- Code snippets with syntax highlighting
- Remediation recommendations
- Mobile-friendly and print-ready

**PDF** - Executive summary
- Cover page with scan info
- Vulnerability statistics tables
- Top critical findings
- Professional formatting

### Report Structure
```
reports/
└── 20260207_184500_myapp/
    ├── report.json       # Full data
    ├── report.html       # Interactive report  
    ├── report.pdf        # Executive summary
    ├── metadata.json     # Scan metadata
    └── evidence/         # Screenshots, logs
```

### Generate Reports
```bash
# All formats
python -m cli.emyuel_cli report --scan-id scan_123 --format all

# Specific format
python -m cli.emyuel_cli report --scan-id scan_123 --format pdf
```

## �🔌 Integrations

### CI/CD Integration

**GitHub Actions:**
```yaml
- uses: emyuel/scan-action@v1
  with:
    api-key: ${{ secrets.EMYUEL_API_KEY }}
    fail-on-high: true
```

**GitLab CI:**
```yaml
emyuel_scan:
  image: emyuel/cli:latest
  script:
    - emyuel scan --repo . --fail-on high
```

See [integration templates](integrations/ci-cd/) for more examples.

### Third-Party Tools

- **Jira** - Auto-create tickets for vulnerabilities
- **Slack** - Real-time scan notifications
- **ServiceNow** - Incident management integration
- **Linear** - Issue tracking

See [INTEGRATION_GUIDES.md](docs/INTEGRATION_GUIDES.md) for setup instructions.

## 🛡️ Security & Compliance

- **Authentication**: JWT, SSO (SAML/OIDC)
- **Authorization**: Role-Based Access Control (RBAC)
- **Audit Logs**: Immutable, append-only logs
- **Data Encryption**: At-rest and in-transit
- **Compliance**: OWASP, PCI-DSS, SOC 2 reporting

## 📊 Supported Vulnerabilities

| Category | Detection | Remediation |
|----------|-----------|-------------|
| SQL Injection | ✅ | ✅ |
| XSS (Reflected, Stored, DOM) | ✅ | ✅ |
| SSRF | ✅ | ✅ |
| RCE | ✅ | ✅ |
| Authentication Bypass | ✅ | ✅ |
| Authorization Issues | ✅ | ✅ |
| Privilege Escalation | ✅ | ✅ |
| Deserialization | ✅ | ✅ |
| Path Traversal | ✅ | ✅ |
| CSRF | ✅ | ✅ |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Community Support**: [GitHub Discussions](https://github.com/your-org/emyuel/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/your-org/emyuel/issues)
- **Enterprise Support**: [Contact Sales](https://emyuel.io/contact)

### Support Tiers

| Tier | Response Time | Channels |
|------|--------------|----------|
| Community | Best effort | GitHub |
| Professional | 24 hours | Email, Slack |
| Enterprise | 4 hours | Email, Slack, Phone |

See [SUPPORT.md](docs/SUPPORT.md) for SLA details.

## 🙏 Acknowledgments

- Inspired by Shannon AI and modern AI-powered security tools
- Built with Claude, GPT-4, and Gemini
- Thanks to the open-source security community

---

<div align="center">

Made with ❤️ by the EMYUEL Team

[Website](https://emyuel.io) • [Documentation](docs/) • [Twitter](https://twitter.com/emyuel)

</div>
