# 🚀 PythonAnywhere Quick Deploy Checklist

## Pre-Deployment: Local Testing
- [ ] App runs locally: `uvicorn main:app --reload`
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Upload test file works
- [ ] All dependencies in requirements.txt

---

## PythonAnywhere Setup (5 minutes)

### 1. Account & Repository
- [ ] Create free account at https://www.pythonanywhere.com
- [ ] Verify email
- [ ] Go to **Bash console**
- [ ] Clone your repository: 
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Virtual Environment
- [ ] Create virtualenv:
```bash
mkvirtualenv --python=/usr/bin/python3.10 oraai
```
- [ ] Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Web App Configuration
- [ ] Go to **Web** tab
- [ ] Click **"Add a new web app"**
- [ ] Select **"Manual configuration"**
- [ ] Choose **"Python 3.10"**
- [ ] Click through to finish

### 4. WSGI Configuration
- [ ] In **Web** tab, click **WSGI configuration file** link
- [ ] Copy entire content from [wsgi.py](wsgi.py)
- [ ] Paste into PythonAnywhere editor
- [ ] **Replace** `YOUR_USERNAME` with your actual username
- [ ] Save (Ctrl+S)

### 5. Virtualenv Setup
- [ ] In **Web** tab, set **Virtualenv** field:
```
/home/YOUR_USERNAME/.virtualenvs/oraai
```
- [ ] Set **Source code** field:
```
/home/YOUR_USERNAME/YOUR_REPO
```

### 6. Environment Variables
- [ ] In **Bash console**, edit `.env`:
```bash
nano /home/YOUR_USERNAME/YOUR_REPO/.env
```
- [ ] Add/update:
```
GROQ_API_KEY=your_real_key_here
ALLOWED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com
```
- [ ] Save: `Ctrl+X` → `Y` → `Enter`

### 7. Reload App
- [ ] Go back to **Web** tab
- [ ] Click green **"Reload YOUR_USERNAME.pythonanywhere.com"** button
- [ ] Wait 10-20 seconds

---

## Post-Deployment: Verification

### Test Your App
- [ ] Visit: `https://YOUR_USERNAME.pythonanywhere.com`
- [ ] Test health: `https://YOUR_USERNAME.pythonanywhere.com/health`
- [ ] Test upload: Use Web UI to upload a file
- [ ] Check error log if issues: **Web** → **Error log**

### Troubleshooting
- [ ] See 500 error? Check **Error log**
- [ ] Module not found? Reinstall: `pip install -r requirements.txt`
- [ ] Still issues? Check WSGI file configuration
- [ ] Click reload button again

---

## Done! 🎉

Your app is now online at:
```
https://YOUR_USERNAME.pythonanywhere.com
```

---

## Optional Upgrades

| Feature | Cost | Benefit |
|---------|------|---------|
| Persistent storage | $5/mo | Data survives restarts |
| Custom domain | $5/mo | Use your own domain |
| PostgreSQL | Included | Better than SQLite |
| Scheduled tasks | $5/mo | Auto backups, etc |

---

**Need help?** See [PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md) for detailed troubleshooting.
