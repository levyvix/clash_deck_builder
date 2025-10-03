# Troubleshooting Guide

## Frontend Won't Start

### For Git Bash Users

**Option 1: Use the shell script**
```bash
./start-frontend.sh
```

**Option 2: Manual start**
```bash
cd frontend
npm start
```

### Common Issues

#### Issue 1: "Cannot find module" errors
**Solution**: Reinstall dependencies
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

#### Issue 2: Port 3000 already in use
**Solution**: Kill the process
```bash
# Find the process
netstat -ano | grep :3000

# Kill it (replace PID with actual process ID)
taskkill //PID <PID> //F

# Or use a different port
PORT=3001 npm start
```

#### Issue 3: "react-scripts: command not found"
**Solution**: Install react-scripts
```bash
cd frontend
npm install react-scripts --save
npm start
```

#### Issue 4: TypeScript errors
**Solution**: Check for compilation errors
```bash
cd frontend
npm run build
```
If build succeeds, try starting again.

#### Issue 5: Browser doesn't open
The .env file has `BROWSER=none` to prevent auto-opening.
**Solution**: Manually open http://localhost:3000 in your browser

---

## Backend Won't Start

### For Git Bash Users

**Option 1: Use the shell script**
```bash
./start-backend.sh
```

**Option 2: Manual start**
```bash
cd backend
uv run uvicorn src.main:app --reload
```

### Common Issues

#### Issue 1: "uv: command not found"
**Solution**: Install uv
```bash
# Using pip
pip install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Issue 2: Port 8000 already in use
**Solution**: Kill the process
```bash
# Find the process
netstat -ano | grep :8000

# Kill it
taskkill //PID <PID> //F
```

#### Issue 3: Database connection failed
**Solution**: Check MySQL is running
```bash
# Check if MySQL is running
net start | grep -i mysql

# Start MySQL if needed
net start MySQL80
```

#### Issue 4: Module not found errors
**Solution**: Install dependencies
```bash
cd backend
uv install
uv run uvicorn src.main:app --reload
```

---

## Quick Diagnostic

Run this to check your setup:

```bash
# Check Node.js
node --version  # Should be v16+

# Check npm
npm --version   # Should be 8+

# Check Python
python --version  # Should be 3.11+

# Check uv
uv --version    # Should be installed

# Check if ports are free
netstat -ano | grep -E ":(3000|8000)"
```

---

## Step-by-Step Startup (Git Bash)

### Terminal 1 - Backend
```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for:
```
INFO:     Application startup complete.
```

Test: Open http://localhost:8000/health in browser

### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

Wait for:
```
Compiled successfully!
```

Open: http://localhost:3000 in browser

---

## Still Not Working?

### Check Frontend Logs
When you run `npm start`, look for:
- ✅ "Compiled successfully!" - Good!
- ❌ "Failed to compile" - Check the error message
- ❌ "Port 3000 is already in use" - Kill the process
- ❌ "Module not found" - Run `npm install`

### Check Backend Logs
When you run uvicorn, look for:
- ✅ "Application startup complete" - Good!
- ❌ "Address already in use" - Port 8000 is taken
- ❌ "ModuleNotFoundError" - Run `uv install`
- ❌ "Database connection failed" - Check MySQL

### Check Browser Console
Open DevTools (F12) and check Console tab:
- ❌ "Failed to fetch" - Backend not running
- ❌ "CORS error" - Backend CORS misconfigured
- ❌ "404 Not Found" - Wrong API URL in .env

---

## Manual Verification

### 1. Check Backend is Running
```bash
curl http://localhost:8000/health
```
Should return JSON with status "healthy"

### 2. Check Frontend is Running
```bash
curl http://localhost:3000
```
Should return HTML

### 3. Check API Connection
Open browser to http://localhost:3000
Open DevTools (F12) → Network tab
Refresh page
Look for request to http://localhost:8000/cards
Should return 200 OK

---

## Environment Variables

### Frontend (.env)
```bash
cd frontend
cat .env
```

Should contain:
```
REACT_APP_API_BASE_URL=http://localhost:8000
PORT=3000
BROWSER=none
```

### Backend
Check `backend/src/utils/config.py` for database settings

---

## Clean Restart

If nothing works, try a clean restart:

```bash
# Stop all servers (Ctrl+C in both terminals)

# Clean frontend
cd frontend
rm -rf node_modules package-lock.json build
npm install

# Clean backend
cd ../backend
rm -rf .venv
uv install

# Start backend
uv run uvicorn src.main:app --reload

# In new terminal, start frontend
cd frontend
npm start
```

---

## Get Help

If you're still stuck, provide:
1. The exact error message you see
2. Output of `node --version` and `npm --version`
3. Output of `python --version` and `uv --version`
4. Whether backend starts successfully
5. Whether frontend builds successfully (`npm run build`)

---

## Quick Test

Run this one-liner to test everything:
```bash
cd backend && uv run python -c "from src.main import app; print('Backend OK')" && cd ../frontend && npm run build && echo "Frontend OK"
```

If both print "OK", your setup is good!
