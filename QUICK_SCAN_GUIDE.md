# 🛡️ Cara Pakai EMYUEL Quick Scan

## Alur Penggunaan yang Mudah

### Step 1: Masukkan Link Website 🌐
```
┌─────────────────────────────────────────────────────┐
│  🌐 Website URL Scanner                             │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  https://example.com                     ⚡   │ │
│  │                                    Quick Scan  │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Quick Examples:                                    │
│  🔗 https://example.com                            │
│  🔗 https://testphp.vulnweb.com                    │
│  🔗 http://demo.testfire.net                       │
└─────────────────────────────────────────────────────┘
```

**Cara:**
- Ketik URL website di kotak input
- ATAU klik salah satu contoh link yang disediakan
- Pastikan URL dimulai dengan `http://` atau `https://`

---

### Step 2: Pilih Celah Keamanan yang Ingin Dicari ☑️
```
┌─────────────────────────────────────────────────────┐
│  Select Vulnerabilities to Scan:                   │
│                                                     │
│  Kolom 1:                    Kolom 2:              │
│  ☑ XSS (Cross-Site Scripting) ☐ SSL/TLS Issues    │
│  ☑ SQL Injection              ☑ Information Disc.  │
│  ☑ CSRF                       ☐ Scan All           │
│  ☑ Security Headers                                │
└─────────────────────────────────────────────────────┘
```

**Pilihan Celah:**
1. **XSS** - Cross-Site Scripting attacks
2. **SQL Injection** - Database injection vulnerabilities
3. **CSRF** - Cross-Site Request Forgery
4. **Security Headers** - Missing security headers
5. **SSL/TLS Issues** - Certificate dan encryption problems
6. **Information Disclosure** - Data leakage
7. **Scan All** - Centang semua sekaligus

**Default:** XSS, SQLi, CSRF, Headers, Info Disclosure sudah tercentang (paling umum)

---

### Step 3: Klik "⚡ Quick Scan" 🚀
```
┌─────────────────────────────────────────────────────┐
│  https://example.com              ⚡ Quick Scan     │
└─────────────────────────────────────────────────────┘
```

**Yang Terjadi:**
1. URL divalidasi otomatis
2. Scanner mulai bekerja
3. Status berubah: Ready → Scanning...
4. Console menampilkan:
   ```
   [INFO] 🚀 Starting quick scan...
   [INFO] Target: https://example.com
   [INFO] Profile: standard
   [INFO] Modules: xss, sqli, csrf, headers
   ```
5. Hasil scan muncul setelah selesai

---

## 🎯 Contoh Penggunaan

### Skenario 1: Cek XSS Saja
1. Masukkan: `https://testphp.vulnweb.com`
2. Uncheck semua kecuali **XSS**
3. Klik **⚡ Quick Scan**
4. Scanner hanya cari celah XSS → Lebih cepat!

### Skenario 2: Scan Lengkap
1. Masukkan: `https://example.com`
2. Centang **Scan All** (otomatis centang semua)
3. Klik **⚡ Quick Scan**
4. Scanner cek semua jenis vulnerability

### Skenario 3: Custom Selection
1. Masukkan: `http://demo.testfire.net`
2. Pilih: XSS + SQL Injection + CSRF
3. Klik **⚡ Quick Scan**
4. Scanner fokus ke 3 celah tersebut

---

## 💡 Tips

**Scan Lebih Cepat:**
- Pilih hanya celah yang relevan
- Contoh: Website form → pilih XSS + CSRF
- Contoh: Website database → pilih SQL Injection

**Scan Lengkap:**
- Centang "Scan All" untuk audit menyeluruh
- Cocok untuk website baru/belum pernah di-scan

**Test Sites:**
- `https://testphp.vulnweb.com` - Sengaja vulnerable
- `http://demo.testfire.net` - IBM demo banking app
- Gunakan untuk testing scanner

---

## 🎨 Interface Quick Scan

```
╔═══════════════════════════════════════════════════════╗
║  🛡️ EMYUEL                      ● Ready              ║
║  Enterprise AI Security Scanner                       ║
╚═══════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│  🌐 Website URL Scanner                                 │
│  Enter a website URL to scan for security              │
│  vulnerabilities                                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [URL Input Here]                  ⚡ Quick Scan │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Quick Examples:                                        │
│  🔗 example.com   🔗 testphp.vulnweb.com              │
│                                                         │
│  Select Vulnerabilities to Scan:                       │
│  ☑ XSS (Cross-Site Scripting)  ☐ SSL/TLS Issues       │
│  ☑ SQL Injection                ☑ Information Disc.    │
│  ☑ CSRF                         ☐ Scan All             │
│  ☑ Security Headers                                    │
└─────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────

│  🔍 Natural Language Query (Alternative)                │
│  Or describe what you want to scan...                   │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Penggunaan

1. ✓ Buka EMYUEL GUI: `python -m gui.emyuel_gui`
2. ✓ Pilih tab **Quick Scan**
3. ✓ Masukkan URL website target
4. ✓ Pilih celah keamanan yang ingin dicari
5. ✓ Klik **⚡ Quick Scan**
6. ✓ Tunggu hasil scan muncul
7. ✓ Review findings yang ditemukan

---

**Alur Singkat:**
```
URL Input → Select Vulns → Quick Scan → Results
   ↓            ↓              ↓            ↓
link web    pilih celah    klik scan    lihat hasil
```

Mudah kan? 🚀
