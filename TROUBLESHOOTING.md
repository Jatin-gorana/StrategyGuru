# Troubleshooting Guide

## Common Issues and Solutions

### Database Connection Issues

#### Error: "could not connect to server: Connection refused"
**Cause**: PostgreSQL is not running

**Solution**:
- Windows: Start PostgreSQL from Services or pgAdmin
- macOS: `brew services start postgresql@15`
- Linux: `sudo systemctl start postgresql`

#### Error: "FATAL: database does not exist"
**Cause**: Database wasn't created

**Solution**:
```bash
psql -U postgres
CREATE DATABASE trading_backtester;
\q
```

#### Error: "FATAL: password authentication failed"
**Cause**: Wrong password in DATABASE_URL

**Solution**:
1. Verify PostgreSQL password
2. Update `backend/.env` with correct password
3. Restart backend

#### Error: "asyncpg.exceptions.CannotConnectNowError"
**Cause**: Connection pool exhausted or database unreachable

**Solution**:
1. Check PostgreSQL is running
2. Verify DATABASE_URL
3. Restart backend
4. Check firewall settings

### Authentication Issues

#### Error: "Invalid authentication credentials"
**Cause**: JWT token expired or invalid

**Solution**:
1. Clear localStorage: `localStorage.clear()` in browser console
2. Login again
3. Check SECRET_KEY in `backend/.env`

#### Error: "Email already registered"
**Cause**: Email already exists in database

**Solution**:
1. Use different email
2. Or login with existing email
3. To reset: Delete user from database:
   ```sql
   DELETE FROM users WHERE email = 'your@email.com';
   ```

#### Error: "Invalid email or password"
**Cause**: Wrong credentials

**Solution**:
1. Check email spelling
2. Verify password
3. Try registering new account
4. Check caps lock

#### Error: "User not found"
**Cause**: User deleted or token invalid

**Solution**:
1. Register new account
2. Clear localStorage and login again

### Backtest Issues

#### Error: "Failed to save backtest to database"
**Cause**: Database connection lost during backtest

**Solution**:
1. Check PostgreSQL is running
2. Verify database connection
3. Check database logs
4. Restart backend

#### Backtest runs but doesn't save
**Cause**: User not authenticated

**Solution**:
1. Login first
2. Check JWT token in localStorage
3. Verify Authorization header sent

#### Error: "Backtest failed: [error message]"
**Cause**: Various backtest execution errors

**Solution**:
1. Check strategy text for malicious patterns
2. Verify stock symbol is valid
3. Check date range is valid
4. See backend logs for details

### Frontend Issues

#### Page shows "Loading..." forever
**Cause**: Backend not running or API unreachable

**Solution**:
1. Check backend is running: `python main.py`
2. Check API URL in `frontend/.env.local`
3. Check CORS settings in backend
4. Check firewall/network

#### Profile page shows "Failed to load profile"
**Cause**: Not authenticated or token expired

**Solution**:
1. Login again
2. Check localStorage has access_token
3. Check token expiration time
4. Restart frontend

#### "Cannot find module" errors
**Cause**: Dependencies not installed

**Solution**:
```bash
cd frontend
npm install
npm run dev
```

#### Styles not loading (page looks broken)
**Cause**: Tailwind CSS not compiled

**Solution**:
```bash
cd frontend
npm run build
npm run dev
```

### Backend Issues

#### Error: "ModuleNotFoundError: No module named 'database'"
**Cause**: Python path issue or dependencies not installed

**Solution**:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Error: "ImportError: cannot import name 'Base'"
**Cause**: Circular import or missing __init__.py

**Solution**:
1. Verify `backend/database/__init__.py` exists
2. Check imports in models.py
3. Restart Python interpreter

#### Error: "TypeError: 'coroutine' object is not subscriptable"
**Cause**: Async/await issue

**Solution**:
1. Ensure all database calls use `await`
2. Check function signatures
3. Verify async context

#### Error: "sqlalchemy.exc.IntegrityError"
**Cause**: Database constraint violation

**Solution**:
1. Check for duplicate emails
2. Verify foreign key references
3. Check data types match schema

### Performance Issues

#### Backtest runs very slowly
**Cause**: Large dataset or inefficient strategy

**Solution**:
1. Reduce date range
2. Simplify strategy
3. Check system resources
4. Monitor database performance

#### Database queries are slow
**Cause**: Missing indexes or large dataset

**Solution**:
1. Check database indexes
2. Optimize queries
3. Archive old backtests
4. Monitor database size

#### Frontend is slow
**Cause**: Large data transfer or rendering

**Solution**:
1. Implement pagination
2. Lazy load data
3. Optimize components
4. Check network tab

### Data Issues

#### Backtests not appearing in profile
**Cause**: Not saved to database

**Solution**:
1. Check user is authenticated
2. Verify database connection
3. Check database has backtest records:
   ```sql
   SELECT * FROM backtests WHERE user_id = 'your-user-id';
   ```

#### Trades missing from backtest detail
**Cause**: Trades not saved

**Solution**:
1. Check trades table:
   ```sql
   SELECT * FROM trades WHERE backtest_id = 'backtest-id';
   ```
2. Verify backtest execution completed
3. Check database logs

#### Equity curve not showing
**Cause**: Equity points not saved

**Solution**:
1. Check equity_curve table:
   ```sql
   SELECT * FROM equity_curve WHERE backtest_id = 'backtest-id';
   ```
2. Verify backtest has equity data
3. Check chart component

### Database Issues

#### Error: "relation 'users' does not exist"
**Cause**: Tables not created

**Solution**:
1. Restart backend (triggers table creation)
2. Or manually create tables:
   ```bash
   cd backend
   python -c "from database.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

#### Error: "column 'id' does not exist"
**Cause**: Schema mismatch

**Solution**:
1. Drop and recreate database:
   ```sql
   DROP DATABASE trading_backtester;
   CREATE DATABASE trading_backtester;
   ```
2. Restart backend

#### Database is locked
**Cause**: Another process accessing database

**Solution**:
1. Close other connections
2. Restart PostgreSQL
3. Check for long-running queries

### Deployment Issues

#### Error: "SECRET_KEY not set"
**Cause**: Environment variable missing

**Solution**:
1. Set SECRET_KEY in environment
2. Or update .env file
3. Restart application

#### Error: "CORS error"
**Cause**: Frontend and backend on different origins

**Solution**:
1. Check CORS settings in main.py
2. Update allow_origins if needed
3. Verify frontend URL

#### Error: "SSL certificate error"
**Cause**: HTTPS certificate issue

**Solution**:
1. Use valid certificate
2. Or disable SSL for development
3. Update DATABASE_URL protocol

## Debug Mode

### Enable Verbose Logging

**Backend**:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```javascript
// In browser console
localStorage.setItem('debug', '*')
```

### Check Database State

```bash
# Connect to database
psql -U postgres -d trading_backtester

# List tables
\dt

# Check users
SELECT * FROM users;

# Check backtests
SELECT * FROM backtests;

# Check trades
SELECT * FROM trades;

# Check equity curve
SELECT * FROM equity_curve;
```

### Monitor Backend Logs

```bash
cd backend
python main.py 2>&1 | tee backend.log
```

### Monitor Frontend Logs

```bash
# Browser DevTools
F12 → Console tab
```

## Getting Help

1. **Check logs first**
   - Backend: `python main.py` output
   - Frontend: Browser console (F12)
   - Database: PostgreSQL logs

2. **Verify configuration**
   - Check `.env` file
   - Verify DATABASE_URL
   - Check SECRET_KEY

3. **Test connectivity**
   - Backend: `curl http://localhost:8000/health`
   - Database: `psql -U postgres -d trading_backtester -c "SELECT 1"`

4. **Reset everything**
   ```bash
   # Stop services
   # Clear database
   psql -U postgres -c "DROP DATABASE trading_backtester;"
   psql -U postgres -c "CREATE DATABASE trading_backtester;"
   # Clear frontend cache
   rm -rf frontend/.next
   # Restart services
   ```

## Performance Optimization

### Database
- Add indexes on frequently queried columns
- Archive old backtests
- Use connection pooling
- Monitor query performance

### Backend
- Cache strategy parsing results
- Implement request rate limiting
- Use async operations
- Monitor memory usage

### Frontend
- Implement pagination
- Lazy load components
- Cache API responses
- Optimize bundle size

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set CORS_ORIGINS appropriately
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Monitor access logs
- [ ] Update dependencies regularly
- [ ] Use strong JWT expiration

## Still Having Issues?

1. Check all error messages carefully
2. Review logs for stack traces
3. Verify all configuration
4. Test each component independently
5. Try resetting the database
6. Restart all services
7. Check system resources
8. Review recent changes
