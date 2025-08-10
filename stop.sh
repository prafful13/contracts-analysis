#!/bin/bash

# =============================================================================
# ## Stop Script for Options Screener App ##
# =============================================================================
# This script shuts down both the backend and frontend servers.

echo "Stopping Options Screener Application..."

# --- Stop Python Backend ---
if [ -f backend.pid ]; then
    PID=$(cat backend.pid)
    echo "--> Stopping backend process with PID: $PID"
    kill $PID
    rm backend.pid
else
    echo "--> No backend.pid file found. Attempting to stop Python process on port 5000..."
    # Find and kill the specific Python process listening on port 5000
    lsof -i tcp:5000 | grep Python | awk '{print $2}' | xargs kill -9 2>/dev/null
fi

# --- Stop React Frontend ---
if [ -f frontend.pid ]; then
    PID=$(cat frontend.pid)
    echo "--> Stopping frontend process with PID: $PID"
    kill $PID
    rm frontend.pid
else
    echo "--> No frontend.pid file found. Attempting to stop Node process on port 5173..."
    # Find and kill the specific Node process listening on port 5173
    lsof -i tcp:5173 | grep node | awk '{print $2}' | xargs kill -9 2>/dev/null
fi

echo ""
echo "✅ Application has been shut down."

