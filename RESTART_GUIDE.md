# Quick Restart Guide

## After Applying Fixes

Follow these steps to restart the application with the fixes applied:

### Step 1: Stop Backend
In the backend terminal, press:
```
CTRL+C
```

### Step 2: Stop Frontend
In the frontend terminal, press:
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
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 4: Restart Frontend (in new terminal)
```bash
cd frontend
npm run dev
```

You should see:
```
> next dev
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### Step 5: Clear Browser Cache
Open browser console (F12) and run:
```javascript
localStorage.clear()
```

### Step 6: Refresh Page
Press `F5` or `CTRL+R`

### Step 7: Test Registration
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123
4. Click "Create Account"

You should be redirected to the dashboard.

---

## Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] No CORS errors in browser console
- [ ] Registration works
- [ ] Login works
- [ ] Can run backtest
- [ ] Can view profile
- [ ] Data persists after refresh

---

## If You Still Get Errors

### CORS Error Still Appears?
1. Make sure backend is fully started (wait 5 seconds)
2. Check backend terminal for errors
3. Try refreshing the page
4. Try in a different browser

### Password Error Still Appears?
1. Make sure you restarted the backend
2. Use a password shorter than 72 characters
3. Check that `backend/database/auth.py` has the fix

### Database Error?
1. Check PostgreSQL is running
2. Verify database exists
3. Check `backend/.env` has correct DATABASE_URL

---

## Ports Used

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432

Make sure these ports are not in use by other applications.

---

## Next Steps

Once everything is working:
1. Create an account
2. Run a backtest
3. View your profile
4. Check strategy history
5. View backtest history

Enjoy the new user system!
