# Cara Mengintegrasikan AI Analysis Tab ke GUI

Untuk mengintegrasikan fitur AI Analysis ke `emyuel_gui.py`, ikuti langkah berikut:

## 1. Salin methods dari `ai_analysis_tab_methods.py`

Buka file `gui/ai_analysis_tab_methods.py` yang sudah dibuat, lalu salin semua methods:
- `setup_ai_analysis_tab()`
- `start_ai_analysis()`
- `run_ai_analysis()`
- `ai_log_console()`
- `ai_update_reasoning()`
- `ai_display_test_plan()`
- `ai_update_step_status()`

## 2. Insert methods ke `emyuel_gui.py`

Tambahkan methods tersebut di class `EMYUELGUI`, **sebelum** method `run()` (sekitar baris 1573).

Location untuk insert:
```python
class EMYUELGUI:
    def __init__(self): ...
    
    # ... existing methods ...
    
    def log_console(self, message): ...
    
    # INSERT AI ANALYSIS METHODS HERE (before run())
    def setup_ai_analysis_tab(self, parent): ...
    def start_ai_analysis(self): ...
    def run_ai_analysis(self, target_url, api_key): ...
    # ... etc
    
    def run(self):
        """Run the GUI"""
        ...
```

## 3. Atau gunakan approach sederhana

Alternatif: gunakan `exec()` atau import untuk load methods:

```python
# Di akhir __init__ method
# Load AI Analysis methods
import importlib.util
spec = importlib.util.spec_from_file_location("ai_methods", "gui/ai_analysis_tab_methods.py")
ai_methods = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_methods)

# Bind methods to self
for method_name in dir(ai_methods):
    if method_name.startswith('setup_ai') or method_name.startswith('ai_') or method_name == 'start_ai_analysis' or method_name == 'run_ai_analysis':
        setattr(self, method_name, types.MethodType(getattr(ai_methods, method_name), self))
```

## 4. Testing

1. Jalankan GUI:
   ```bash
   python -m gui.emyuel_gui
   ```

2. Pastikan tab "🤖 AI Analysis" muncul

3. Configure OpenAI API key di tab API Keys

4. Test dengan URL: `https://testphp.vulnweb.com`

5. Klik "🚀 Start AI Analysis"

## 5. Troubleshooting

**Error: "module 'openai' not found"**
```bash
pip install openai
```

**Error: API Key invalid**
- Pastikan OpenAI API key valid di tab API Keys
- Format: `sk-...`

**Error: No AI tab**
- Check bahwa `setup_ai_analysis_tab` dipanggil di `setup_ui()`
- Tab sudah ditambahkan ke notebook (baris 270-272)

## 6. Usage Flow

```
1. User input URL
2. Click "Start AI Analysis"
3. AI Planner analyzes target
4. Plan displayed in steps section
5. Executor runs each step
6. Real-time updates in console
7. AI reviews results after each step
8. Final report generated
```

Enjoy your cutting-edge AI-driven security analysis! 🤖🛡️
