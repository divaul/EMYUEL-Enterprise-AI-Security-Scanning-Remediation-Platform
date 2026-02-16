#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# EMYUEL - Enterprise AI-Powered Security Scanner
# Automated Setup Script for Linux (Kali, Ubuntu, Debian, etc.)
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# ═══════════════════════════════════════════════════════════════════════════
# COLOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Bold colors
BRED='\033[1;31m'
BGREEN='\033[1;32m'
BYELLOW='\033[1;33m'
BCYAN='\033[1;36m'

# Background colors
BG_BLUE='\033[44m'
BG_GREEN='\033[42m'
BG_RED='\033[41m'

# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY BANNER
# ═══════════════════════════════════════════════════════════════════════════
clear
echo -e "${CYAN}"
cat << "EOF"
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   ███████╗███╗   ███╗██╗   ██╗██╗   ██╗███████╗██╗                   ║
    ║   ██╔════╝████╗ ████║╚██╗ ██╔╝██║   ██║██╔════╝██║                   ║
    ║   █████╗  ██╔████╔██║ ╚████╔╝ ██║   ██║█████╗  ██║                   ║
    ║   ██╔══╝  ██║╚██╔╝██║  ╚██╔╝  ██║   ██║██╔══╝  ██║                   ║
    ║   ███████╗██║ ╚═╝ ██║   ██║   ╚██████╔╝███████╗███████╗              ║
    ║   ╚══════╝╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚══════╝              ║
    ║                                                                       ║
    ║        Enterprise AI-Powered Security Scanning Platform              ║
    ║                    Automated Setup Wizard                            ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo -e "${GRAY}    Version: 2.0.0 | Platform: Linux | Runtime: Python 3.10+${NC}"
echo -e "${GRAY}    ─────────────────────────────────────────────────────────────────${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${BCYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BCYAN}║${NC} ${WHITE}$1${NC}"
    echo -e "${BCYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${BGREEN}[✓]${NC} ${GREEN}$1${NC}"
}

print_error() {
    echo -e "${BRED}[✗]${NC} ${RED}$1${NC}"
}

print_warning() {
    echo -e "${BYELLOW}[!]${NC} ${YELLOW}$1${NC}"
}

print_info() {
    echo -e "${BCYAN}[ℹ]${NC} ${CYAN}$1${NC}"
}

print_step() {
    echo -e "${BLUE}[→]${NC} ${WHITE}$1${NC}"
}

print_separator() {
    echo -e "${GRAY}    ─────────────────────────────────────────────────────────────────${NC}"
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
    print_header "📦 INSTALLING SYSTEM DEPENDENCIES"
    
    print_info "Updating package repositories..."
    print_separator
    
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
    
    sudo apt update > /dev/null 2>&1
    
    local total=${#PACKAGES[@]}
    local current=0
    
    for pkg in "${PACKAGES[@]}"; do
        current=$((current + 1))
        echo -ne "\r${BLUE}[→]${NC} Installing packages... ${BCYAN}[$current/$total]${NC} ${pkg}                    "
        
        if dpkg -l | grep -q "^ii  $pkg "; then
            echo -ne "\r"
            print_success "$pkg ${GRAY}(already installed)${NC}"
        else
            if sudo apt install -y "$pkg" > /dev/null 2>&1; then
                echo -ne "\r"
                print_success "$pkg ${GRAY}(newly installed)${NC}"
            else
                echo -ne "\r"
                print_warning "$pkg ${GRAY}(failed to install)${NC}"
            fi
        fi
    done
    
    echo ""
    print_separator
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
    
    python3 check_dependencies.py
    DEPS_EXIT_CODE=$?
    
    if [ $DEPS_EXIT_CODE -eq 0 ]; then
        print_success "Dependencies managed successfully"
    else
        print_warning "Some dependencies failed to install"
        echo ""
        echo -e "${YELLOW}⚠️  Common causes:${NC}"
        echo -e "   ${GRAY}• Network connectivity issues${NC}"
        echo -e "   ${GRAY}• Package version conflicts${NC}"
        echo -e "   ${GRAY}• Missing system libraries${NC}"
        echo ""
        echo -e "${BYELLOW}These packages are optional - setup will continue${NC}"
        echo -e "${GRAY}Install missing packages later: pip install <package-name>${NC}"
    fi
    
    echo ""
    # Check cybersecurity tools
    echo ""
    print_header "Checking Cybersecurity Tools"
    echo ""
    
    python3 check_security_tools.py
    TOOLS_EXIT_CODE=$?
    
    echo ""
    
    if [ $TOOLS_EXIT_CODE -eq 0 ]; then
        print_success "All required security tools are available"
    else
        print_warning "Some required security tools are missing"
        print_warning "Auto-installation may have failed - check output above"
        echo ""
        echo -e "${YELLOW}⚠️  You can:${NC}"
        echo -e "   ${GRAY}1. Install tools manually after setup${NC}"
        echo -e "   ${GRAY}2. Re-run: python3 check_security_tools.py${NC}"
        echo -e "   ${GRAY}3. Continue anyway (reduced functionality)${NC}"
        echo ""
        read -p "$(echo -e ${BYELLOW}Continue setup anyway? [Y/n]:${NC} )" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            echo ""
            print_error "Setup aborted by user"
            print_info "Install the missing tools and run ./setup.sh again"
            exit 1
        fi
    fi
    
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
" && print_success "Core dependencies verified" || { print_error "Dependency verification failed"; return 1; }
    
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
    
    return 0
}

# Print completion information
print_completion() {
    clear
    echo ""
    
    # Check if there were critical issues
    DEPS_FAILED=${DEPS_EXIT_CODE:-0}
    TOOLS_FAILED=${TOOLS_EXIT_CODE:-0}
    VERIFY_FAILED=${VERIFY_EXIT_CODE:-0}
    
    if [ $DEPS_FAILED -ne 0 ] || [ $TOOLS_FAILED -ne 0 ] || [ $VERIFY_FAILED -ne 0 ]; then
        # Setup with warnings
        echo -e "${BYELLOW}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BYELLOW}║${NC}                                                                       ${BYELLOW}║${NC}"
        echo -e "${BYELLOW}║${NC}    ${BYELLOW}⚠  SETUP COMPLETE - WITH WARNINGS${NC}                              ${BYELLOW}║${NC}"
        echo -e "${BYELLOW}║${NC}                                                                       ${BYELLOW}║${NC}"
        echo -e "${BYELLOW}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    else
        # Perfect installation
        echo -e "${BGREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BGREEN}║${NC}                                                                       ${BGREEN}║${NC}"
        echo -e "${BGREEN}║${NC}    ${BGREEN}✓  INSTALLATION SUCCESSFUL!${NC}                                   ${BGREEN}║${NC}"
        echo -e "${BGREEN}║${NC}                                                                       ${BGREEN}║${NC}"
        echo -e "${BGREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    fi
    echo ""
    
    print_header "🚀 QUICK START GUIDE"
    
    echo -e "${BCYAN}[1]${NC} ${WHITE}Activate Virtual Environment${NC}"
    echo -e "    ${GRAY}source venv/bin/activate${NC}"
    echo ""
    
    echo -e "${BCYAN}[2]${NC} ${WHITE}Launch GUI Mode${NC} ${BGREEN}(Recommended)${NC}"
    echo -e "    ${GRAY}python -m gui.emyuel_gui${NC}"
    echo ""
    
    echo -e "${BCYAN}[3]${NC} ${WHITE}Run CLI Scan${NC}"
    echo -e "    ${GRAY}python -m cli.emyuel_cli scan --target /path/to/code${NC}"
    echo ""
    
    print_separator
    print_header "⚡ FEATURES OVERVIEW"
    
    echo -e "${BCYAN}┌─${NC} ${WHITE}GUI Features${NC}"
    echo -e "${BCYAN}│${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}Quick Scan${NC}         ${GRAY}URL input + vulnerability selection${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}Advanced Scan${NC}      ${GRAY}Directory scanning with custom profiles${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}AI Analysis${NC}        ${GRAY}Autonomous AI-driven security testing${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}Results Monitor${NC}    ${GRAY}Real-time scan progress tracking${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}Reports Hub${NC}        ${GRAY}Browse history, search, export reports${NC}"
    echo -e "${BCYAN}├─${NC} ${BGREEN}▸${NC} ${GREEN}Database${NC}           ${GRAY}Persistent scan history (SQLite)${NC}"
    echo -e "${BCYAN}└─${NC} ${BGREEN}▸${NC} ${GREEN}API Keys${NC}           ${GRAY}Manage OpenAI/Gemini/Claude credentials${NC}"
    echo ""
    
    echo -e "${BCYAN}┌─${NC} ${WHITE}Security Modules${NC}"
    echo -e "${BCYAN}│${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}XSS Detection${NC}       ${GRAY}Cross-Site Scripting vulnerabilities${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}SQL Injection${NC}       ${GRAY}Database injection attacks${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}CSRF${NC}                ${GRAY}Cross-Site Request Forgery${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}Auth Bypass${NC}         ${GRAY}Authentication vulnerabilities${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}Headers${NC}             ${GRAY}Security header analysis${NC}"
    echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}Brute Force${NC}         ${GRAY}Credential testing${NC}"
    echo -e "${BCYAN}└─${NC} ${BYELLOW}◆${NC} ${YELLOW}AI-Powered${NC}          ${GRAY}GPT-4 autonomous testing${NC}"
    echo ""
    
    print_separator
    print_header "📁 DIRECTORY STRUCTURE"
    
    echo -e "${GRAY}  ~/.emyuel/                 ${BCYAN}Application Data${NC}"
    echo -e "${GRAY}  ├─ scan_history.db         ${GREEN}✓${NC} Scan database"
    echo -e "${GRAY}  ├─ states/                 ${GREEN}✓${NC} Scan states"
    echo -e "${GRAY}  └─ cache/                  ${GREEN}✓${NC} Cache files"
    echo ""
    echo -e "${GRAY}  ./reports/                 ${BCYAN}Generated Reports${NC}"
    echo -e "${GRAY}  ./logs/                    ${BCYAN}Application Logs${NC}"
    echo ""
    
    print_separator
    print_header "⚙️  CONFIGURATION"
    
    echo -e "${BCYAN}[→]${NC} ${WHITE}Configure API Keys${NC} ${GRAY}(if skipped during setup)${NC}"
    echo -e "    ${GRAY}python -m cli.emyuel_cli config --provider openai${NC}"
    echo ""
    
    echo -e "${BCYAN}[→]${NC} ${WHITE}Edit Environment${NC}"
    echo -e "    ${GRAY}nano .env${NC}"
    echo ""
    
    print_separator
    print_header "💡 PRO TIPS"
    
    echo -e "${BYELLOW}[!]${NC} ${YELLOW}Natural Language Queries${NC}"
    echo -e "    ${GRAY}Use English or Indonesian in AI Analysis tab${NC}"
    echo ""
    
    echo -e "${BYELLOW}[!]${NC} ${YELLOW}Scan History${NC}"
    echo -e "    ${GRAY}All scans are automatically saved to database${NC}"
    echo -e "    ${GRAY}Browse/export from Reports tab${NC}"
    echo ""
    
    echo -e "${BYELLOW}[!]${NC} ${YELLOW}Pause & Resume${NC}"
    echo -e "    ${GRAY}Scans automatically pause on API errors${NC}"
    echo -e "    ${GRAY}Click 'Resume' button to continue${NC}"
    echo ""
    
    print_separator
    
    echo ""
    echo -e "${BGREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BGREEN}║${NC}  ${WHITE}EMYUEL is ready!${NC}  Start scanning for vulnerabilities now! 🛡️       ${BGREEN}║${NC}"
    echo -e "${BGREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Interactive launcher - AT THE END OF SETUP
launch_app() {
    print_header "🚀 CHOOSE YOUR MODE"
    
    echo -e "${BCYAN}[1]${NC} ${WHITE}Launch GUI Mode${NC} ${BGREEN}⭐ Recommended${NC}"
    echo -e "    ${GRAY}Full-featured graphical interface${NC}"
    echo -e "    ${GRAY}Configure API keys in the GUI's API Keys tab${NC}"
    echo ""
    
    echo -e "${BCYAN}[2]${NC} ${WHITE}Terminal Mode${NC}"
    echo -e "    ${GRAY}Use CLI commands - configure API keys manually${NC}"
    echo ""
    
    read -p "$(echo -e ${BYELLOW}Select mode [1-2]:${NC} )" choice
    
    case $choice in
        1)
            # GUI Mode - Auto-launch
            print_separator
            echo ""
            print_info "Launching GUI mode..."
            echo ""
            
            # Activate venv and launch GUI
            source venv/bin/activate
            
            echo -e "${BCYAN}[→]${NC} Starting EMYUEL GUI..."
            echo -e "${GRAY}    Press Ctrl+C to stop${NC}"
            echo ""
            print_separator
            echo ""
            
            # Launch GUI in foreground
            python -m gui.emyuel_gui
            
            echo ""
            print_success "GUI closed. Thank you for using EMYUEL!"
            ;;
        2)
            # Terminal Mode - Show professional setup guide
            clear
            echo ""
            echo -e "${BGREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BGREEN}║${NC}                                                                       ${BGREEN}║${NC}"
            echo -e "${BGREEN}║${NC}    ${BGREEN}✓  SETUP COMPLETE - TERMINAL MODE${NC}                              ${BGREEN}║${NC}"
            echo -e "${BGREEN}║${NC}                                                                       ${BGREEN}║${NC}"
            echo -e "${BGREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            
            print_header "⚡ QUICK START - TERMINAL MODE"
            
            echo -e "${BCYAN}[1]${NC} ${WHITE}Activate Virtual Environment${NC}"
            echo -e "    ${GRAY}source venv/bin/activate${NC}"
            echo ""
            
            echo -e "${BCYAN}[2]${NC} ${WHITE}Configure API Keys${NC} ${BYELLOW}(Required)${NC}"
            echo -e "    ${BGREEN}▸${NC} ${GREEN}Using CLI Configuration Tool:${NC}"
            echo -e "      ${GRAY}python -m cli.emyuel_cli config --provider openai${NC}"
            echo ""
            echo -e "    ${BGREEN}▸${NC} ${GREEN}Or Edit .env File Directly:${NC}"
            echo -e "      ${GRAY}nano .env${NC}"
            echo -e "      ${GRAY}# Add one of:${NC}"
            echo -e "      ${GRAY}#   OPENAI_API_KEY=sk-...${NC}"
            echo -e "      ${GRAY}#   GOOGLE_AI_API_KEY=...${NC}"
            echo -e "      ${GRAY}#   ANTHROPIC_API_KEY=sk-ant-...${NC}"
            echo ""
            
            print_separator
            print_header "🔍 SCANNING COMMANDS"
            
            echo -e "${BCYAN}┌─${NC} ${WHITE}CLI Scan Examples${NC}"
            echo -e "${BCYAN}│${NC}"
            echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}Full Security Scan${NC}"
            echo -e "${BCYAN}│${NC}   ${GRAY}python -m cli.emyuel_cli scan --target /var/www/myapp${NC}"
            echo ""
            echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}Targeted Vulnerability Scan${NC}"
            echo -e "${BCYAN}│${NC}   ${GRAY}python -m cli.emyuel_cli scan --target /opt/webapp --modules sqli,xss${NC}"
            echo ""
            echo -e "${BCYAN}├─${NC} ${BYELLOW}◆${NC} ${YELLOW}With Specific AI Provider${NC}"
            echo -e "${BCYAN}│${NC}   ${GRAY}python -m cli.emyuel_cli scan --target ~/code --provider gemini${NC}"
            echo ""
            echo -e "${BCYAN}└─${NC} ${BYELLOW}◆${NC} ${YELLOW}Resume Paused Scan${NC}"
            echo -e "    ${GRAY}python -m cli.emyuel_cli resume --scan-id <scan-id>${NC}"
            echo ""
            
            print_separator
            print_header "🎨 GUI MODE (ALTERNATIVE)"
            
            echo -e "${BCYAN}[→]${NC} ${WHITE}Launch GUI Anytime:${NC}"
            echo -e "    ${GRAY}python -m gui.emyuel_gui${NC}"
            echo ""
            echo -e "${GRAY}    GUI Features:${NC}"
            echo -e "${GRAY}    • Visual scan configuration${NC}"
            echo -e "${GRAY}    • Real-time progress monitoring${NC}"
            echo -e "${GRAY}    • Interactive API key management${NC}"
            echo -e "${GRAY}    • Scan history browser${NC}"
            echo -e "${GRAY}    • AI-powered analysis${NC}"
            echo ""
            
            print_separator
            print_header "📚 HELPFUL RESOURCES"
            
            echo -e "${BCYAN}[→]${NC} ${WHITE}Documentation${NC}"
            echo -e "    ${GRAY}cat QUICKSTART.md${NC}"
            echo -e "    ${GRAY}cat DOKUMENTASI_PROGRAM.md${NC}"
            echo ""
            
            echo -e "${BCYAN}[→]${NC} ${WHITE}View Available Commands${NC}"
            echo -e "    ${GRAY}python -m cli.emyuel_cli --help${NC}"
            echo ""
            
            echo -e "${BCYAN}[→]${NC} ${WHITE}Check Dependencies${NC}"
            echo -e "    ${GRAY}python3 check_dependencies.py${NC}"
            echo ""
            
            print_separator
            echo ""
            echo -e "${BGREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BGREEN}║${NC}  ${WHITE}Ready to scan!${NC}  Happy hacking! 🛡️ 💻                                ${BGREEN}║${NC}"
            echo -e "${BGREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            ;;
        *)
            # Default to showing commands
            echo ""
            print_warning "Invalid option."
            echo ""
            print_success "Setup complete! You can:"
            echo -e "    ${GRAY}source venv/bin/activate${NC}"
            echo -e "    ${GRAY}python -m gui.emyuel_gui  ${BCYAN}# GUI mode${NC}"
            echo -e "    ${GRAY}python -m cli.emyuel_cli scan --target /path  ${BCYAN}# CLI mode${NC}"
            echo ""
            ;;
    esac
}

# Setup environment file (NO API KEY PROMPT - users configure later)
setup_env() {
    print_header "⚙️  ENVIRONMENT SETUP"
    
    # Just create basic .env if it doesn't exist
    if [ ! -f ".env" ]; then
        touch .env
        print_success "Created .env file"
    else
        print_success ".env file already exists"
    fi
    
    print_info "API keys can be configured later:"
    echo -e "    ${GRAY}• GUI: API Keys tab${NC}"
    echo -e "    ${GRAY}• CLI: python -m cli.emyuel_cli config${NC}"
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
    
    # Verify installation and capture exit code
    verify_installation
    VERIFY_EXIT_CODE=$?
    
    print_completion
    
    # Ask mode choice AT THE END (after everything installed)
    launch_app
}

# Run main installation
main
