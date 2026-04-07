# ORA AI - Render Deployment Guide

This guide walks through deploying the app to Render using the included `render.yaml` or manual service settings.

## 1. Push Your Repo

- Push your code to GitHub, GitLab, or Bitbucket.

## 2. Create a Render Web Service

1. Go to https://render.com
2. Sign in or sign up
3. Click **New +** → **Web Service**
4. Connect your repository
5. Select the branch you want to deploy

## 3. Choose Environment

- Select **Python** for the environment.
- Render will use `requirements.txt` to install dependencies.

## 4. Set Build & Start Commands

If Render does not auto-detect the commands, use:

- Build command:
  ```bash
  pip install -r requirements.txt
  ```
- Start command:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

## 5. Add Environment Variables

In your Render service settings, add:

- `GROQ_API_KEY=your_real_key_here`
- Optional: `ALLOWED_ORIGINS=https://your-app.onrender.com`
- Optional: `ORA_DATA_ROOT=/var/data/ora_ai` (for custom persistent storage location)

**Data Persistence Note**: The app automatically creates a `./data` directory for persistent storage on Render. Uploaded files and databases are stored there and will persist across restarts.

## 6. Deploy the Service

- Click **Create Web Service** or **Deploy**.
- Wait for the build and deploy process to finish.

## 7. Verify the App

- Visit the Render service URL.
- Confirm the health endpoint works:
  `https://your-app.onrender.com/health`
- Try uploading a file and running an AI SQL query.

## Notes

- Render uses the `$PORT` environment variable.
- **Data Persistence**: The app now uses a persistent `./data` directory (relative to app root) for Render deployments. Uploaded files and databases persist across restarts.
- Local development uses `/tmp/ora_ai_data` which is cleaned up automatically on shutdown.
- Session data (uploaded datasets, queries) are stored locally per instance. For multi-instance deployments, consider using external storage.

## Troubleshooting

- If the build fails, check the logs for dependency installation issues.
- Confirm `main.py` exists in the repo root.
- Confirm the start command uses `uvicorn main:app`.
- Make sure `GROQ_API_KEY` is set in Render environment variables.
