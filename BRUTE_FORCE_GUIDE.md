# 🔓 Brute Force Feature - User Guide

## Apa itu Brute Force?

**Brute Force** adalah metode testing keamanan yang mencoba berbagai kombinasi username/password sampai menemukan yang benar. EMYUEL sekarang dilengkapi dengan brute force engine yang sangat powerful!

---

## 🚀 Fitur Utama

### 1. **Tiga Strategi Attack**
- ✅ **Default Credentials** - Tercepat! Coba admin/admin, root/toor, dll
- ✅ **Wordlist Attack** - Dictionary-based dengan 100+ password umum
- ✅ **Exhaustive Brute Force** - Mencoba SEMUA kombinasi karakter sampai ketemu!

### 2. **Character Sets Lengkap**
- `lowercase` = a-z (26 karakter)
- `uppercase` = A-Z (26 karakter)  
- `numbers` = 0-9 (10 karakter)
- `symbols` = !@#$%^&*()-_=+[]{}|;:',.<>?/~` (30+ karakter)
- `all` = Semua karakter (95 total)

### 3. **Exhaustive Mode - SEMUA KOMBINASI!**
Program akan mencoba:
- Panjang 1: a, b, c, ..., 1, 2, 3, ..., !, @, #
- Panjang 2: aa, ab, ac, ..., a1, a2, ..., a!, a@
- Panjang 3: aaa, aab, aac, ... dst
- **Sampai ketemu password yang benar!**

---

## 📊 Perkiraan Jumlah Kombinasi

| Length | Lowercase | +Numbers | +Uppercase | ALL (symbols) |
|--------|-----------|----------|------------|---------------|
| 1 | 26 | 36 | 62 | 95 |
| 2 | 676 | 1,296 | 3,844 | 9,025 |
| 3 | 17,576 | 46,656 | 238,328 | 857,375 |
| 4 | 456,976 | 1.7M | 14.8M | **81.4M** |
| 5 | 11.9M | 60.5M | 916M | **7.7 Billion** |
| 6 | 308M | 2.2B | 56.8B | **735 Billion** |

⚠️ **PERINGATAN**: 
- Length 4 ke atas dengan "all chars" = SANGAT LAMA!
- Length 6+ bisa memakan waktu BERHARI-HARI atau BERMINGGU-MINGGU!

---

## 🎯 Cara Pakai di GUI

### Quick Scan Tab:

1. **Masukkan URL target**:
   ```
   https://example.com/login
   ```

2. **Centang Brute Force**:
   ```
   ☑ XSS
   ☑ SQL Injection
   ☑ CSRF
   ☑ Security Headers
   ☑ 🔓 Brute Force (Auth Testing)  ← Centang ini!
   ```

3. **Klik "⚡ Quick Scan"**

4. Scanner akan:
   - Detect login form/HTTP auth
   - Coba default credentials dulu (cepat)
   - Lalu wordlist attack
   - Opsi exhaustive (kalau dikonfigurasi)

---

## ⚙️ Konfigurasi (Advanced)

Untuk customize brute force behavior, edit `brute_force_detector.py`:

```python
detector = BruteForceDetector(
    strategy='hybrid',              # default | wordlist | exhaustive | hybrid
    charsets=['lowercase', 'numbers'],  # atau ['all']
    min_length=1,
    max_length=4,                   # HATI-HATI! >6 = SANGAT LAMA
    rate_limit=0.1,                 # delay antar attempt (detik)
    max_attempts=10000,             # safety limit
    stop_on_success=True            # stop setelah ketemu
)
```

---

## 💡 Rekomendasi Penggunaan

### ✅ Gunakan Untuk:
- Testing weak passwords pada sistem sendiri
- Penetration testing dengan izin
- Security audit internal
- Training & education

### ⚠️ Mulai Dari:
1. **Default credentials** (paling cepat, paling umum)
2. **Wordlist attack** (top 100 passwords)
3. **Exhaustive** hanya jika yakin password sangat pendek (<4 chars)

### 📝 Strategi Efektif:
- **Website korporat**: Coba default + wordlist
- **IoT devices**: Default credentials (sering lupa diganti!)
- **Test lokal**: Exhaustive OK untuk max_length 3-4
- **Production scan**: Wordlist only (exhaustive terlalu lama)

---

## 🔐 Contoh Output

```
[BRUTE FORCE] Starting attack on: https://example.com/login
[BRUTE FORCE] Strategy: hybrid
[BRUTE FORCE] Character sets: ['lowercase', 'numbers']
[BRUTE FORCE] Length range: 1-4

[BRUTE FORCE] Trying default credentials...
[PROGRESS] Attempts: 15 | Testing: admin:admin
[PROGRESS] Attempts: 23 | Testing: root:toor

[BRUTE FORCE] Trying wordlist attack...
[PROGRESS] Attempts: 100 | Rate: 10.2/sec | Testing: admin:pas...
[PROGRESS] Attempts: 200 | Rate: 9.8/sec | Testing: user:123...
[SUCCESS] Found valid credential: admin:password123

Results:
- Found credentials: admin:password123
- Attempts: 247
- Time taken: 24.7 seconds
- Strategy used: wordlist
```

---

## ⚠️ Legal & Ethical Warning

### 🚨 PENTING - HARUS DIBACA!

**Brute force testing hanya boleh dilakukan pada:**
1. ✅ Sistem milik sendiri
2. ✅ Sistem dengan izin tertulis eksplisit
3. ✅ Lab testing environment
4. ✅ Vulnerable apps (DVWA, WebGoat, dll)

**DILARANG untuk:**
1. ❌ Website orang lain tanpa izin
2. ❌ Production systems tanpa approval
3. ❌ Illegal hacking
4. ❌ Unauthorized access

**Konsekuensi:**
- Melanggar UU ITE
- Tindak pidana cyber crime
- Denda & penjara

**Gunakan secara bertanggung jawab!**

---

## 🎓 Tips & Tricks

### Optimasi Kecepatan:
```python
# Cepat - lowercase + numbers, max 4 chars
charsets=['lowercase', 'numbers'], max_length=4

# Sedang - +uppercase, max 3 chars  
charsets=['lowercase', 'uppercase', 'numbers'], max_length=3

# Lambat - ALL chars, max 3 chars (masih feasible)
charsets=['all'], max_length=3

# SANGAT LAMBAT - jangan coba ini kecuali yakin!
charsets=['all'], max_length=5  # 7.7 BILLION kombinasi!
```

### Rate Limiting:
- Production: `rate_limit=1.0` (1 detik per attempt)
- Testing: `rate_limit=0.1` (10 attempts/second)
- Local:  `rate_limit=0.01` (100 attempts/second)

### Max Attempts:
- Quick test: `max_attempts=1000`
- Standard: `max_attempts=10000`  
- Exhaustive: `max_attempts=100000` atau lebih

---

## 📚 Resources

**Wordlists Location:**
- `services/scanner-core/wordlists/common_passwords.txt`
- `services/scanner-core/wordlists/common_usernames.txt`
- `services/scanner-core/wordlists/default_credentials.json`

**Test Sites:**
- https://testphp.vulnweb.com (vulnerable test site)
- DVWA (Damn Vulnerable Web Application)
- bWAPP (buggy Web Application)

---

**Sekarang EMYUEL punya brute force yang SANGAT KUAT! Gunakan dengan bijak! 🔓🛡️**
