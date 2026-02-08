# Running EMYUEL on Kali Linux

Complete guide for deploying EMYUEL security platform on Kali Linux.

## Prerequisites

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
sudo apt install -y docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Apply group changes (logout/login or run)
newgrp docker

# Verify installation
docker --version
```

### 3. Install Docker Compose

```bash
# Install Docker Compose
sudo apt install -y docker-compose

# Verify installation
docker-compose --version
```

### 4. Install Python 3.11+ (Optional - for setup script)

```bash
# Kali Linux usually has Python 3.11+
python3 --version

# If needed, install Python
sudo apt install -y python3 python3-pip python3-venv
```

---

## Installation Steps

### Method 1: Automated Setup (Recommended)

```bash
# Navigate to project directory
cd /path/to/emyuel

# Make setup script executable
chmod +x setup.py

# Run setup script
python3 setup.py
```

The script will:
- ✅ Check Docker installation
- ✅ Generate secure secrets automatically
- ✅ Create `.env` file
- ✅ Start all services via Docker Compose

### Method 2: Manual Setup

```bash
# 1. Clone or navigate to project
cd /path/to/emyuel

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env file
nano .env

# Add at least ONE LLM API key:
# OPENAI_API_KEY=sk-your-key-here
# OR
# GOOGLE_AI_API_KEY=your-key-here
# OR
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# 4. Generate secure secrets
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(16))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(16))"

# Add these to .env file

# 5. Start services
docker-compose up -d
```

---

## Verify Installation

### Check Running Services

```bash
# List all running containers
docker-compose ps

# Expected output: All services should be "Up"
# - emyuel-postgres
# - emyuel-redis
# - emyuel-api-gateway
# - emyuel-scanner
# - emyuel-celery-worker
# - emyuel-prometheus
# - emyuel-grafana
# - emyuel-frontend
```

### Check Service Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api-gateway
docker-compose logs scanner-core

# Follow logs in real-time
docker-compose logs -f api-gateway
```

### Test API Endpoint

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","environment":"development","version":"1.0.0"}
```

---

## Access Services

Once all services are running:

### 1. API Documentation (Swagger)
```bash
# Open in browser
firefox http://localhost:8000/api/docs

# Or use curl to explore
curl http://localhost:8000/api/v1/
```

### 2. Frontend Dashboard
```bash
firefox http://localhost:8080
```

**Default Login**:
- Email: `admin@emyuel.local`
- Password: `admin123`

⚠️ **Change this immediately in production!**

### 3. Grafana Dashboards
```bash
firefox http://localhost:3000
```

**Default Login**:
- Username: `admin`
- Password: Check `GRAFANA_ADMIN_PASSWORD` in `.env` (default: `admin`)

### 4. Prometheus Metrics
```bash
firefox http://localhost:9090
```

---

## Running Your First Scan

### Option 1: Using API with curl

```bash
# 1. Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@emyuel.local",
    "password": "admin123"
  }'

# Save the access_token from response

# 2. Create a scan (replace YOUR_TOKEN and YOUR_PROJECT_ID)
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_ID",
    "scan_type": "quick"
  }'
```

### Option 2: Using Python

```bash
# Install requests library
pip3 install requests

# Run Python script
python3 << 'EOF'
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@emyuel.local", "password": "admin123"}
)
token = response.json()["access_token"]

# Create scan
response = requests.post(
    "http://localhost:8000/api/v1/scans",
    headers={"Authorization": f"Bearer {token}"},
    json={"project_id": "YOUR_PROJECT_ID", "scan_type": "quick"}
)
print(response.json())
EOF
```

---

## Integration with Kali Linux Tools

EMYUEL can complement existing Kali Linux security tools:

### 1. Scan Web Application (combine with Burp/OWASP ZAP)

```bash
# Use EMYUEL for static analysis
# Use Burp Suite/ZAP for dynamic analysis
# Correlate findings for comprehensive coverage
```

### 2. Integration with Nmap

```bash
# First, scan ports with nmap
nmap -sV target.com

# Then analyze discovered web services with EMYUEL
# Point EMYUEL scanner to the source code repository
```

### 3. Scripted Scanning

```bash
#!/bin/bash
# automated-security-scan.sh

# Run nmap scan
echo "[+] Running nmap scan..."
nmap -sV -oX nmap-results.xml $TARGET

# Run EMYUEL static analysis
echo "[+] Running EMYUEL scan..."
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"scan_type\": \"comprehensive\"}"

# Export results
echo "[+] Exporting results..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/reports/export
```

---

## Troubleshooting on Kali Linux

### Docker Permission Denied

```bash
# If you get "permission denied" error
sudo usermod -aG docker $USER
newgrp docker

# Or restart system
sudo reboot
```

### Port Already in Use

```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill the process if needed
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Change external port
```

### Services Won't Start

```bash
# Check Docker logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Connect to PostgreSQL manually
docker-compose exec postgres psql -U emyuel_user -d emyuel
```

---

## Performance Optimization on Kali Linux

### 1. Allocate More Resources

```bash
# Edit docker-compose.yml to limit resources
services:
  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

### 2. Use SSD for Docker Storage

```bash
# Move Docker data to SSD
sudo systemctl stop docker
sudo mv /var/lib/docker /path/to/ssd/docker
sudo ln -s /path/to/ssd/docker /var/lib/docker
sudo systemctl start docker
```

### 3. Enable Swap if Needed

```bash
# Check swap
free -h

# Create swap file if needed (2GB example)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Security Hardening on Kali Linux

### 1. Use Firewall

```bash
# Allow only necessary ports
sudo ufw allow 8000/tcp  # API Gateway
sudo ufw allow 8080/tcp  # Frontend
sudo ufw enable
```

### 2. Use Strong Passwords

```bash
# Generate strong password for database
openssl rand -base64 32

# Add to .env file
```

### 3. Enable SSL/TLS (Production)

```bash
# Use nginx reverse proxy with Let's Encrypt
sudo apt install -y nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## Updating EMYUEL

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check migration status
docker-compose exec api-gateway alembic current
docker-compose exec api-gateway alembic upgrade head
```

---

## Backup and Restore

### Backup Database

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U emyuel_user emyuel > backup_$(date +%Y%m%d).sql

# Backup with compression
docker-compose exec postgres pg_dump -U emyuel_user emyuel | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T postgres psql -U emyuel_user emyuel < backup_20260130.sql

# Restore from compressed backup
gunzip -c backup_20260130.sql.gz | docker-compose exec -T postgres psql -U emyuel_user emyuel
```

---

## Uninstall

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove Docker images
docker rmi $(docker images -q 'emyuel*')

# Remove project directory
rm -rf /path/to/emyuel
```

---

## Additional Resources

- [Kali Linux Documentation](https://www.kali.org/docs/)
- [Docker on Kali Linux](https://www.kali.org/docs/containers/installing-docker-on-kali/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `.env` file
3. Test connectivity: `curl http://localhost:8000/health`
4. GitHub Issues: Report bugs and get help

---

**Note**: Kali Linux is designed for penetration testing. EMYUEL complements it by providing AI-powered static code analysis alongside Kali's dynamic testing tools.
