# 🚀 Render Quick Deploy Checklist

## Pre-Deployment: Local Testing
- [ ] App runs locally: `uvicorn main:app --reload`
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Upload test file works
- [ ] All dependencies in `requirements.txt`

---

## Render Setup (5 minutes)

### 1. Push Your Repo
- [ ] Push your project to GitHub, GitLab, or Bitbucket

### 2. Create a Render Web Service
- [ ] Go to https://render.com
- [ ] Create a new Web Service
- [ ] Connect your repo and select the branch
- [ ] Choose **Python** environment

### 3. Set Build & Start Commands
- [ ] Build command:
```bash
pip install -r requirements.txt
```
- [ ] Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Add Environment Variables
- [ ] Add `GROQ_API_KEY=your_real_key_here`
- [ ] Optional: `ALLOWED_ORIGINS=https://your-app.onrender.com`

### 5. Deploy
- [ ] Click **Deploy**
- [ ] Wait for the service to build and start

---

## Post-Deployment: Verification

### Test Your App
- [ ] Visit your Render URL
- [ ] Test health endpoint: `https://your-app.onrender.com/health`
- [ ] Upload a file and verify preview works
- [ ] Run AI SQL queries with `GROQ_API_KEY` set

### Troubleshooting
- [ ] Check Render build logs for errors
- [ ] Verify `requirements.txt` installed successfully
- [ ] Confirm `main.py` exists in project root
- [ ] Confirm Start Command uses `uvicorn main:app`

---

## Done! 🎉

Your app is now online on Render.

---

## Optional Improvements

| Feature | Benefit |
|---------|---------|
| Custom domain | Makes app easier to share |
| TLS | Secure HTTPS traffic |
| External DB | Better persistence than local disk |

---

**Need help?** See `RENDER_DEPLOY.md` for detailed troubleshooting.
