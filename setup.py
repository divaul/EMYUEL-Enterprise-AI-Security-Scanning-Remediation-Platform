#!/usr/bin/env python3
"""
Quick setup script for EMYUEL platform
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_requirements():
    """Check if Docker is installed"""
    print_header("Checking Requirements")
    
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Docker installed: {result.stdout.strip()}")
    except FileNotFoundError:
        print("✗ Docker not found. Please install Docker Desktop.")
        print("  Download: https://www.docker.com/products/docker-desktop/")
        sys.exit(1)
    
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Docker Compose installed: {result.stdout.strip()}")
    except FileNotFoundError:
        print("✗ Docker Compose not found.")
        sys.exit(1)


def setup_env_file():
    """Create .env file from template"""
    print_header("Setting up Environment Variables")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        overwrite = input(".env file already exists. Overwrite? (y/N): ")
        if overwrite.lower() != 'y':
            print("Skipping .env setup")
            return
    
    if not env_example.exists():
        print("✗ .env.example not found")
        sys.exit(1)
    
    # Read template
    with open(env_example) as f:
        content = f.read()
    
    # Generate secure secrets
    jwt_secret = secrets.token_urlsafe(32)
    postgres_password = secrets.token_urlsafe(16)
    redis_password = secrets.token_urlsafe(16)
    encryption_key = secrets.token_urlsafe(24)
    
    # Replace placeholders
    content = content.replace(
        "JWT_SECRET_KEY=change-this-to-a-very-long-random-secret-key",
        f"JWT_SECRET_KEY={jwt_secret}"
    )
    content = content.replace(
        "POSTGRES_PASSWORD=changeme",
        f"POSTGRES_PASSWORD={postgres_password}"
    )
    content = content.replace(
        "REDIS_PASSWORD=changeme",
        f"REDIS_PASSWORD={redis_password}"
    )
    content = content.replace(
        "ENCRYPTION_KEY=change-this-to-32-byte-key-___",
        f"ENCRYPTION_KEY={encryption_key}"
    )
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✓ Created .env file with secure random secrets")
    print("\n⚠️  IMPORTANT: Add your LLM API key to .env file!")
    print("   Choose ONE provider:")
    print("   - OPENAI_API_KEY=sk-...")
    print("   - GOOGLE_AI_API_KEY=...")
    print("   - ANTHROPIC_API_KEY=sk-ant-...")


def start_services():
    """Start Docker services"""
    print_header("Starting Services")
    
    # Check if .env has API key
    with open(".env") as f:
        env_content = f.read()
    
    has_api_key = (
        "OPENAI_API_KEY=sk-" in env_content or
        "GOOGLE_AI_API_KEY=" in env_content and "your-" not in env_content or
        "ANTHROPIC_API_KEY=sk-ant-" in env_content
    )
    
    if not has_api_key:
        print("⚠️  Warning: No LLM API key found in .env")
        proceed = input("Continue anyway? (y/N): ")
        if proceed.lower() != 'y':
            print("\nPlease add an API key to .env and run:")
            print("  docker-compose up -d")
            return
    
    print("Starting Docker Compose services...")
    subprocess.run(["docker-compose", "up", "-d"])
    
    print("\n✓ Services started!")
    print_urls()


def print_urls():
    """Print access URLs"""
    print_header("Access URLs")
    print("API Documentation:  http://localhost:8000/api/docs")
    print("Frontend Dashboard: http://localhost:8080")
    print("Grafana:            http://localhost:3000")
    print("Prometheus:         http://localhost:9090")
    print("\nDefault Login:")
    print("  Email:    admin@emyuel.local")
    print("  Password: admin123")
    print("\n⚠️  CHANGE DEFAULT PASSWORD IMMEDIATELY!")


def main():
    """Main setup function"""
    print("""
    ███████╗███╗   ███╗██╗   ██╗██╗   ██╗███████╗██╗     
    ██╔════╝████╗ ████║╚██╗ ██╔╝██║   ██║██╔════╝██║     
    █████╗  ██╔████╔██║ ╚████╔╝ ██║   ██║█████╗  ██║     
    ██╔══╝  ██║╚██╔╝██║  ╚██╔╝  ██║   ██║██╔══╝  ██║     
    ███████╗██║ ╚═╝ ██║   ██║   ╚██████╔╝███████╗███████╗
    ╚══════╝╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚══════╝
    
    Security Scanning & Remediation Platform
    """)
    
    check_requirements()
    setup_env_file()
    
    start = input("\nStart services now? (Y/n): ")
    if start.lower() != 'n':
        start_services()
    else:
        print("\nTo start services later, run:")
        print("  docker-compose up -d")
        print_urls()


if __name__ == "__main__":
    main()
