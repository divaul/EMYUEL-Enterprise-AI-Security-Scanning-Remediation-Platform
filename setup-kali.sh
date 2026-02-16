#!/bin/bash
# EMYUEL Setup Script for Kali Linux
# Simple Python-based installation (NO Docker required)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Header
clear
echo -e "${CYAN}"
cat << "EOF"
    ███████╗███╗   ███╗██╗   ██╗██╗   ██╗███████╗██╗     
    ██╔════╝████╗ ████║╚██╗ ██╔╝██║   ██║██╔════╝██║     
    █████╗  ██╔████╔██║ ╚████╔╝ ██║   ██║█████╗  ██║     
    ██╔══╝  ██║╚██╔╝██║  ╚██╔╝  ██║   ██║██╔══╝  ██║     
    ███████╗██║ ╚═╝ ██║   ██║   ╚██████╔╝███████╗███████╗
    ╚══════╝╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚══════╝
    
    AI-Powered Security Scanner - Kali Linux Setup
EOF
echo -e "${NC}"
echo ""

print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC}  $1"
}

# Check if running on Kali Linux
check_kali() {
    print_header "Checking System"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "kali" ]]; then
            print_success "Running on Kali Linux $VERSION"
            return 0
        fi
    fi
    print_warning "Not running on Kali Linux, but will continue..."
    return 0
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        echo "Installing Python 3..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
        print_success "Python 3 installed"
    else
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
        
        # Check Python version (need 3.10+)
        PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VER="3.10"
        
        if [ "$(printf '%s\n' "$REQUIRED_VER" "$PYTHON_VER" | sort -V | head -n1)" != "$REQUIRED_VER" ]; then
            print_warning "Python $PYTHON_VER found, but 3.10+ recommended"
            print_info "Trying to install python3.11..."
            sudo apt update
            sudo apt install -y python3.11 python3.11-venv python3.11-dev || true
        fi
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_error "pip not found"
        echo "Installing pip..."
        sudo apt install -y python3-pip
        print_success "pip installed"
    else
        print_success "pip found"
    fi
    
    # Check venv
    if ! python3 -m venv --help &> /dev/null; then
        print_error "python3-venv not found"
        echo "Installing python3-venv..."
        sudo apt install -y python3-venv
        print_success "python3-venv installed"
    else
        print_success "python3-venv available"
    fi
    
    # Check tkinter for GUI
    if ! python3 -c "import tkinter" &> /dev/null; then
        print_warning "tkinter not found (required for GUI mode)"
        echo "Installing python3-tk..."
        sudo apt install -y python3-tk
        print_success "python3-tk installed"
    else
        print_success "tkinter available (GUI supported)"
    fi
}

# Install system dependencies
install_dependencies() {
    print_header "Installing System Dependencies"
    
    print_info "Installing required Kali packages..."
    
    # Essential packages for security scanning
    PACKAGES=(
        "python3-dev"
        "build-essential"
        "libssl-dev"
        "libffi-dev"
        "libpq-dev"
        "git"
        "curl"
        "wget"
    )
    
    sudo apt update
    
    for pkg in "${PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii  $pkg "; then
            print_success "$pkg already installed"
        else
            echo "Installing $pkg..."
            sudo apt install -y "$pkg" || print_warning "Failed to install $pkg"
        fi
    done
}

# Create virtual environment
create_venv() {
    print_header "Creating Virtual Environment"
    
    if [ -d "venv" ]; then
        read -p "$(echo -e ${YELLOW}Virtual environment exists. Recreate? [y/N]:${NC} )" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing old virtual environment..."
            rm -rf venv
        else
            print_warning "Using existing virtual environment"
            return 0
        fi
    fi
    
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ ! -d "venv" ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment created"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install packaging for version comparison
    echo "Installing dependency management tools..."
    pip install packaging --quiet
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Check system tools first
    echo ""
    print_header "Checking System Tools and Frameworks"
    echo ""
    
    if python3 check_system_tools.py; then
        print_success "System tools check completed"
    else
        print_warning "Some system tools are missing or outdated"
        echo "The script will continue, but some features may not work"
    fi
    
    # Run smart dependency checker
    echo ""
    print_header "Checking and Managing Python Dependencies"
    echo ""
    
    if python3 check_dependencies.py; then
        print_success "Dependencies managed successfully"
    else
        print_warning "Dependency checker had issues, attempting full install..."
        pip install -r requirements.txt
    fi
    
    # Check cybersecurity tools
    echo ""
    print_header "Checking Cybersecurity Tools"
    echo ""
    
    python3 check_security_tools.py
    
    echo ""
    print_success "Dependency checks completed"
}

# Setup environment file
setup_env() {
    print_header "Setting Up Environment"
    
    if [ -f ".env" ]; then
        read -p "$(echo -e ${YELLOW}.env file exists. Overwrite? [y/N]:${NC} )" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Skipping .env setup"
            return 0
        fi
    fi
    
    if [ ! -f ".env.example" ]; then
        print_error ".env.example not found"
        print_warning "Skipping environment setup"
        return 0
    fi
    
    cp .env.example .env
    print_success "Created .env file from template"
    
    # Configure API key
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}LLM API Key Configuration${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    echo "Choose your LLM provider:"
    echo "  1) OpenAI (GPT-4)"
    echo "  2) Google Gemini"
    echo "  3) Anthropic Claude"
    echo "  4) Configure later"
    echo ""
    read -p "Select option [1-4]: " PROVIDER_CHOICE
    
    case $PROVIDER_CHOICE in
        1)
            read -p "Enter OpenAI API key: " OPENAI_KEY
            if [ ! -z "$OPENAI_KEY" ]; then
                sed -i "s|OPENAI_API_KEY=|OPENAI_API_KEY=$OPENAI_KEY|g" .env
                sed -i "s|LLM_PRIMARY_PROVIDER=.*|LLM_PRIMARY_PROVIDER=openai|g" .env
                print_success "OpenAI configured as primary provider"
            fi
            ;;
        2)
            read -p "Enter Google AI API key: " GEMINI_KEY
            if [ ! -z "$GEMINI_KEY" ]; then
                sed -i "s|GOOGLE_AI_API_KEY=|GOOGLE_AI_API_KEY=$GEMINI_KEY|g" .env
                sed -i "s|LLM_PRIMARY_PROVIDER=.*|LLM_PRIMARY_PROVIDER=gemini|g" .env
                print_success "Gemini configured as primary provider"
            fi
            ;;
        3)
            read -p "Enter Anthropic API key: " CLAUDE_KEY
            if [ ! -z "$CLAUDE_KEY" ]; then
                sed -i "s|ANTHROPIC_API_KEY=|ANTHROPIC_API_KEY=$CLAUDE_KEY|g" .env
                sed -i "s|LLM_PRIMARY_PROVIDER=.*|LLM_PRIMARY_PROVIDER=claude|g" .env
                print_success "Claude configured as primary provider"
            fi
            ;;
        4)
            print_warning "API key configuration skipped"
            print_info "Configure later with: python -m cli.emyuel_cli config --provider openai"
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

# Create necessary directories
create_directories() {
    print_header "Creating Directories"
    
    DIRS=(
        "reports"
        "logs"
        "$HOME/.emyuel/states"
        "$HOME/.emyuel/cache"
        "$HOME/.emyuel"
    )
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created $dir"
        else
            print_success "$dir exists"
        fi
    done
    
    # Initialize database
    print_header "Initializing Database"
    
    if [ -f "$HOME/.emyuel/scan_history.db" ]; then
        print_success "Scan history database already exists"
    else
        print_info "Creating scan history database..."
        
        # Activate venv if not already active
        if [ -z "$VIRTUAL_ENV" ]; then
            source venv/bin/activate
        fi
        
        # Initialize database by running a simple Python script
        python3 -c "
from services.database.db_manager import DatabaseManager
try:
    db = DatabaseManager()
    print('[DB] ✅ Database initialized successfully')
    print(f'[DB] Location: {db.db_path}')
except Exception as e:
    print(f'[DB] ⚠️ Failed to initialize database: {e}')
    exit(1)
" && print_success "Database initialized at $HOME/.emyuel/scan_history.db" || print_warning "Database initialization failed (will be created on first run)"
    fi
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    source venv/bin/activate
    
    # Test imports
    echo "Testing Python imports..."
    python3 -c "
try:
    import rich
    import click
    import openai
    import anthropic
    import google.generativeai
    import aiohttp
    import beautifulsoup4
    print('✓ All core dependencies imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
" && print_success "Core dependencies verified" || print_error "Dependency verification failed"
    
    # Test CLI
    if python3 -m cli.emyuel_cli --help &> /dev/null; then
        print_success "CLI interface working"
    else
        print_warning "CLI interface check failed"
    fi
    
    # Test GUI imports
    if python3 -c "import tkinter" &> /dev/null; then
        print_success "GUI dependencies verified"
    else
        print_warning "GUI dependencies missing (run: sudo apt install python3-tk)"
    fi
    
    # Test AI modules
    if python3 -c "from services.ai_planner import AIPlanner; from services.executor import Executor" &> /dev/null; then
        print_success "AI Analysis modules verified"
    else
        print_warning "AI Analysis modules check failed"
    fi
}

# Print completion information
print_completion() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}✓ EMYUEL successfully installed on Kali Linux!${NC}"
    echo ""
    
    echo -e "${CYAN}Quick Start:${NC}"
    echo ""
    echo -e "${YELLOW}1. Activate virtual environment:${NC}"
    echo "   source venv/bin/activate"
    echo ""
    
    echo -e "${YELLOW}2. Run CLI scan:${NC}"
    echo "   python -m cli.emyuel_cli scan --target /path/to/code"
    echo ""
    
    echo -e "${YELLOW}3. Run GUI mode:${NC}"
    echo "   python -m gui.emyuel_gui"
    echo ""
    echo -e "${CYAN}   GUI Features:${NC}"
    echo "   • Quick Scan tab - URL input + vulnerability selection"
    echo "   • Advanced Scan tab - Directory scanning"
    echo "   • 🤖 AI Analysis tab - Autonomous AI-driven testing"
    echo "   • API Keys tab - Configure OpenAI/Gemini/Claude"
    echo "   • 📊 Results tab - Real-time scan monitoring"
    echo "   • 📋 Reports tab - View findings, browse history, generate reports"
    echo "   • 🗄️ Database - Persistent scan history (SQLite)"
    echo ""
    
    echo -e "${YELLOW}4. Configure API keys (if skipped):${NC}"
    echo "   python -m cli.emyuel_cli config --provider openai"
    echo ""
    
    echo -e "${CYAN}Available Commands:${NC}"
    echo "  scan     - Start security scan"
    echo "  resume   - Resume paused scan"
    echo "  list     - List resumable scans"
    echo "  report   - Generate scan reports"
    echo "  config   - Configure API keys"
    echo ""
    
    echo -e "${CYAN}Example Scans:${NC}"
    echo "  # Full scan"
    echo "  python -m cli.emyuel_cli scan --target /var/www/myapp"
    echo ""
    echo "  # Targeted scan"
    echo "  python -m cli.emyuel_cli scan --target /opt/webapp --modules sqli,xss"
    echo ""
    echo "  # With specific provider"
    echo "  python -m cli.emyuel_cli scan --target ~/code --provider gemini"
    echo ""
    
    echo -e "${CYAN}New Features:${NC}"
    echo "  🤖 AI Analysis - Autonomous security testing with GPT-4"
    echo "  🔓 Brute Force - Authentication testing (default creds, wordlist, exhaustive)"
    echo "  💬 Natural Language - English & Indonesian query support"
    echo "  🎨 Enhanced GUI - Modern design with gradient buttons"
    echo "  🗄️ Database - Persistent scan history with search & export"
    echo ""
    
    echo -e "${CYAN}Documentation:${NC}"
    echo "  Quick Start:        QUICKSTART.md"
    echo "  Full Docs (ID):     DOKUMENTASI_PROGRAM.md"
    echo "  Architecture:       docs/ARCHITECTURE.md"
    echo "  Bug Fixes:          .gemini/antigravity/brain/.../bug_fixes.md"
    echo ""
    
    echo -e "${YELLOW}⚠  Important Notes:${NC}"
    echo "  • Docker is NOT required - runs natively on Python"
    echo "  • API key needed from OpenAI/Gemini/Claude"
    echo "  • Activate venv before running: source venv/bin/activate"
    echo "  • Reports saved to: ./reports/"
    echo "  • AI Analysis requires OpenAI API key"
    echo ""
    
    print_success "Ready to scan! Happy hacking! 🛡️"
}

# Main installation flow
main() {
    check_kali
    check_prerequisites
    install_dependencies
    create_venv
    install_python_deps
    setup_env
    create_directories
    verify_installation
    print_completion
}

# Run main installation
main
