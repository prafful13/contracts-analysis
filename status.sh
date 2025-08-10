#!/bin/bash

# =============================================================================
# ## Status Script for Options Screener App ##
# =============================================================================
# This script checks the status of the backend and frontend servers
# by checking for their PID files and specific processes on listening ports.

echo "Checking application status..."
echo ""

# --- Check Backend Status (Port 5000) ---
BACKEND_PID_FROM_FILE=$(cat backend.pid 2>/dev/null)
if [ -n "$BACKEND_PID_FROM_FILE" ] && ps -p "$BACKEND_PID_FROM_FILE" > /dev/null; then
    echo "🟢 Backend Server:   RUNNING (PID: $BACKEND_PID_FROM_FILE)"
else
    # Fallback to check the port for a Python process if no valid pid file is found
    if lsof -i :5000 | grep "Python" > /dev/null; then
        echo "🟢 Backend Server:   RUNNING (PID not tracked)"
    else
        echo "🔴 Backend Server:   STOPPED"
        # Clean up stale pid file if it exists
        [ -f backend.pid ] && rm backend.pid
    fi
fi

# --- Check Frontend Status (Port 5173) ---
FRONTEND_PID_FROM_FILE=$(cat frontend.pid 2>/dev/null)
if [ -n "$FRONTEND_PID_FROM_FILE" ] && ps -p "$FRONTEND_PID_FROM_FILE" > /dev/null; then
    echo "🟢 Frontend Server:  RUNNING (PID: $FRONTEND_PID_FROM_FILE)"
else
    if lsof -i :5173 | grep "node" > /dev/null; then
        echo "🟢 Frontend Server:  RUNNING (PID not tracked)"
    else
        echo "🔴 Frontend Server:  STOPPED"
        [ -f frontend.pid ] && rm frontend.pid
    fi
fi

