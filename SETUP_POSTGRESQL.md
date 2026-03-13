# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL for the Trading Strategy Backtester with user authentication and persistent storage.

## Prerequisites

- PostgreSQL 12+ installed
- Python 3.8+
- Node.js 18+

## Step 1: Install PostgreSQL

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation, set password for `postgres` user (e.g., `1234`)
4. Keep default port `5432`
5. Complete the installation

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Step 2: Create Database

Open PostgreSQL command line:

### Windows (pgAdmin or psql)
```bash
psql -U postgres
```

### macOS/Linux
```bash
psql -U postgres
```

Then run:
```sql
CREATE DATABASE trading_backtester;
\q
```

## Step 3: Update Backend Environment

Edit `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:1234@localhost:5432/trading_backtester
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace `1234` with your PostgreSQL password if different.

## Step 4: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 5: Initialize Database

The database tables will be created automatically when you start the backend server.

To verify tables were created:

```bash
psql -U postgres -d trading_backtester -c "\dt"
```

You should see:
- users
- strategies
- backtests
- trades
- equity_curve

## Step 6: Run Backend

```bash
cd backend
python main.py
```

The server will start at `http://localhost:8000`

## Step 7: Run Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Step 8: Test the System

1. Go to http://localhost:3000
2. Click "Sign Up" to create an account
3. Fill in your details and create an account
4. You'll be redirected to the dashboard
5. Run a backtest
6. Go to your profile to see saved strategies and backtests

## Database Migrations (Optional)

If you need to make schema changes:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## Troubleshooting

### Connection Error: "could not connect to server"
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify password is correct

### "database does not exist"
- Create the database using the SQL command above
- Restart the backend server

### "relation does not exist"
- Tables weren't created. Restart the backend server
- Check backend logs for errors

### Port 5432 already in use
- Change the port in DATABASE_URL
- Or stop the service using port 5432

## Backup and Restore

### Backup Database
```bash
pg_dump -U postgres trading_backtester > backup.sql
```

### Restore Database
```bash
psql -U postgres trading_backtester < backup.sql
```

## Production Considerations

1. Use strong SECRET_KEY
2. Set ACCESS_TOKEN_EXPIRE_MINUTES appropriately
3. Use environment variables for sensitive data
4. Enable SSL for database connections
5. Set up regular backups
6. Use connection pooling for production
7. Monitor database performance

## Next Steps

- Customize the authentication system
- Add email verification
- Implement password reset
- Add user roles and permissions
- Set up monitoring and logging
