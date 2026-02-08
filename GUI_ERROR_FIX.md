# ⚠️ PENTING: GUI Memerlukan Display Server!

## Error yang Anda Alami

```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

Ini berarti **tidak ada X display server** yang tersedia.

---

## ✅ SOLUSI TERCEPAT: GUNAKAN CLI MODE

**CLI mode tidak butuh display dan lebih cocok untuk Kali Linux!**

```bash
# Aktifkan virtual environment
source venv/bin/activate

# Gunakan CLI (bukan GUI)
python -m cli.emyuel_cli --help

# Contoh scan
python -m cli.emyuel_cli scan --target /path/to/your/code

# Configure API key
python -m cli.emyuel_cli config --provider openai

# List scans yang bisa di-resume
python -m cli.emyuel_cli list

# Generate report
python -m cli.emyuel_cli report --scan-id scan_123 --format all
```

---

## Kenapa CLI Lebih Baik untuk Kali?

✅ **Tidak butuh X server** - Jalan di SSH, headless, dll  
✅ **Lebih ringan** - Minimal resource usage  
✅ **Lebih cepat** - No GUI overhead  
✅ **Automation-friendly** - Bisa di-script  
✅ **Perfect untuk pentesting** - Sesuai workflow Kali Linux  

---

## Jika Tetap Ingin GUI

### Opsi 1: X11 Forwarding (SSH)

```bash
# Di komputer lokal, SSH dengan X11:
ssh -X user@kali-machine

# Verify DISPLAY:
echo $DISPLAY  # Harus ada output

# Jalankan GUI:
python -m gui.emyuel_gui
```

### Opsi 2: Virtual Display

```bash
# Install xvfb
sudo apt install xvfb

# Jalankan dengan virtual display
xvfb-run python -m gui.emyuel_gui
```

### Opsi 3: Desktop Environment

```bash
# Jika Kali tidak punya desktop:
sudo apt install kali-desktop-xfce
startx

# Lalu jalankan GUI
python -m gui.emyuel_gui
```

---

## Panduan Lengkap

Lihat **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** untuk solusi detail semua error.

---

## Rekomendasi

**Untuk security scanning di Kali Linux, gunakan CLI mode.**  
GUI hanya diperlukan jika Anda perlu interface visual, yang jarang dibutuhkan dalam penetration testing.
