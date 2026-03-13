# Restart Guide After Database Fix

## What Was Fixed
✅ Database schema recreated with all required columns
✅ `return_percent` column now exists in backtests table
✅ All tables created correctly

## How to Restart

### Step 1: Stop Backend
In backend terminal:
```
CTRL+C
```

### Step 2: Stop Frontend
In frontend terminal:
```
CTRL+C
```

### Step 3: Restart Backend
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Restart Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
```

### Step 5: Clear Browser Cache
In browser console (F12):
```javascript
localStorage.clear()
```

### Step 6: Refresh Page
Press `F5`

---

## Testing

### Test 1: Sign Up
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Create account
4. ✅ Should work without errors

### Test 2: View Profile
1. Click profile icon
2. Click "Profile"
3. ✅ Should show user details and statistics

### Test 3: Run Backtest
1. Enter strategy
2. Click "Run Backtest"
3. ✅ Should complete successfully
4. ✅ Results saved to database

---

## Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] No database errors
- [ ] Can sign up
- [ ] Can view profile
- [ ] Can run backtest
- [ ] Profile shows statistics
- [ ] No errors in console

---

## If You Still Get Errors

### Database Error
1. Check PostgreSQL is running
2. Run: `python verify_db.py` in backend folder
3. Check all tables exist

### Profile Page Error
1. Make sure you're logged in
2. Check browser console for errors
3. Check backend logs

### Backtest Error
1. Check you're logged in
2. Check backend logs
3. Try simpler strategy

---

**Status**: ✅ **READY TO USE**

Just restart and test!
