# ORA AI - PythonAnywhere Deployment Guide

## Step-by-Step Deployment Instructions

### Step 1: Create a PythonAnywhere Account
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a **FREE** account
3. Verify your email

### Step 2: Clone Your Repository
In PythonAnywhere **Bash console**:

```bash
cd /home/YOUR_USERNAME
git clone https://github.com/YOUR_USERNAME/ORA-AI.git
cd ORA-AI
```

### Step 3: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 oraai
pip install -r requirements.txt
```

### Step 4: Configure Your Web App

1. Go to **"Web"** → **"Add a new web app"**
2. Choose **"Manual configuration"**
3. Select **Python 3.10**
4. Click **"Next"**

### Step 5: Update WSGI Configuration

1. In the Web tab, you'll see a WSGI configuration file path. Click it.
2. Replace the entire content with:

```python
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
username = os.getenv('USER')
project_dir = f'/home/{username}/ORA-AI'
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = f'/home/{username}/.virtualenvs/oraai/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

# Import FastAPI app
from main import app
application = app
```

3. Click **"Save"**

### Step 6: Update Web App Settings

In the **Web** tab:

**Virtualenv:**
- Set to: `/home/YOUR_USERNAME/.virtualenvs/oraai`

**Source code:**
- Set to: `/home/YOUR_USERNAME/ORA-AI`

**WSGI configuration file:**
- Should automatically be set

### Step 7: Configure Static Files (if needed)

1. In **Web** tab, scroll to "Static files"
2. Add (optional, for static assets):
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/ORA-AI/static/`

### Step 8: Add Environment Variables

1. Go to **Web** → **"Add a new web app"**
2. Scroll down to find the config section
3. Or edit your `.env` file:

```bash
# In bash console
cd /home/YOUR_USERNAME/ORA-AI
nano .env
```

Add:
```
GROQ_API_KEY=your_actual_key_here
ALLOWED_ORIGINS=https://your-domain.pythonanywhere.com,http://localhost:8000
```

Save with `Ctrl+X` then `Y`

### Step 9: Reload Your Web App

1. Go to **Web** tab
2. Click the green **"Reload YOUR_DOMAIN.pythonanywhere.com"** button
3. Wait 10-20 seconds for reload to complete

### Step 10: Test Your Deployment

1. Visit: `https://YOUR_USERNAME.pythonanywhere.com`
2. Test the `/health` endpoint: `https://YOUR_USERNAME.pythonanywhere.com/health`
3. Upload a test file and verify it works

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:**
- Ensure virtual environment is activated
- Check all packages are installed: `pip list`
- Verify sys.path includes project directory

### Issue: 500 Error
**Solution:**
- Check error log: **Web** → **"Error log"**
- Verify `.env` file exists with GROQ_API_KEY
- Restart the app: Click **"Reload..."** button

### Issue: 404 on Frontend
**Solution:**
- Verify static files path is correct
- Check that `frontend.html` and `index.html` exist
- Test: `curl https://YOUR_USERNAME.pythonanywhere.com/app`

### Issue: "No module named 'main'"
**Solution:**
- Verify project directory is correct
- Ensure `main.py` is in the root directory
- Check sys.path in WSGI file

### Issue: Database Issues
**Solution:**
- PythonAnywhere creates temp dirs in `/tmp`
- Your app uses `/tmp/ora_ai_data` (auto-cleanup on restart)
- For persistence, upgrade to paid tier OR use PostgreSQL

---

## PythonAnywhere Free Tier Limitations

| Feature | Free | Paid |
|---------|------|------|
| Web apps | 1 | Unlimited |
| CPU time | Limited | Unlimited |
| Storage | 512 MB | Unlimited |
| Database | SQLite (temp) | PostgreSQL included |
| HTTPS | Yes | Yes |
| Custom domain | No | Yes |
| Scheduled tasks | No | Yes |

---

## Persistence & Database

Your current app uses **temporary** `/tmp/ora_ai_data` which resets on restart.

### Option 1: Live with Temporary Storage (Current)
- Data resets every app restart
- Fine for demos/testing
- No cost

### Option 2: Use PythonAnywhere Disk
- Consider upgrading to paid tier
- Adds persistent `/var/www` storage
- ~$5-7/month

### Option 3: Add PostgreSQL
- Switch from SQLite to PostgreSQL
- Free tier: Included with paid PythonAnywhere
- Requires code changes to `db_config.py`

---

## File Structure

Your PythonAnywhere directory should look like:

```
/home/YOUR_USERNAME/ORA-AI/
├── main.py
├── app.py
├── wsgi.py (NEW - for PythonAnywhere)
├── frontend.html
├── index.html
├── requirements.txt
├── .env
├── agent/
├── ingestion/
├── static/
└── templates/
```

---

## Useful Commands

```bash
# SSH into PythonAnywhere console
ssh YOUR_USERNAME@ssh.pythonanywhere.com

# Activate virtualenv
cd /home/YOUR_USERNAME
source .virtualenvs/oraai/bin/activate

# Reinstall dependencies
pip install --upgrade -r /home/YOUR_USERNAME/ORA-AI/requirements.txt

# Check logs
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com/access.log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com/error.log

# Test app locally
python /home/YOUR_USERNAME/ORA-AI/main.py
```

---

## Next Steps

1. **Verify deployment works**: Visit your URL and test features
2. **Get custom domain**: Upgrade to paid tier
3. **Add persistent storage**: Upgrade to store data permanently
4. **Enable HTTPS**: Already included on PythonAnywhere
5. **Monitor logs**: Check Web tab → Error log regularly

---

## Troubleshooting Help

If you encounter issues:

1. Check **Web** tab → **"Error log"** for specific errors
2. Review this guide's "Common Issues" section
3. Run: `pip install -r requirements.txt` again
4. Click **"Reload blue button"** to restart app

---

**Your app is now live on PythonAnywhere! 🚀**
