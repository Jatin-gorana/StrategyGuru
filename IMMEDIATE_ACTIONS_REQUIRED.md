# Immediate Actions Required

## Critical Issue Fixed ✅
The frontend runtime error "Cannot read properties of undefined (reading 'toFixed')" has been fixed in all components.

## Remaining Issue ⚠️
The database is missing the `return_percent` column, which causes errors when fetching profile data.

## What You Need to Do

### Step 1: Check Database Status
```bash
cd backend
python check_database_status.py
```

This will show you:
- Database connection status
- All tables and their columns
- Whether `return_percent` column exists
- Row counts in each table

### Step 2: Fix the Database

**Option A: Quick Fix (Recommended if you have data)**
```bash
python fix_database.py
```
This adds the missing column without deleting data.

**Option B: Full Rebuild (Recommended if you want a clean start)**
```bash
python recreate_db.py
```
This deletes all data and creates a fresh database with correct schema.

### Step 3: Restart Backend
After running the fix script, restart your backend server.

### Step 4: Test
1. Sign up / Sign in
2. Run a backtest
3. Check the dashboard
4. View your profile page

## Files Created/Modified

### Frontend (Fixed - No Action Needed)
- ✅ `frontend/components/TradesTable.tsx` - Fixed undefined pnl error
- ✅ `frontend/components/TradesTableEnhanced.tsx` - Fixed undefined pnl error
- ✅ `frontend/components/PerformanceChart.tsx` - Fixed undefined pnl error
- ✅ `frontend/app/dashboard/page.tsx` - Fixed undefined pnl error

### Backend (New Scripts - Ready to Use)
- 🆕 `backend/fix_database.py` - Quick fix script
- 🆕 `backend/check_database_status.py` - Status checker
- 🆕 `backend/alembic/versions/001_add_return_percent_column.py` - Migration file

### Documentation
- 📄 `DATABASE_FIX_GUIDE.md` - Detailed guide
- 📄 `FIXES_APPLIED_TODAY.md` - Summary of all fixes
- 📄 `IMMEDIATE_ACTIONS_REQUIRED.md` - This file

## Expected Outcome

After completing these steps:
1. ✅ No more "Cannot read properties of undefined" errors
2. ✅ Profile page loads correctly
3. ✅ Backtest results display properly
4. ✅ All trade data shows correctly in tables

## Troubleshooting

If you still see errors after running the fix:

1. **Check the fix script output** - Did it say "Added return_percent column successfully"?
2. **Restart the backend** - Make sure you restarted after running the fix
3. **Check backend logs** - Look for any SQL errors
4. **Try the full rebuild** - Run `recreate_db.py` if the quick fix didn't work

## Questions?

Refer to `DATABASE_FIX_GUIDE.md` for more detailed information about each option.
