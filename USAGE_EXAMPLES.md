# EMYUEL Usage Examples - URLs and Scan All

## CLI Examples

### Scan URL (Website)

```bash
# Full scan on website (all vulnerabilities)
python -m cli.emyuel_cli scan --target https://example.com --all

# Targeted scan on website (specific modules)
python -m cli.emyuel_cli scan --target https://myapp.com --modules sqli,xss

# Quick scan on website
python -m cli.emyuel_cli scan --target https://example.com --all --profile quick

# Comprehensive scan
python -m cli.emyuel_cli scan --target https://example.com --all --profile comprehensive
```

### Scan Local Directory

```bash
# Full scan on local directory
python -m cli.emyuel_cli scan --target /var/www/myapp --all

# Scan current directory
python -m cli.emyuel_cli scan --target . --all

# Targeted scan
python -m cli.emyuel_cli scan --target ~/projects/webapp --modules sqli,xss,csrf
```

### Natural Language Queries

```bash
# English
python -m cli.emyuel_cli query "scan all vulnerabilities in https://example.com"
python -m cli.emyuel_cli query "find XSS in login page"
python -m cli.emyuel_cli query "check security issues in website"

# Indonesian
python -m cli.emyuel_cli query "cari semua celah keamanan"
python -m cli.emyuel_cli query "scan seluruh website"
```

### With Different Providers

```bash
# OpenAI
python -m cli.emyuel_cli scan --target https://example.com --all --provider openai

# Google Gemini
python -m cli.emyuel_cli scan --target https://example.com --all --provider gemini

# Anthropic Claude
python -m cli.emyuel_cli scan --target https://example.com --all --provider claude
```

---

## GUI Usage

### Scan URL

**Tab: Advanced Scan**

1. Enter URL in target field:
   ```
   https://example.com
   ```

2. Click "🌐 Scan All (Full Website/Directory)" button
   - This activates full scan mode
   - Status bar will show "Mode: Full Scan (All Vulnerabilities)"

3. Select provider (OpenAI/Gemini/Claude)

4. Select profile (Quick/Standard/Comprehensive)

5. Click "▶ Start Scan"

**What happens:**
- GUI auto-detects it's a URL
- Shows "🌐 Web Target" indicator
- Console output shows:
  ```
  [INFO] Detected web target: https://example.com
  [MODE] Set to FULL SCAN (All Modules)
  [SCAN] Starting Full Scan (All Modules) on Web target
  [TARGET] https://example.com
  ```

### Scan Local Directory

**Tab: Advanced Scan**

1. Option A: Type path directly:
   ```
   /var/www/myapp
   ```

2. Option B: Click "📁 Browse" and select directory

3. Click "🌐 Scan All" button for full scan

4. Click "▶ Start Scan"

**What happens:**
- GUI auto-detects it's a directory
- Shows "📁 Local Directory" indicator
- Full scan mode activated

### Natural Language (Quick Scan Tab)

1. Type query:
   ```
   scan all vulnerabilities in https://example.com
   ```

2. Click "Analyze"

3. Review parsed parameters

4. Click "▶ Start Scan"

---

## All Vulnerability Types Scanned

When using `--all` flag or "Scan All" button, EMYUEL will scan for:

✅ **Injection Flaws:**
- SQL Injection (SQLi)
- Command Injection
- LDAP Injection
- XML Injection

✅ **Cross-Site Scripting (XSS):**
- Reflected XSS
- Stored XSS
- DOM-based XSS

✅ **Server-Side Request Forgery (SSRF)**

✅ **Remote Code Execution (RCE)**

✅ **Cross-Site Request Forgery (CSRF)**

✅ **Path Traversal / Directory Traversal**

✅ **Authentication & Authorization:**
- Broken Authentication
- Broken Access Control
- Privilege Escalation

✅ **Sensitive Data Exposure:**
- Hardcoded Credentials
- API Keys in Source Code
- Information Disclosure

✅ **Security Misconfiguration**

✅ **Insecure Deserialization**

✅ **Using Components with Known Vulnerabilities**

✅ **Insufficient Logging & Monitoring**

---

## Quick Reference

| Action | Command | GUI |
|--------|---------|-----|
| Scan URL (all) | `scan --target https://... --all` | Enter URL + Click "Scan All" |
| Scan directory (all) | `scan --target /path --all` | Browse + Click "Scan All" |
| Targeted scan | `scan --target ... --modules sqli,xss` | Select "Targeted Scan" mode |
| Natural language | `query "scan all issues"` | Quick Scan tab → Type query |
| Check target type | Auto-detected | Shows indicator (🌐/📁) |

---

## Tips

💡 **URL Format:**
- Always include protocol: `https://example.com` not `example.com`
- Can include paths: `https://example.com/admin`
- Can include ports: `https://example.com:8080`

💡 **Directory Format:**
- Absolute path: `/var/www/myapp`
- Relative path: `./myapp` or `.` (current)
- Windows path: `C:\inetpub\wwwroot\myapp`

💡 **Full Scan:**
- Use `--all` flag in CLI for explicit full scan
- Use "Scan All" button in GUI
- Or simply omit `--modules` argument

💡 **Performance:**
- Full scans take longer but are more thorough
- Use `--profile quick` for faster results
- Use `--profile comprehensive` for maximum coverage
