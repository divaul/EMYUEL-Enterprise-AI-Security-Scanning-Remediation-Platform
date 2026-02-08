# Quick Fix untuk ModuleNotFoundError

## Masalah

Error `ModuleNotFoundError` terjadi karena:
- Direktori menggunakan **dash** (`api-key-manager`)
- Python import menggunakan **underscore** (`api_key_manager`)

Python tidak bisa import modul dengan nama yang mengandung dash (-).

## Solusi yang Sudah Diterapkan

Saya telah membuat file stub/wrapper:

✅ **libs/api_key_manager.py** - wrapper untuk libs/api-key-manager/  
✅ **libs/scanner_state.py** - wrapper untuk libs/scanner-state/  
✅ **services/scanner_core.py** - wrapper untuk services/scanner-core/  
✅ **libs/__init__.py** - package initialization  
✅ **services/__init__.py** - package initialization  

## Cara Test

```bash
# Aktifkan virtual environment
source venv/bin/activate

# Test imports
python3 -c "from libs.api_key_manager import APIKeyManager; print('✓ API Key Manager OK')"
python3 -c "from libs.scanner_state import StateManager; print('✓ State Manager OK')"
python3 -c "from services.scanner_core import ScannerCore; print('✓ Scanner Core OK')"

# Test CLI
python -m cli.emyuel_cli --help

# Test GUI
python -m gui.emyuel_gui
```

## Jika Masih Error

Jika masih ada error, coba:

```bash
# Re-install dalam editable mode
pip install -e .

# Atau tambahkan PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Catatan

File stub ini menyediakan:
1. **Fallback implementation** - Implementasi minimal jika file asli tidak ditemukan
2. **Path bridging** - Menghubungkan dash-named directories dengan underscore imports
3. **Graceful degradation** - Program tetap bisa jalan meski implementasi penuh belum ada

Implementasi lengkap ada di direktori dengan dash, tetapi stub files memungkinkan Python untuk melakukan import yang benar.
