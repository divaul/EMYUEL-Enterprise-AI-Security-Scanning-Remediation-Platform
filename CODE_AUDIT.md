# Code Audit Report - Scanner Components

## Issues Found & Fixed

### 1. **Typo in code_scanner.py (Line 204)** ⚠️
**File:** `code_scanner.py`  
**Line:** 204  
**Issue:** `'description': 'Potential SQLinjection via string formatting'`  
**Should be:** `'description': 'Potential SQL injection via string formatting'`  
**Severity:** Minor (typo)  
**Status:** TO FIX

---

### 2. **Deprecated OpenAI API in llm_analyzer.py** ⚠️
**File:** `llm_analyzer.py`  
**Lines:** 202-211, 221-230  
**Issue:** Using `openai.ChatCompletion.create` which is deprecated in openai>=1.0.0  
**Should use:** New `OpenAI()` client style  
**Severity:** Critical (will break with openai>=1.0.0)  
**Status:** TO FIX

Example:
```python
# OLD (deprecated):
response = openai.ChatCompletion.create(...)

# NEW (openai>=1.0.0):
client = OpenAI(api_key=api_key)
response = client.chat.completions.create(...)
```

---

### 3. **Potential KeyError in web_scanner.py** ⚠️
**File:** `web_scanner.py`  
**Line:** 226  
**Issue:** `headers.get(header, '')` but header is lowercase, headers dict may have mixed case  
**Code:**
```python
for header in disclosure_headers:
    if header in {k.lower(): v for k, v in headers.items()}:
        findings.append({
            'evidence': f"{header}: {headers.get(header, '')}"  # ← KeyError risk
```
**Problem:** Using lowercase `header` to check but using it directly to get value  
**Severity:** Medium (runtime error possible)  
**Status:** TO FIX

---

### 4. **No SSL/TLS Error Handling in web_scanner.py** ⚠️
**File:** `web_scanner.py`  
**Line:** 93  
**Issue:** `aiohttp.ClientSession.get()` may fail on SSL errors  
**Should:** Add `ssl=False` for testing or proper SSL verification  
**Severity:** Minor (might fail on self-signed certs)  
**Status:** OPTIONAL FIX

---

### 5. **Large File Memory Issue in code_scanner.py** ⚠️
**File:** `code_scanner.py`  
**Line:** 89  
**Issue:** `file_path.read_text()` loads entire file into memory  
**Problem:** Large files (>100MB) could cause memory issues  
**Current:** Has check at line 116 (`if len(content) < 10000`)  
**Severity:** Low (already has size check)  
**Status:** OK (already mitigated)

---

### 6. **Missing Try-Except in _crawl Method** ⚠️
**File:** `web_scanner.py`  
**Lines:** 73-119  
**Issue:** Uses `await self.session.get()` which could timeout/fail  
**Current:** Has try-except ✅  
**Status:** OK

---

### 7. **Regex Injection Risk in Pattern Matching** ⚠️
**File:** `code_scanner.py`, `web_scanner.py`  
**Issue:** All patterns are hardcoded  
**Status:** OK (no user input in regex)

---

### 8. **Missing API Key Validation** ⚠️
**File:** `llm_analyzer.py`  
**Lines:** 195-197, 246-248, 267-269  
**Issue:** Checks `if not api_key` but doesn't validate format  
**Current:** Raises ValueError if missing ✅  
**Severity:** Low  
**Status:** OK (basic validation present)

---

## Priority Fixes

### High Priority (Breaking)
1. ✅ **OpenAI API deprecation** → Must fix for openai>=1.0.0
2. ✅ **Typo in description** → Easy fix
3. ✅ **KeyError in headers access** → Potential runtime error

### Medium Priority (Good to have)
4. **SSL handling** → Add ssl parameter option
5. **Better error messages** → More descriptive exceptions

### Low Priority (Nice to have)
6. **Type hints consistency** → Already good
7. **Logging instead of print()** → Use proper logger

---

## Recommended Fixes

### Fix 1: Update OpenAI API Usage
```python
# llm_analyzer.py, line 188-237
async def _call_openai(self, prompt: str) -> str:
    """Call OpenAI API"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")
    
    api_key = self.api_keys.get_key('openai')
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        self.usage_stats['total_tokens'] += response.usage.total_tokens
        
        return content
        
    except Exception as e:
        # Fallback to gpt-3.5-turbo if gpt-4 fails
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a security expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            self.usage_stats['total_tokens'] += response.usage.total_tokens
            
            return content
        except:
            raise e
```

### Fix 2: Typo in code_scanner.py
```python
# Line 204
'description': 'Potential SQL injection via string formatting',  # Fixed typo
```

### Fix 3: KeyError in web_scanner.py
```python
# Lines 219-230
for header in disclosure_headers:
    headers_lower = {k.lower(): (k, v) for k, v in headers.items()}
    if header in headers_lower:
        original_key, value = headers_lower[header]
        findings.append({
            'type': 'info_disclosure',
            'severity': 'low',
            'url': url,
            'description': f'Server version disclosed in {header} header',
            'evidence': f"{original_key}: {value}",  # Fixed
            'remediation': f'Remove or obfuscate {header} header',
            'source': 'static',
            'confidence': 1.0
        })
```

---

## Summary

**Total Issues Found:** 8  
**Critical:** 1 (OpenAI API)  
**High:** 1 (KeyError)  
**Medium:** 1 (Typo)  
**Low:** 5 (Various)

**Files Affected:**
- `llm_analyzer.py` → OpenAI API update needed
- `code_scanner.py` → Typo fix
- `web_scanner.py` → Header access fix

All other code looks solid with proper error handling! 👍
