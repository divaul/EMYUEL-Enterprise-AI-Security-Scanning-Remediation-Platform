# EMYUEL - Deployment Options

## ⚡ Recommended: Python Native (NO Docker)

EMYUEL is a **Python-native application** that runs directly without Docker. This is the **simplest and fastest** way to get started.

### Why Python Native?

✅ **Simpler** - No Docker installation needed  
✅ **Faster** - Direct Python execution, no container overhead  
✅ **Lighter** - Uses ~500MB vs Docker's ~2GB+  
✅ **Easier debugging** - Direct access to logs and code  
✅ **Perfect for Kali Linux** - Works out of the box  

### Installation

```bash
# Kali Linux / Debian / Ubuntu
chmod +x setup-kali.sh
./setup-kali.sh

# Other Linux
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

### Usage

```bash
# Activate virtual environment
source venv/bin/activate  # Linux
venv\Scripts\activate.bat  # Windows

# Run CLI
python -m cli.emyuel_cli scan --target /path/to/code

# Run GUI
python -m gui.emyuel_gui
```

---

## 🐳 Optional: Docker Deployment

Docker is **OPTIONAL** and only recommended for:
- Production microservices deployment
- Multiple team members
- Enterprise environments
- Auto-scaling requirements

### When to Use Docker

- ❌ **NOT for development** - Python native is faster
- ❌ **NOT for single user** - Unnecessary complexity
- ✅ **YES for production clusters** - Kubernetes deployment
- ✅ **YES for CI/CD pipelines** - Isolated environments

### Docker Installation

```bash
# Start with Docker Compose
docker-compose up -d

# Access dashboard
open http://localhost:8080
```

### Docker vs Native Comparison

| Feature | Python Native | Docker |
|---------|--------------|--------|
| Setup Time | 2 minutes | 10+ minutes |
| RAM Usage | ~500MB | ~2GB+ |
| Disk Space | ~1GB | ~5GB+ |
| Startup Speed | Instant | 30+ seconds |
| Debugging | Easy | Complex |
| Best For | Development, Single User | Production, Teams |

---

## 📊 Summary

**For Kali Linux Users:**
- Use `setup-kali.sh` (Python native)
- Docker is NOT required
- Lighter, faster, simpler

**For Development:**
- Python native installation
- Direct code access
- Easy debugging

**For Production:**
- Consider Docker/Kubernetes
- Full microservices architecture
- Auto-scaling support

**Our Recommendation:** Start with Python native. Only use Docker if you specifically need microservices deployment.
