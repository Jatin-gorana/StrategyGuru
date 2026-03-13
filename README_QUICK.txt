================================================================================
TRADING STRATEGY BACKTESTER - QUICK START GUIDE
================================================================================

FASTEST WAY (30 SECONDS)
================================================================================

macOS/Linux:
  chmod +x run.sh && ./run.sh

Windows:
  run.bat

Then follow on-screen instructions!

MANUAL SETUP (5 MINUTES)
================================================================================

Terminal 1 - Backend:
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate.bat # Windows
  pip install -r requirements.txt
  python backend/main.py

Terminal 2 - Frontend:
  cd frontend
  npm install
  npm run dev

Browser:
  http://localhost:3000

VERIFY EVERYTHING WORKS
================================================================================

Backend:  curl http://localhost:8000/health
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs

RUN YOUR FIRST BACKTEST
================================================================================

1. Go to http://localhost:3000
2. Enter: "Buy when RSI < 30 and sell when RSI > 70"
3. Stock: AAPL
4. Dates: 2023-01-01 to 2024-01-01
5. Click: "Run Backtest"
6. View: Dashboard with results
7. Click: "Improve Strategy" for AI suggestions

WHAT'S RUNNING
================================================================================

Frontend:        http://localhost:3000
Backend API:     http://localhost:8000
API Docs:        http://localhost:8000/docs

TROUBLESHOOTING
================================================================================

Port already in use?
  python backend/main.py --port 8001

Frontend won't start?
  cd frontend && rm -rf node_modules && npm install && npm run dev

API not responding?
  curl http://localhost:8000/health

DOCUMENTATION
================================================================================

START_HERE.md          - Overview
QUICK_START.md         - Fast setup
SETUP_AND_RUN.md       - Detailed guide
COMMANDS.md            - All commands
RUN_PROJECT.md         - How to run

READY TO START?
================================================================================

Choose your setup method above and get started!

Happy backtesting! 🚀
