#!/bin/bash

# Trading Strategy Backtester - Quick Start Script
# This script sets up and runs the entire project

set -e

echo "================================"
echo "Trading Strategy Backtester"
echo "Quick Start Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
echo ""

# Check Node.js
echo -e "${BLUE}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Found: Node.js $NODE_VERSION${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}Setting up Backend...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Setup Frontend
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install -q
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
cd ..
echo ""

# Display instructions
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}To start the application, open TWO terminal windows:${NC}"
echo ""
echo -e "${BLUE}Terminal 1 - Backend API:${NC}"
echo "  source venv/bin/activate"
echo "  python backend/main.py"
echo ""
echo -e "${BLUE}Terminal 2 - Frontend:${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Then open your browser to:${NC}"
echo "  http://localhost:3000"
echo ""
echo -e "${YELLOW}API Documentation:${NC}"
echo "  http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy backtesting! 🚀${NC}"
