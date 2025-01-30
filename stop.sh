#!/bin/bash

# Function to check if a command was successful
check_status() {
    if [ $? -ne 0 ]; then
        echo "Warning: $1"
    fi
}

echo "🛑 Stopping all applications..."

# Stop tmux sessions
echo "📝 Stopping tmux sessions..."
tmux kill-server 2>/dev/null
check_status "Failed to stop tmux sessions"

# Stop Docker containers
echo "🐳 Stopping Docker containers..."
docker compose down 2>/dev/null
check_status "Failed to stop Docker containers"

# Stop Ollama service
echo "🤖 Stopping Ollama service..."
if command -v ollama &> /dev/null; then
    pkill ollama 2>/dev/null
    check_status "Failed to stop Ollama service"
fi

# Check for any remaining Python processes
echo "🐍 Checking for remaining Python processes..."
pkill -f "python3 main.py" 2>/dev/null
pkill -f "python3 Ui.py" 2>/dev/null

echo "✅ All applications have been stopped."
echo "Note: If you see any warnings above, you can safely ignore them if those services weren't running."
