#!/usr/bin/env python3
"""
PythonAnywhere Deployment Helper
This script helps verify and prepare your app for PythonAnywhere deployment.
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    print("✓ Checking requirements.txt...")
    
    try:
        # Try to import critical packages directly
        import fastapi
        import pandas
        import sqlalchemy
        import groq
        from dotenv import load_dotenv
        
        print("  ✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"  ⚠ Missing package: {e}")
        print(f"  Run: pip install -r requirements.txt")
        return False

def check_files():
    """Check if essential files exist."""
    print("✓ Checking essential files...")
    required_files = [
        "main.py",
        "wsgi.py",
        "requirements.txt",
        "frontend.html",
        "index.html",
        ".env"
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
    """Check if .env file has required variables."""
    print("✓ Checking .env file...")
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
            ("Static files", "response_class=HTMLResponse"),
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

def check_wsgi():
    """Check if wsgi.py exists and is correct."""
    print("✓ Checking wsgi.py...")
    if not Path("wsgi.py").exists():
        print("  ✗ wsgi.py not found")
        return False
    
    try:
        with open("wsgi.py") as f:
            content = f.read()
        
        required = [
            "from main import app",
            "application = app"
        ]
        
        all_good = True
        for check_str in required:
            if check_str in content:
                print(f"  ✓ Contains: {check_str}")
            else:
                print(f"  ✗ Missing: {check_str}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"  ✗ Error checking wsgi.py: {e}")
        return False

def print_deployment_guide():
    """Print quick deployment guide."""
    print("\n" + "="*60)
    print("📋 PYTHONANYWHERE DEPLOYMENT GUIDE")
    print("="*60)
    print("""
1. CREATE ACCOUNT
   - Sign up at https://www.pythonanywhere.com (FREE)
   - Verify your email

2. CLONE REPOSITORY
   - Open Bash console
   - cd /home/YOUR_USERNAME
   - git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   - cd YOUR_REPO

3. CREATE VIRTUALENV
   - mkvirtualenv --python=/usr/bin/python3.10 oraai
   - pip install -r requirements.txt

4. ADD WEB APP
   - Click "Web" → "Add new web app"
   - Choose "Manual configuration"
   - Select "Python 3.10"

5. UPDATE WSGI FILE
   - Click WSGI configuration file link
   - Replace content with wsgi.py from your project
   - Replace YOUR_USERNAME with actual username

6. SET VIRTUALENV & SOURCE CODE
   - Virtualenv: /home/YOUR_USERNAME/.virtualenvs/oraai
   - Source code: /home/YOUR_USERNAME/YOUR_REPO

7. ADD ENVIRONMENT VARIABLES
   - nano /home/YOUR_USERNAME/YOUR_REPO/.env
   - Add: GROQ_API_KEY=your_real_key
   - Add: ALLOWED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com
   - Save: Ctrl+X → Y → Enter

8. RELOAD APP
   - Click green "Reload" button in Web tab
   - Wait 10-20 seconds

9. TEST
   - Visit: https://YOUR_USERNAME.pythonanywhere.com
   - Check: https://YOUR_USERNAME.pythonanywhere.com/health

✓ DONE! Your app is live!
""")

def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("🚀 ORA AI - PythonAnywhere Pre-Deployment Check")
    print("="*60 + "\n")
    
    results = {
        "Requirements": check_requirements(),
        "Files": check_files(),
        "Environment (.env)": check_env(),
        "main.py": check_main_py(),
        "wsgi.py": check_wsgi(),
    }
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check}: {status}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print(f"\n✓ All checks passed! Ready for deployment.\n")
    else:
        print(f"\n⚠ Some checks failed. Fix issues above if needed.\n")
    
    print_deployment_guide()
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
