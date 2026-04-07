#!/usr/bin/env python3
"""
Render Deployment Helper
This script helps verify the app is ready for deployment to Render.
"""

import os
import sys
from pathlib import Path


def check_requirements():
    """Check if all required packages are installed."""
    print("✓ Checking requirements.txt...")
    
    try:
        import fastapi
        import pandas
        import sqlalchemy
        import groq
        from dotenv import load_dotenv
        
        print("  ✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"  ⚠ Missing package: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def check_files():
    """Check if essential files exist."""
    print("✓ Checking essential files...")
    required_files = [
        "main.py",
        "requirements.txt",
        "frontend.html",
        "index.html",
        "render.yaml"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist


def check_env():
    """Check if .env file has required variables if present."""
    print("✓ Checking environment variables...")
    env_path = Path(".env")
    if not env_path.exists():
        print("  ⚠ .env not found. Make sure GROQ_API_KEY is set in Render environment variables.")
        return True
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ["GROQ_API_KEY"]
        missing = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or "placeholder" in value.lower():
                missing.append(var)
                print(f"  ⚠ {var}: Not set or is placeholder")
            else:
                print(f"  ✓ {var}: Set")
        
        return len(missing) == 0
    except Exception as e:
        print(f"  ✗ Error checking .env: {e}")
        return False


def check_main_py():
    """Check if main.py has required imports and setup."""
    print("✓ Checking main.py...")
    try:
        with open("main.py") as f:
            content = f.read()
        
        checks = [
            ("FastAPI import", "from fastapi import FastAPI"),
            ("Lifespan handler", "@asynccontextmanager"),
            ("CORS middleware", "CORSMiddleware"),
            ("Health endpoint", "@app.get(\"/health\")"),
        ]
        
        all_good = True
        for check_name, check_str in checks:
            if check_str in content:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name}: Missing")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"  ✗ Error checking main.py: {e}")
        return False


def check_render_yaml():
    """Check if render.yaml exists and contains a valid start command."""
    print("✓ Checking render.yaml...")
    if not Path("render.yaml").exists():
        print("  ✗ render.yaml not found")
        return False
    
    try:
        with open("render.yaml") as f:
            content = f.read()
        
        if "uvicorn main:app --host 0.0.0.0 --port $PORT" in content:
            print("  ✓ startCommand uses uvicorn main:app")
            return True
        print("  ⚠ render.yaml found but start command is not the expected uvicorn command")
        return False
    except Exception as e:
        print(f"  ✗ Error checking render.yaml: {e}")
        return False


def print_deployment_guide():
    """Print quick deployment guide."""
    print("\n" + "="*60)
    print("📋 Render Deployment Guide")
    print("="*60)
    print("""
1. PUSH YOUR REPO
   - Push your code to GitHub, GitLab, or Bitbucket.

2. CREATE A RENDER WEB SERVICE
   - Visit https://render.com
   - Create a new Web Service
   - Connect your repo and select the branch
   - Choose Python environment

3. SET BUILD & START COMMANDS
   - Build command: pip install -r requirements.txt
   - Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

4. ADD ENVIRONMENT VARIABLES
   - GROQ_API_KEY=your_real_key_here
   - Optional: ALLOWED_ORIGINS=https://your-app.onrender.com

5. DEPLOY
   - Click Deploy
   - Wait for the service to build and start

6. VERIFY
   - Visit your Render service URL
   - Check: <your-service-url>/health
""")


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("🚀 ORA AI - Render Deployment Preflight")
    print("="*60 + "\n")
    
    results = {
        "Requirements": check_requirements(),
        "Files": check_files(),
        "Environment (.env or Render vars)": check_env(),
        "main.py": check_main_py(),
        "render.yaml": check_render_yaml(),
    }
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check}: {status}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print(f"\n✓ All checks passed! Ready for Render deployment.\n")
    else:
        print(f"\n⚠ Some checks failed. Fix issues above if needed.\n")
    
    print_deployment_guide()
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
