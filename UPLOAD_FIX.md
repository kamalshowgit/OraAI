# Upload Function Fix - Production Deployment

## Problem
The dataset upload function was failing on production servers (Render, Railway, Heroku, etc.) because:

1. **Ephemeral `/tmp` directory**: Production environments automatically clean up `/tmp`, causing data loss
2. **Automatic cleanup on startup**: The code was deleting the data directory on every restart
3. **Write permission issues**: `/tmp` might not have proper write permissions in containerized environments

## Solution
Updated the data storage logic to:

1. **Detect production environment**: Automatically identify Render, Railway, or Heroku deployments
2. **Use persistent storage on production**: 
   - Default: `./data/` directory (relative to app root)
   - Custom: Set `ORA_DATA_ROOT` environment variable
3. **Use ephemeral storage on local**: Still uses `/tmp/ora_ai_data` for development with cleanup on shutdown
4. **Ensure directory creation**: All required directories (db, uploads, exports) are created automatically

## Changes Made

### 1. `ingestion/db_config.py`
```python
# Production: Use app-relative persistent directory
# Local development: Use /tmp with cleanup
IS_PRODUCTION = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HEROKU_APP_NAME")

if IS_PRODUCTION:
    DATA_ROOT = Path(os.getenv("ORA_DATA_ROOT", "./data"))
else:
    # Cleanup /tmp on local, use it for temporary storage
    TEMP_DIR = Path("/tmp/ora_ai_data")
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    DATA_ROOT = TEMP_DIR
```

### 2. `main.py`
```python
# Only cleanup /tmp on local development, not in production
is_production = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HEROKU_APP_NAME")
if not is_production:
    shutil.rmtree("/tmp/ora_ai_data", ignore_errors=True)
```

## For Your Render Deployment

### Option 1: Use Default Persistent Directory (Recommended)
No configuration needed! The app will automatically use `./data/` directory which persists in Render.

### Option 2: Use Custom Data Directory
Set environment variable in Render dashboard:
```
ORA_DATA_ROOT=/var/data/ora_ai
```

Or for app-relative path:
```
ORA_DATA_ROOT=./persistent_data
```

## Testing Locally

```bash
# Start the server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# Upload a file
curl -X POST -F "file=@test.csv" -F "table_name=my_table" http://localhost:8000/upload

# Verify data persists
curl http://localhost:8000/tables
```

## Production Testing

1. Push code to your Git repository
2. Render will automatically detect changes and redeploy
3. Test upload via the web interface or cURL
4. Verify data persists across requests and restarts

## Troubleshooting

### "Permission denied" error
- Ensure the app has write permissions to the data directory
- Check Render service logs for detailed error messages

### Upload still fails
1. Check Render service logs: **Settings** → **Logs**
2. Look for errors in the "Error Logs" tab
3. Verify `ORA_DATA_ROOT` environment variable if using custom path

### Data lost after restart
- Verify the `data/` directory exists in your repo or uses a persistent path
- Check that the data directory path is not in an ephemeral location like `/tmp`

## Files Modified
- `ingestion/db_config.py` - Fixed path detection and directory creation
- `main.py` - Fixed cleanup logic for production safety
