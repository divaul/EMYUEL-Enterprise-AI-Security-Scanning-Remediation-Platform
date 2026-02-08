# Dynamic Analysis (DAST) Support

## Current Status

EMYUEL currently focuses on **Static Application Security Testing (SAST)** using LLM-powered code analysis. Dynamic Analysis (DAST) support is **partially implemented** with hooks for future expansion.

## SAST vs DAST

### Static Analysis (SAST) - ✅ Fully Implemented

**What it does**:
- Analyzes source code without executing it
- Traces data flow from input to dangerous operations
- Detects vulnerabilities in code logic
- Provides code-level remediation suggestions

**Strengths**:
- Early detection (during development)
- Covers all code paths
- No need for running application
- Low false positives with LLM analysis

**Current Detectors**:
- SQL Injection
- XSS (Reflected, Stored, DOM-based)
- SSRF
- More planned (RCE, Auth, Deserialization, etc.)

### Dynamic Analysis (DAST) - 🚧 Planned/Partial

**What it does**:
- Tests running application
- Sends malicious payloads
- Monitors application behavior
- Detects runtime vulnerabilities

**Strengths**:
- Finds configuration issues
- Tests authentication flows
- Discovers business logic flaws
- No source code required

**Planned Features**:
- HTTP fuzzing
- Authentication testing
- Session management testing
- API endpoint discovery
- Credential stuffing detection

---

## Enabling DAST (Experimental)

### Configuration

```yaml
# configs/scanner-profiles/comprehensive.yaml

scan:
  # Enable dynamic analysis
  dynamic_analysis: true
  
  # DAST configuration
  dast:
    enabled: true
    target_url: "http://target-application.com"
    
    # Authentication
    auth:
      type: "basic"  # basic, bearer, session
      username: "test_user"
      password: "test_pass"
    
    # Scope
    scope:
      include_paths:
        - "/api/*"
        - "/app/*"
      exclude_paths:
        - "/static/*"
        - "/logout"
    
    # Testing modules
    modules:
      - injection_testing
      - xss_testing
      - authentication_testing
      - session_testing
    
    # Performance
    max_requests_per_second: 10
    timeout: 30
```

### Environment Variables

```env
# Enable DAST
DYNAMIC_ANALYSIS_ENABLED=true

# DAST Scanner Configuration
DAST_TIMEOUT=3600
DAST_MAX_REQUESTS=10000
DAST_USER_AGENT="EMYUEL-DAST/1.0"
```

---

## DAST Integration with Kali Linux Tools

EMYUEL can work alongside popular Kali Linux DAST tools:

### 1. OWASP ZAP Integration

```bash
# Start ZAP in daemon mode
zaproxy -daemon -port 8090 -config api.key=your-api-key

# Configure EMYUEL to use ZAP as DAST engine
# In .env:
DAST_ENGINE=zap
DAST_ZAP_API_URL=http://localhost:8090
DAST_ZAP_API_KEY=your-api-key
```

### 2. Burp Suite Integration

```bash
# Export Burp findings to JSON
# Import to EMYUEL for correlation with SAST results

curl -X POST http://localhost:8000/api/v1/scans/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@burp-findings.json" \
  -F "source=burp"
```

### 3. Sqlmap Integration

```bash
# Run sqlmap on discovered SQL injection points
# EMYUEL detects potential SQLi via SAST
# Sqlmap confirms and exploits via DAST

sqlmap -u "http://target.com/page?id=1" --batch --random-agent
```

### 4. Nikto Integration

```bash
# Web server scanning
nikto -h http://target.com -o nikto-results.json -Format json

# Import to EMYUEL
curl -X POST http://localhost:8000/api/v1/scans/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@nikto-results.json" \
  -F "source=nikto"
```

---

## Hybrid Scanning (SAST + DAST)

**Recommended Workflow**:

```
1. SAST Phase (EMYUEL):
   ├── Scan source code
   ├── Identify potential vulnerabilities
   └── Generate attack vectors

2. DAST Phase (Kali Tools + EMYUEL):
   ├── Deploy application to test environment
   ├── Use SAST findings to guide DAST
   ├── Confirm vulnerabilities with proof-of-concept
   └── Validate remediation effectiveness

3. Correlation Phase (EMYUEL):
   ├── Merge SAST and DAST findings
   ├── Remove duplicates
   ├── Prioritize by confirmed exploitability
   └── Generate comprehensive report
```

### Example: Hybrid SQL Injection Detection

**Step 1: SAST Detection**
```python
# EMYUEL detects unsanitized SQL query
# File: app.py, Line: 45
query = "SELECT * FROM users WHERE id = " + user_input
```

**Step 2: DAST Confirmation**
```bash
# Use sqlmap to confirm
sqlmap -u "http://target.com/user?id=1" \
  --technique=BEUSTQ \
  --level=5 \
  --risk=3 \
  --batch

# Result: Confirmed exploitable SQLi
```

**Step 3: Correlation**
```json
{
  "vulnerability_id": "vuln_001",
  "type": "SQL Injection",
  "severity": "critical",
  "sast_finding": {
    "file": "app.py",
    "line": 45,
    "confidence": 0.95
  },
  "dast_confirmation": {
    "tool": "sqlmap",
    "exploitable": true,
    "payload": "1' OR '1'='1"
  },
  "status": "confirmed"
}
```

---

## Planned DAST Features

### Phase 1: Basic HTTP Testing (Q2 2026)
- [ ] HTTP fuzzing
- [ ] XSS payload testing
- [ ] SQL injection confirmation
- [ ] SSRF verification

### Phase 2: Authentication Testing (Q3 2026)
- [ ] Brute force detection
- [ ] Session fixation testing
- [ ] Authentication bypass
- [ ] Password policy testing

### Phase 3: Advanced Features (Q4 2026)
- [ ] Business logic testing
- [ ] API fuzzing
- [ ] GraphQL testing
- [ ] WebSocket testing
- [ ] File upload testing

### Phase 4: LLM-Powered DAST (2027)
- [ ] Intelligent payload generation
- [ ] Context-aware testing
- [ ] Automated exploit chains
- [ ] Self-healing test suites

---

## DAST Implementation Roadmap

```python
# services/scanner-core/dast/dast_scanner.py (Planned)

class DASTScanner:
    """Dynamic Application Security Testing scanner"""
    
    async def scan_application(self, target_url: str, config: dict):
        """
        Perform dynamic security testing
        
        Features:
        - Crawling and endpoint discovery
        - Payload generation using LLM
        - Vulnerability confirmation
        - Exploit proof-of-concept
        """
        pass
    
    async def fuzz_endpoint(self, endpoint: str, method: str):
        """Fuzz single endpoint with malicious payloads"""
        pass
    
    async def test_authentication(self, auth_endpoint: str):
        """Test authentication mechanisms"""
        pass
    
    async def confirm_sast_finding(self, sast_vulnerability: dict):
        """
        Confirm SAST finding with dynamic testing
        
        Uses LLM to generate targeted payloads based on
        vulnerability context from SAST analysis
        """
        pass
```

---

## Contributing DAST Features

We welcome contributions! To add DAST capabilities:

1. **Fork repository**
2. **Create DAST module** in `services/scanner-core/dast/`
3. **Integrate with LLM orchestrator** for intelligent testing
4. **Add tests** in `tests/dast/`
5. **Update documentation**
6. **Submit pull request**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## Current Workaround

Until native DAST is fully implemented, use this hybrid approach:

### 1. Run EMYUEL SAST Scan

```bash
# Scan codebase with EMYUEL
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"project_id": "proj_123", "scan_type": "comprehensive"}'
```

### 2. Export Findings

```bash
# Export potential injection points
curl http://localhost:8000/api/v1/scans/scan_123/export \
  -H "Authorization: Bearer $TOKEN" \
  -o sast-findings.json
```

### 3. Use Kali Tools for DAST
 
```bash
# Extract URLs and test with OWASP ZAP
zap-cli quick-scan http://target.com

# Or use Burp Suite Professional
# Import SAST findings as scan queue
```

### 4. Import DAST Results Back to EMYUEL

```bash
# Import ZAP results
curl -X POST http://localhost:8000/api/v1/scans/scan_123/dast-import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@zap-report.json"
```

---

## FAQ

**Q: When will full DAST support be available?**  
A: Phase 1 (basic HTTP testing) is planned for Q2 2026. Check GitHub milestones for updates.

**Q: Can I use EMYUEL with existing DAST tools?**  
A: Yes! EMYUEL is designed to complement tools like ZAP, Burp Suite, Nikto, and Sqlmap. See integration examples above.

**Q: Does EMYUEL replace traditional DAST tools?**  
A: No. EMYUEL focuses on LLM-powered SAST with plans to add LLM-enhanced DAST. Traditional tools remain valuable.

**Q: How does LLM help with DAST?**  
A: LLM can generate context-aware payloads, understand complex injection chains, and correlate SAST/DAST findings intelligently.

---

## Support

For DAST-related questions:
- GitHub Discussions: https://github.com/your-org/emyuel/discussions
- Email: dast-support@emyuel.io

---

**Summary**: EMYUEL currently excels at SAST (static analysis). For DAST, use it alongside Kali Linux tools like ZAP, Burp Suite, Sqlmap, and Nikto. Native DAST support is coming in 2026.
