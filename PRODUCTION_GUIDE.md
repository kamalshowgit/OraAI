# ORA AI Production Deployment Guide

## Quick Start

### Step 1: Deploy to Render
1. Push your code to GitHub
2. Create a new Web Service on Render
3. Set environment variables:
   - `GROQ_API_KEY=your_key_here` (optional, for AI features)
4. Deploy!

### Step 2: Test Upload Function

**Via cURL:**
```bash
# Create test file
echo "name,age,city
Alice,25,NYC
Bob,30,LA" > test.csv

# Upload to your Render app
curl -X POST \
  -F "file=@test.csv" \
  -F "table_name=my_data" \
  https://your-app.onrender.com/upload
```

**Expected Response:**
```json
{
  "message": "Dataset uploaded successfully",
  "rows": 2,
  "columns": ["name", "age", "city"],
  "table_name": "my_data",
  "tables": ["my_data"]
}
```

## Troubleshooting

### 1. Check Server Status
```bash
curl https://your-app.onrender.com/health
```

Should return:
```json
{
  "status": "ORA AI API is running",
  "database_exists": true,
  "tables": ["uploaded_table_names"],
  "active_table": "table_name"
}
```

### 2. Check Debug Information
```bash
curl https://your-app.onrender.com/debug
```

This shows:
- Data directory location
- Which directories exist
- Uploaded files
- Tables in database
- Any errors

**Example Output:**
```json
{
  "environment": "production",
  "data_root": "./data",
  "db_path": "./data/db/datasets.db",
  "upload_dir": "./data/uploads",
  "dirs_exist": {
    "data_root": true,
    "upload_dir": true,
    "db_dir": true,
    "db_file": true
  },
  "tables": ["users", "products"]
}
```

### 3. Upload Not Working?

**Check:**
1. File format is `.csv`, `.xlsx`, or `.txt`
2. File is not empty
3. Check Render logs: **Settings** → **Logs**
4. Run `/debug` endpoint to check directories

### 4. Tables Not Showing?

**Check:**
1. Upload succeeded (check response)
2. Run `/tables` endpoint: `curl https://your-app.onrender.com/tables`
3. Check `/debug` to see tables in database

### 5. Connection Not Working?

**Upload Database File (`.db`):**
```bash
curl -X POST \
  -F "file=@your_database.db" \
  https://your-app.onrender.com/connect/sqlite
```

Expected: Returns matching tables from the database

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check server status |
| `/debug` | GET | Get detailed debug info |
| `/upload` | POST | Upload CSV/Excel/TXT file |
| `/connect/sqlite` | POST | Connect existing SQLite database |
| `/tables` | GET | List all tables |
| `/schema` | GET | Get table schema |
| `/table` | GET | Preview table data |
| `/sql` | POST | Execute SQL query |
| `/download` | GET | Download table as CSV |

## Data Persistence

- ✅ **Local storage**: Data persists in `./data/` directory
- ✅ **Across restarts**: Data stays between server restarts
- ✅ **Per session**: Each user session uses the shared database

## Performance Notes

- Tables are stored in local SQLite database
- Works best with datasets under 100MB
- For larger datasets, consider external database

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Choose file" appears | This is just the file input. Select a file and click Upload |
| Upload fails silently | Check `/debug` endpoint to see error logs |
| Can't see uploaded data | Verify table name in `/tables` endpoint |
| SQL query returns no results | Check table schema with `/schema` endpoint |

## Contact & Support

If something doesn't work:
1. Check server logs on Render
2. Try `/debug` endpoint for diagnostics
3. Verify all environment variables are set
4. Check file format and size

---

**Status**: ✅ Production Ready
**Last Updated**: April 8, 2026
