# Dokumentasi Program Shannon AI - Autonomous Penetration Testing Agent

## 1. Gambaran Umum Program

### Tujuan Utama
Shannon adalah sistem penetration testing (pentesting) otomatis berbasis AI yang dirancang untuk menemukan dan mengeksploitasi kerentanan keamanan pada aplikasi web sebelum diserang oleh pihak jahat.

### Masalah yang Diselesaikan
Mengatasi kesenjangan keamanan antara:
- Pengembangan kode yang cepat (continuous deployment)
- Penetration testing manual yang hanya dilakukan 1x setahun
- Risiko kerentanan keamanan yang tidak terdeteksi selama 364 hari

Shannon menjadi "pentest on-demand" yang bisa dijalankan kapan saja untuk memvalidasi keamanan aplikasi.

### Jenis Aplikasi
- **Tipe**: Command-Line Interface (CLI) dengan Docker containerization
- **Platform**: Multi-platform (Linux, macOS, Windows lewat Docker/WSL)
- **Target**: Aplikasi web (whitebox testing - memerlukan akses source code)

### Kemampuan Utama
1. **Operasi Sepenuhnya Otomatis** - Dari login 2FA/TOTP hingga laporan akhir
2. **Eksploitasi Nyata** - Tidak hanya scanning, tapi eksekusi exploit real-world
3. **Analisis Source Code** - Membaca dan memahami kode untuk menemukan kerentanan
4. **Deteksi OWASP Critical** - Injection, XSS, SSRF, Broken Auth/Authz
5. **Zero False Positives** - Hanya melaporkan bug yang benar-benar bisa dieksploitasi

---

## 2. Struktur & Isi Program

### Struktur Direktori Utama

```
shannonAI-main/
├── shannon.mjs              # File utama (entry point)
├── package.json             # Dependency Node.js
├── Dockerfile              # Container definition
├── src/                    # Source code utama
│   ├── ai/                 # Integrasi Claude AI
│   ├── phases/             # Implementasi 5 fase pentesting
│   ├── cli/                # Command-line interface
│   ├── audit/              # Audit logging sistem
│   ├── setup/              # Environment setup
│   └── utils/              # Helper functions
├── prompts/                # Prompt AI untuk setiap agent
├── configs/                # File konfigurasi
├── sessions/               # Session tracking data
├── deliverables/           # Hasil laporan
└── scripts/                # Utility scripts
```

### Penjelasan File dan Direktori Penting

#### File Utama
- **shannon.mjs**: Orchestrator utama yang menjalankan seluruh workflow pentesting
- **package.json**: Mendefinisikan dependency (Claude SDK, zx, chalk, yaml, dll)
- **Dockerfile**: Multi-stage build untuk container security tools

#### Direktori `src/`
- **ai/claude-executor.js**: Menjalankan AI prompts dengan retry logic
- **session-manager.js**: Tracking status eksekusi agent (707 baris)
- **checkpoint-manager.js**: Git-based checkpoint untuk recovery (910 baris)
- **config-parser.js**: Parser dan validator konfigurasi YAML
- **phases/**: Implementasi Pre-recon dan Reporting phase

#### Direktori `prompts/`
Berisi 13 file prompt untuk berbagai agent:
- **pre-recon-code.txt**: Analisis kode awal
- **recon.txt**: Reconnaissance mendalam
- **vuln-*.txt**: Analisis kerentanan (injection, xss, auth, authz, ssrf)
- **exploit-*.txt**: Eksploitasi kerentanan
- **report-executive.txt**: Generate laporan eksekutif

#### Direktori `configs/`
- **config-schema.json**: JSON Schema untuk validasi
- **example-config.yaml**: Template konfigurasi authentication & rules

---

## 3. Penjelasan Fungsi Program

### File `shannon.mjs` (Entry Point)

#### Fungsi `main(webUrl, repoPath, configPath, pipelineTestingMode, disableLoader)`
**Parameter:**
- `webUrl`: URL target aplikasi
- `repoPath`: Path ke repository source code
- `configPath`: Path ke file konfigurasi YAML
- `pipelineTestingMode`: Mode testing cepat
- `disableLoader`: Disable progress indicator

**Return:** Object dengan `reportPath` dan `auditLogsPath`

**Fungsi:** Orchestrator utama yang menjalankan 5 fase pentesting secara berurutan

#### Fungsi `updateSessionProgress(agentName, commitHash)`
**Parameter:**
- `agentName`: Nama agent yang selesai
- `commitHash`: Git commit hash untuk checkpoint

**Fungsi:** Update status session dan simpan checkpoint untuk disaster recovery

### File `src/session-manager.js`

#### Fungsi `createSession(webUrl, repoPath, configFile, targetRepo)`
**Return:** Session object dengan unique UUID

**Fungsi:** Membuat atau mengambil session yang sudah ada untuk melanjutkan proses yang terputus

#### Fungsi `getNextAgent(session)`
**Return:** Agent object berikutnya yang perlu dijalankan

**Fungsi:** Menentukan agent mana yang harus dijalankan berdasarkan status session

#### Fungsi `markAgentCompleted(sessionId, agentName, checkpointCommit)`
**Fungsi:** Menandai agent sebagai selesai dan menyimpan checkpoint Git

#### Fungsi `checkPrerequisites(session, agentName)`
**Return:** Boolean (apakah prerequisites terpenuhi)

**Fungsi:** Memvalidasi bahwa semua agent prerequisite sudah selesai

### File `src/checkpoint-manager.js`

#### Fungsi `runSingleAgent(agentName, session, pipelineTestingMode, runClaudePromptWithRetry, loadPrompt, allowRerun, skipWorkspaceClean)`
**Return:** Object hasil eksekusi agent

**Fungsi:** Menjalankan satu agent dengan retry logic, checkpoint, dan error handling

#### Fungsi `runPhase(phaseName, session, pipelineTestingMode, runClaudePromptWithRetry, loadPrompt)`
**Fungsi:** Menjalankan seluruh agent dalam satu fase (bisa parallel untuk vuln/exploit)

#### Fungsi `rollbackToAgent(sessionId, targetAgent)`
**Fungsi:** Rollback workspace ke checkpoint tertentu menggunakan Git

### File `src/config-parser.js`

#### Fungsi `parseConfig(configPath)`
**Return:** Parsed configuration object

**Fungsi:** Membaca, parse, dan validasi file YAML dengan security checks

#### Fungsi `distributeConfig(config)`
**Return:** Distributed config untuk berbagai agent

**Fungsi:** Mendistribusikan bagian-bagian config ke agent yang membutuhkan

### File `src/phases/pre-recon.js`

#### Fungsi `runTerminalScan(tool, target, sourceDir)`
**Parameter:**
- `tool`: Nama tool (nmap/subfinder/whatweb/schemathesis)
- `target`: Target URL
- `sourceDir`: Directory source code

**Return:** Object dengan output scan

**Fungsi:** Menjalankan security scanning tools eksternal

#### Fungsi `executePreReconPhase(webUrl, sourceDir, variables, config, toolAvailability, pipelineTestingMode, sessionId)`
**Return:** Object dengan duration dan report

**Fungsi:** Menjalankan Phase 1 dengan 2 wave paralel operations

---

## 4. Alur Program

### Alur Kerja Keseluruhan (Step-by-Step)

#### **Fase Inisialisasi**
1. Parse argumen CLI (URL target, path repository, config)
2. Validasi input (URL format, repository accessibility)
3. Load dan validasi konfigurasi YAML
4. Check ketersediaan security tools (nmap, subfinder, whatweb, schemathesis)
5. Setup local repository (clone/copy ke workspace)
6. Buat atau resume session dengan UUID unik

#### **PHASE 1: PRE-RECONNAISSANCE** (~5-10 menit)
**Wave 1 (Parallel):**
1. **Nmap scan** - Port scanning dan service detection
2. **Subfinder** - Subdomain enumeration
3. **WhatWeb** - Technology stack detection
4. **Code Analysis AI** - Static code analysis untuk entry points, API endpoints, authentication

**Wave 2 (Parallel):**
5. **Schemathesis** - API schema testing (jika ada OpenAPI/Swagger spec)

**Output:** `deliverables/pre_recon_deliverable.md`

#### **PHASE 2: RECONNAISSANCE** (~5-10 menit)
1. AI agent menganalisis hasil pre-recon
2. Browser automation untuk explore aplikasi secara live
3. Login dengan 2FA/TOTP jika dikonfigurasi
4. Map semua endpoint, form, dan functionality
5. Korelasi antara source code dan behavior aplikasi

**Output:** Peta lengkap attack surface

#### **PHASE 3: VULNERABILITY ANALYSIS** (~20-30 menit - PARALLEL)
Menjalankan 5 specialist agent secara **paralel**:

1. **Injection Vuln Agent**
   - Trace data flow dari user input ke dangerous sink
   - Identifikasi SQL/NoSQL/Command injection
   - Generate hypothesis exploit paths

2. **XSS Vuln Agent**
   - Trace input validation dan output sanitization
   - Identifikasi reflected/stored/DOM XSS
   - Generate payload candidates

3. **Auth Vuln Agent**
   - Analisis authentication mechanism
   - JWT weaknesses, session handling
   - Password reset vulnerabilities

4. **AuthZ Vuln Agent**
   - Analisis authorization checks
   - IDOR (Insecure Direct Object Reference)
   - Privilege escalation paths

5. **SSRF Vuln Agent**
   - URL parameter analysis
   - Internal service exposure
   - Cloud metadata access

**Output:** List hypothesized exploitable vulnerabilities

#### **PHASE 4: EXPLOITATION** (~20-40 menit - PARALLEL)
Menjalankan 5 exploit agent secara **paralel**:

Setiap agent mencoba mengeksploitasi kerentanan yang ditemukan di Phase 3:
- Browser automation untuk XSS
- cURL/httpx untuk injection attacks
- Custom scripts untuk auth bypass
- SSRF payload delivery

**Policy:** "No Exploit, No Report" - Jika tidak bisa dibuktikan, tidak dilaporkan

**Output:** Proof-of-concepts yang reproducible

#### **PHASE 5: REPORTING** (~5-10 menit)
1. Assemble semua deliverables dari specialist agents
2. AI reporter agent membuat executive summary
3. Cleaning hallucinations dan false claims
4. Format laporan final dengan severity scoring

**Output:** `deliverables/comprehensive_security_assessment_report.md`

### Alur Data dalam Program

```
User Input (URL + Repo Path)
    ↓
Configuration Parser
    ↓
Session Creation/Resume
    ↓
┌─────────────────────────────────┐
│  PHASE 1: External Tools        │
│  + AI Code Analysis             │
└─────────────────────────────────┘
    ↓ (Attack Surface Map)
┌─────────────────────────────────┐
│  PHASE 2: AI Browser Recon      │
└─────────────────────────────────┘
    ↓ (Complete Endpoint Map)
┌─────────────────────────────────┐
│  PHASE 3: 5 Vuln Agents (||)    │
│  - Injection                    │
│  - XSS                          │
│  - Auth                         │
│  - AuthZ                        │
│  - SSRF                         │
└─────────────────────────────────┘
    ↓ (Vulnerability Hypotheses)
┌─────────────────────────────────┐
│  PHASE 4: 5 Exploit Agents (||) │
│  - Verify exploitability        │
│  - Generate PoCs                │
└─────────────────────────────────┘
    ↓ (Proven Exploits Only)
┌─────────────────────────────────┐
│  PHASE 5: Report Assembly       │
│  - Executive Summary            │
│  - Cleanup Hallucinations       │
└─────────────────────────────────┘
    ↓
Final Report + Audit Logs
```

---

## 5. Library / Dependency yang Digunakan

### Node.js Dependencies

#### **@anthropic-ai/claude-agent-sdk** (^0.1.0)
- **Fungsi:** SDK untuk Anthropic Claude AI dengan browser automation
- **Alasan:** Core reasoning engine untuk AI pentesting agents

#### **zx** (^8.0.0)
- **Fungsi:** Shell scripting dalam JavaScript/Node.js
- **Alasan:** Menjalankan command-line tools (nmap, subfinder) dari Node.js

#### **chalk** (^5.0.0)
- **Fungsi:** Terminal string styling (warna, bold, dll)
- **Alasan:** UI/UX yang lebih baik untuk output CLI

#### **js-yaml** (^4.1.0)
- **Fungsi:** YAML parser dan stringifier
- **Alasan:** Parse file konfigurasi authentication dan rules

#### **ajv** (^8.12.0) + **ajv-formats** (^2.1.1)
- **Fungsi:** JSON Schema validator
- **Alasan:** Validasi ketat struktur konfigurasi untuk keamanan

#### **dotenv** (^16.4.5)
- **Fungsi:** Load environment variables dari .env
- **Alasan:** Manajemen API keys (CLAUDE_CODE_OAUTH_TOKEN)

#### **boxen** (^8.0.1)
- **Fungsi:** Create boxes in terminal
- **Alasan:** Display banner dan summary yang menarik

#### **figlet** (^1.9.3) + **gradient-string** (^3.0.0)
- **Fungsi:** ASCII art text generation
- **Alasan:** Splash screen Shannon branding

#### **zod** (^3.22.4)
- **Fungsi:** TypeScript-first schema validation
- **Alasan:** Runtime type safety untuk data structures

### System Dependencies (Docker Container)

#### Security Tools
- **nmap**: Network port scanning dan service detection
- **subfinder**: Fast subdomain discovery tool
- **whatweb**: Web technology fingerprinting
- **schemathesis**: API schema-based testing

#### Runtimes
- **Node.js 22**: JavaScript runtime
- **Python 3**: Untuk schemathesis
- **Ruby**: Untuk WhatWeb
- **Go**: Untuk subfinder compilation

#### Browser
- **Chromium**: Headless browser untuk automation
- **Playwright libraries**: Browser automation framework

---

## 6. Cara Menjalankan Program

### Requirements

#### Software Requirements
- **Docker Desktop** atau Docker Engine (20.10+)
- **Git** (untuk clone repository target)
- **8GB RAM minimum** (16GB recommended)
- **Claude Console Account** dengan credits

#### Sistem Operasi
- Linux (native Docker)
- macOS (Docker Desktop)
- Windows (Docker Desktop atau WSL2)

#### API Authentication
Salah satu dari:
- Claude Code OAuth Token (dari console.anthropic.com)
- Anthropic API Key

### Instalasi Dependency

#### 1. Clone Repository Shannon
```bash
git clone https://github.com/KeygraphHQ/shannon.git
cd shannon
```

#### 2. Build Docker Container
```bash
docker build -t shannon:latest .
```

#### 3. Prepare Target Repository
```bash
# Untuk monorepo
git clone https://github.com/your-org/your-app.git repos/your-app

# Untuk multi-repo
mkdir repos/your-app
cd repos/your-app
git clone https://github.com/your-org/frontend.git
git clone https://github.com/your-org/backend.git
```

#### 4. Setup Environment Variables
```bash
export CLAUDE_CODE_OAUTH_TOKEN="your-token-here"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000
```

### Perintah untuk Menjalankan Program

#### Menjalankan Full Pentest (Production Mode)
```bash
docker run --rm -it \
  --network host \
  --cap-add=NET_RAW \
  --cap-add=NET_ADMIN \
  -e CLAUDE_CODE_OAUTH_TOKEN="$CLAUDE_CODE_OAUTH_TOKEN" \
  -e CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000 \
  -v "$(pwd)/repos:/app/repos" \
  -v "$(pwd)/configs:/app/configs" \
  shannon:latest \
  "https://your-app.com/" \
  "/app/repos/your-app" \
  --config /app/configs/example-config.yaml
```

#### Testing Aplikasi Localhost
```bash
docker run --rm -it \
  --add-host=host.docker.internal:host-gateway \
  --cap-add=NET_RAW \
  --cap-add=NET_ADMIN \
  -e CLAUDE_CODE_OAUTH_TOKEN="$CLAUDE_CODE_OAUTH_TOKEN" \
  -v "$(pwd)/repos:/app/repos" \
  shannon:latest \
  "http://host.docker.internal:3000" \
  "/app/repos/your-app"
```

#### Developer Commands

**Lihat Status Session:**
```bash
docker run --rm shannon:latest --status
```

**Run Specific Agent:**
```bash
./shannon.mjs --run-agent recon
```

**Rollback ke Checkpoint:**
```bash
./shannon.mjs --rollback-to injection-vuln
```

**List Available Agents:**
```bash
./shannon.mjs --list-agents
```

---

## 7. Cara Penggunaan Program

### Contoh Penggunaan 1: Web App dengan Form Login

#### Input yang Dibutuhkan
1. **Target URL**: `https://demo.example.com`
2. **Repository Path**: `/path/to/source-code`
3. **Config File**: `configs/demo-config.yaml`

#### File Konfigurasi
```yaml
authentication:
  login_type: form
  login_url: "https://demo.example.com/login"
  credentials:
    username: "test@example.com"
    password: "TestPass123"
  login_flow:
    - "Type $username into the email field"
    - "Type $password into the password field"
    - "Click the 'Sign In' button"
  success_condition:
    type: url_contains
    value: "/dashboard"

rules:
  avoid:
    - description: "Skip logout endpoint"
      type: path
      url_path: "/logout"
  focus:
    - description: "Prioritize API endpoints"
      type: path
      url_path: "/api"
```

#### Perintah Eksekusi
```bash
docker run --rm -it \
  --network host \
  --cap-add=NET_RAW \
  -e CLAUDE_CODE_OAUTH_TOKEN="$TOKEN" \
  -v "$(pwd)/repos:/app/repos" \
  -v "$(pwd)/configs:/app/configs" \
  shannon:latest \
  "https://demo.example.com/" \
  "/app/repos/demo-app" \
  --config /app/configs/demo-config.yaml
```

#### Output yang Dihasilkan
```
deliverables/
├── pre_recon_deliverable.md         # Hasil scanning tools
├── code_analysis_deliverable.md     # Analisis kode
├── recon_deliverable.md             # Peta attack surface
├── injection_vuln_analysis.md       # Analisis injection
├── xss_vuln_analysis.md             # Analisis XSS
├── auth_vuln_analysis.md            # Analisis autentikasi
├── authz_vuln_analysis.md           # Analisis otorisasi
├── ssrf_vuln_analysis.md            # Analisis SSRF
├── injection_exploit_results.md     # PoC injection
├── xss_exploit_results.md           # PoC XSS
├── auth_exploit_results.md          # PoC auth bypass
├── authz_exploit_results.md         # PoC privilege escalation
├── ssrf_exploit_results.md          # PoC SSRF
└── comprehensive_security_assessment_report.md  # Final report
```

### Contoh Penggunaan 2: API dengan 2FA/TOTP

#### Konfigurasi dengan TOTP
```yaml
authentication:
  login_type: form
  login_url: "https://api.example.com/auth/login"
  credentials:
    username: "apitest@example.com"
    password: "SecurePass456"
    totp_secret: "JBSWY3DPEHPK3PXP"  # TOTP secret
  login_flow:
    - "Type $username into username field"
    - "Type $password into password field"
    - "Click 'Next'"
    - "Wait for TOTP prompt"
    - "Enter $totp in verification field"
    - "Click 'Verify'"
  success_condition:
    type: element_present
    value: "#dashboard-container"
```

### Skenario Penggunaan Umum

#### Skenario 1: Pre-Production Security Check
- **Situasi:** Sebelum deploy ke production
- **Target:** Staging environment
- **Frekuensi:** Setiap sprint/release
- **Durasi:** 1-1.5 jam
- **Cost:** ~$50 USD (Claude API)

#### Skenario 2: Continuous Security Testing
- **Situasi:** CI/CD pipeline integration
- **Target:** Development/Staging
- **Frekuensi:** Setiap commit ke main branch
- **Durasi:** 1-1.5 jam
- **Cost:** ~$50 USD per run

#### Skenario 3: Compliance Audit Preparation
- **Situasi:** Sebelum SOC2/PCI-DSS audit
- **Target:** Production-like environment
- **Frekuensi:** Quarterly
- **Durasi:** Full comprehensive test
- **Output:** Executive report untuk auditor

---

## 8. Detail Teknis Program

### Konsep Penting

#### 1. Multi-Agent Architecture
Shannon menggunakan **specialized agents** untuk berbagai tugas:
- **Pre-recon agent**: External reconnaissance
- **Recon agent**: Deep application exploration
- **5 Vulnerability agents**: Domain-specific analysis
- **5 Exploit agents**: Proof-of-concept execution
- **Report agent**: Final assembly dan cleanup

Setiap agent adalah **isolated AI conversation** dengan prompt engineering khusus.

#### 2. Async/Parallel Processing
- **Phase 1-2**: Sequential (butuh hasil lengkap)
- **Phase 3 (Vuln Analysis)**: 5 agents berjalan **paralel** (Promise.all)
- **Phase 4 (Exploitation)**: 5 agents berjalan **paralel**
- **Phase 5**: Sequential (assembly report)

Parallel processing menghemat waktu ~50% vs sequential.

#### 3. Git-Based Checkpointing
Setiap agent completion:
```javascript
const commitHash = await getGitCommitHash(sourceDir);
await updateSession(sessionId, {
  checkpoints: { [agentName]: commitHash }
});
```

Disaster recovery:
```javascript
await rollbackGitToCommit(sourceDir, checkpointHash);
```

Keuntungan:
- Resume dari interruption
- Rerun specific agent
- Rollback jika ada masalah

#### 4. Session Management
File `.shannon-store.json` menyimpan:
- Session ID (UUID)
- Completed agents
- Failed agents
- Checkpoint commit hashes
- Timestamp

Recovery otomatis jika process crash.

#### 5. Audit Logging System
Setiap AI call dicatat di `audit-logs/`:
```
audit-logs/{sessionId}/
├── session.json              # Metadata
├── pre-recon/
│   ├── prompt.md
│   ├── response.md
│   └── metrics.json
├── recon/
└── ...
```

Untuk debugging, compliance, dan cost tracking.

#### 6. Browser Automation dengan Playwright
Claude Agent SDK menggunakan Playwright untuk:
- Login automation (form + 2FA)
- Dynamic page exploration
- XSS exploit validation
- Screenshot evidence collection

Headless chromium di Docker container.

#### 7. LLM-Powered Data Flow Analysis
Untuk Injection/SSRF vulnerability:
1. Identify user-controlled input (source)
2. Trace through code execution
3. Find dangerous operation (sink)
4. Validate exploitability

Berbasis konsep dari paper: https://arxiv.org/abs/2402.10754

#### 8. Configuration Security
Multiple layers:
- **JSON Schema validation** (struktur)
- **Dangerous pattern detection** (path traversal, XSS)
- **Type-specific validation** (domain format, HTTP methods)
- **Conflict detection** (avoid vs focus rules)

#### 9. Error Handling dan Retry Logic
```javascript
async function runClaudePromptWithRetry(
  prompt, sourceDir, glob, exclude,
  agentName, snapshotName, colorFn, sessionMetadata
) {
  const maxRetries = 3;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await executePrompt(...);
    } catch (error) {
      if (isRetryable(error) && attempt < maxRetries) {
        await sleep(exponentialBackoff(attempt));
        continue;
      }
      throw error;
    }
  }
}
```

#### 10. Cost dan Timing Metrics
Global tracking:
```javascript
const costResults = {
  total: 0,
  agents: {}
};

const timingResults = {
  total: Timer,
  phases: {},
  agents: {},
  commands: {}
};
```

Display di akhir execution untuk optimization.

### Komunikasi Antar Komponen

#### Shannon.mjs ↔ Session Manager
```
shannon.mjs: createSession(url, repo)
    ↓
session-manager.js: Generate UUID, save to .shannon-store.json
    ↓
shannon.mjs: getNextAgent(session)
    ↓
session-manager.js: Return next agent in sequence
```

#### Shannon.mjs ↔ Checkpoint Manager
```
shannon.mjs: runPhase('vulnerability-analysis', session)
    ↓
checkpoint-manager.js: runParallelVuln()
    ↓
checkpoint-manager.js: runSingleAgent() × 5 (parallel)
    ↓
checkpoint-manager.js: markAgentCompleted(sessionId, agentName, commitHash)
```

#### Checkpoint Manager ↔ AI Executor
```
checkpoint-manager.js: runSingleAgent('injection-vuln')
    ↓
claude-executor.js: runClaudePromptWithRetry(prompt, sourceDir, ...)
    ↓
Claude Agent SDK: Execute AI agent with browser/filesystem/code analysis
    ↓
claude-executor.js: Save audit logs, return usage metrics
    ↓
checkpoint-manager.js: Save checkpoint via Git commit
```

### Logika Penting

#### Vulnerability → Exploit Flow
```javascript
// Phase 3: Find vulnerabilities
const vulnResults = await runParallelVuln(session);
// Simpan ke session.vulnerabilities

// Phase 4: Skip exploitation jika tidak ada vuln
const exploitAgents = ['injection-exploit', 'xss-exploit', ...];
for (const agent of exploitAgents) {
  const vulnType = agent.replace('-exploit', '');
  const hasVulnerabilities = session.vulnerabilities[vulnType]?.length > 0;
  
  if (!hasVulnerabilities) {
    console.log(`Skipping ${agent} - no vulnerabilities found`);
    continue;
  }
  
  await runSingleAgent(agent, session);
}
```

#### No Exploit, No Report Policy
```javascript
// Exploitation agent harus return proof:
{
  "vulnerability": "SQL Injection in /api/users",
  "exploited": true,
  "proof": {
    "payload": "' OR 1=1--",
    "response": "200 OK, returned all users",
    "screenshot": "base64_image"
  }
}

// Reporter agent filter:
if (exploit.exploited === false) {
  // Don't include in final report
  continue;
}
```

---

## 9. Kesimpulan

### Ringkasan Cara Kerja
Shannon bekerja sebagai **autonomous AI pentester** yang mengemulasi metodologi penetration tester manusia melalui 5 fase terstruktur:

1. **External Reconnaissance** - Gathering intel dengan security tools
2. **Application Exploration** - Browser automation untuk mapping
3. **Vulnerability Analysis** - Source code analysis paralel dengan 5 spesialisasi
4. **Exploitation** - Proof-of-concept execution untuk validasi
5. **Professional Reporting** - Assembly dan cleanup untuk actionable output

Keunggulan utama adalah **proof-by-exploitation** - hanya melaporkan bug yang benar-benar bisa dieksploitasi dengan PoC yang reproducible.

### Kelebihan Program

#### 1. Zero False Positives
- Policy "No Exploit, No Report"
- Setiap vulnerability harus dibuktikan dengan exploit nyata
- Hemat waktu developer (tidak investigate false alarm)

#### 2. Fully Autonomous
- Tidak perlu manual intervention setelah start
- Auto-handle 2FA/TOTP authentication
- Auto-navigate aplikasi dengan browser
- Auto-generate actionable report

#### 3. White-box + Black-box Hybrid
- Source code analysis untuk deep insight
- Live exploitation untuk real-world validation
- Best of both worlds

#### 4. Fast Parallel Processing
- Phase 3 dan 4 berjalan paralel
- 5 specialist agents concurrent
- Total waktu ~1-1.5 jam (vs 8+ jam sequential)

#### 5. Disaster Recovery
- Git-based checkpointing
- Session persistence
- Resume dari crash atau interruption

#### 6. Enterprise-Grade Audit Trail
- Complete audit logs per session
- Cost tracking per agent
- Timing metrics untuk optimization
- Compliance-ready documentation

#### 7. Extensible Architecture
- Modular agent system
- Easy to add new vulnerability types
- Customizable prompts
- Configuration-driven testing

### Potensi Pengembangan ke Depan

#### 1. Coverage Expansion
- **File Upload vulnerabilities** (malicious files, path traversal)
- **Deserialization attacks** (Python pickle, Java objects)
- **Business logic flaws** (payment bypass, workflow manipulation)
- **Race conditions** (TOCTOU, concurrent request exploits)
- **GraphQL vulnerabilities** (introspection, batching attacks)

#### 2. CI/CD Integration (Shannon Pro)
- Native GitHub Actions support
- GitLab CI pipeline templates
- Jenkins plugin
- Auto-comment di PR dengan findings

#### 3. Advanced Analysis Engine
- Full codebase graph analysis (tidak limited oleh context window)
- Cross-service vulnerability tracking (microservices)
- Taint analysis yang lebih sophisticated
- ML-based exploit generation

#### 4. Multi-Platform Support
- Mobile app testing (iOS/Android)
- Desktop application testing
- API-only testing (tanpa UI)
- Blockchain/Smart contract testing

#### 5. Collaborative Features
- Multi-user session sharing
- Team collaboration dashboard
- Severity customization per organization
- Custom compliance frameworks

#### 6. Performance Optimization
- Incremental scanning (hanya test yang berubah)
- Smart agent scheduling berdasarkan codebase
- Adaptive timeout berdasarkan complexity
- Cost optimization dengan model selection

#### 7. Remediation Assistance
- Auto-generate fix suggestions
- Code patch generation
- Secure coding pattern recommendations
- Integration dengan IDEs (VSCode extension)

---

## Informasi Lisensi & Kontak

**Lisensi:** GNU Affero General Public License v3.0 (AGPL-3.0)

**Shannon Lite** (open source) vs **Shannon Pro** (commercial):
- Pro memiliki LLM-powered data flow analysis engine
- Pro mendukung CI/CD integration
- Pro termasuk RBAC, SSO/SAML, compliance reporting

**Website:** https://keygraph.io  
**Email:** shannon@keygraph.io  
**Discord:** https://discord.gg/KAqzSHHpRt

---

**Dokumentasi dibuat:** 2026-01-29  
**Versi Shannon:** 1.0.0  
**Platform:** Node.js 22, Docker
