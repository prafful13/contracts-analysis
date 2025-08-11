#!/bin/bash

# =============================================================================
# ## Start Script for Options Screener App ##
# =============================================================================
# This script automates the startup process for both the Python backend
# and the React frontend, running each in the background and routing
# their logs to a 'logs' directory.

echo "Starting Options Screener Application..."

# Create a logs directory if it doesn't exist
mkdir -p logs

# --- Start Python Backend ---
echo "--> Starting Python backend... Logs will be in logs/backend.log"
source venv/bin/activate
pip install -r backend/requirements.txt
# Redirect stdout and stderr to the log file
python backend/app.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "    Backend started with PID: $BACKEND_PID"
deactivate

# --- Start React Frontend ---
echo "--> Starting React frontend... Logs will be in logs/frontend.log"
cd frontend
npm install
# Redirect stdout and stderr to the log file in the parent directory
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > frontend.pid
echo "    Frontend started with PID: $FRONTEND_PID"

echo ""
echo "✅ Application is starting up. Frontend should be available at http://localhost:5173"
echo "   You can monitor logs by running: tail -f logs/backend.log or logs/frontend.log"
