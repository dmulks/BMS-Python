# Quick Start Guide

## 🚀 Get the Bond Management System Running in 3 Steps

### Step 1: Start the Backend

Open a terminal and run:

```bash
cd /Users/dariusmulenga/BMS-Python/backend
./start_server.sh
```

**Or manually:**

```bash
cd /Users/dariusmulenga/BMS-Python/backend
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dateutil pandas python-multipart
python scripts/migrate_add_bond_issues.py --auto
uvicorn app.main:app --reload
```

The backend will be available at: **http://localhost:8000**
API Docs: **http://localhost:8000/api/docs**

---

### Step 2: Start the Frontend

Open a **NEW** terminal and run:

```bash
cd /Users/dariusmulenga/BMS-Python/frontend
npm install   # Only needed once
npm run dev
```

The frontend will be available at: **http://localhost:5173** (or the port shown in terminal)

---

### Step 3: Access the Dashboard

1. Open your browser to: **http://localhost:5173**
2. Log in with your credentials
3. You should see the dashboard!

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error: ModuleNotFoundError**
```bash
cd /Users/dariusmulenga/BMS-Python/backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error: Database connection failed**
- Make sure PostgreSQL is running
- Check database credentials in `app/core/config.py`

**Error: Import errors**
```bash
# Reinstall dependencies
pip install --upgrade fastapi uvicorn sqlalchemy psycopg2-binary
```

### Frontend Won't Start

**Error: Command not found: npm**
- Install Node.js from https://nodejs.org/

**Error: Dependencies not found**
```bash
cd /Users/dariusmulenga/BMS-Python/frontend
rm -rf node_modules package-lock.json
npm install
```

### Dashboard Shows Errors

**Error: 401 Unauthorized**
- You need to log in first at `/login`

**Error: Failed to fetch dashboard data**
- Make sure backend is running at http://localhost:8000
- Check browser console (F12) for detailed errors
- Verify API endpoint: http://localhost:8000/api/v1/dashboard

**Error: Network Error / CORS**
- Backend and frontend must both be running
- Check CORS settings in `backend/app/main.py`

---

## 📊 Verify Everything is Working

### Test Backend API

Open in browser or use curl:
```bash
# Health check
curl http://localhost:8000/api/health

# Dashboard (requires auth token)
curl http://localhost:8000/api/v1/dashboard -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Frontend

1. Go to http://localhost:5173
2. You should see the login page
3. After login, you should see the dashboard with:
   - Bond Issues count
   - Total Face Value
   - Total Members
   - Active Purchases

---

## 🎯 What's Next?

Once the dashboard loads successfully:

1. **Import Bond Holdings**
   ```bash
   cd /Users/dariusmulenga/BMS-Python/backend
   source venv/bin/activate
   python scripts/import_bond_holdings.py "path/to/excel.xlsx"
   ```

2. **Create Payment Events**
   - Navigate to a bond detail page
   - Click "Create Event"
   - Fill in event details

3. **Preview & Generate Payments**
   - Click "Preview/Generate" on an event
   - Review calculations
   - Click "Generate & Save Payments"

4. **View Audit Reports**
   - Navigate to `/admin/audit`
   - Upload BOZ statement CSV
   - Review discrepancies

---

## 📝 Common Commands

**Backend:**
```bash
# Start server
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Run migration
python scripts/migrate_add_bond_issues.py

# Import Excel
python scripts/import_bond_holdings.py "file.xlsx"
```

**Frontend:**
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🆘 Still Having Issues?

1. **Check the logs:**
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)

2. **Verify ports:**
   - Backend should be on 8000
   - Frontend should be on 5173 (or shown in terminal)

3. **Check database:**
   ```bash
   # Connect to PostgreSQL
   psql -U your_username -d bond_db

   # Check if new tables exist
   \dt
   # You should see: bond_issues, member_bond_holdings, payment_events, member_payments
   ```

4. **Review configuration:**
   - Backend: `backend/app/core/config.py`
   - Frontend: `frontend/src/api/client.js`

---

## ✅ Success Indicators

You know everything is working when:

- ✅ Backend shows: "Application startup complete"
- ✅ Frontend shows: "Local: http://localhost:5173"
- ✅ Browser shows the login page
- ✅ After login, dashboard displays KPIs
- ✅ No console errors in browser (F12)
- ✅ API docs accessible at http://localhost:8000/api/docs

---

**Need more help?** See `INTEGRATION_GUIDE.md` for detailed documentation.