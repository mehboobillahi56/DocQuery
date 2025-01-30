#!/bin/bash

# Application ports
FASTAPI_PORT=8080    # Main backend API
GRADIO_PORT=7860     # UI interface
OLLAMA_PORT=11434    # LLM service
DB_PORT=5432         # PostgreSQL database

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i ":$port" >/dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Function to kill process using a specific port
kill_port_process() {
    local port=$1
    local service=$2
    echo "Freeing port $port ($service)..."
    
    local pid=$(lsof -t -i ":$port" 2>/dev/null)
    
    if [ ! -z "$pid" ]; then
        echo "Found process using port $port: $pid"
        kill -15 $pid 2>/dev/null || kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

echo "🧹 Cleaning up application ports..."

# Clean up FastAPI (Backend)
if check_port $FASTAPI_PORT; then
    kill_port_process $FASTAPI_PORT "FastAPI Backend"
fi

# Clean up Gradio (UI)
if check_port $GRADIO_PORT; then
    kill_port_process $GRADIO_PORT "Gradio UI"
fi

# Clean up Ollama (LLM)
if check_port $OLLAMA_PORT; then
    kill_port_process $OLLAMA_PORT "Ollama LLM"
fi

# Clean up PostgreSQL (if running locally)
if check_port $DB_PORT; then
    kill_port_process $DB_PORT "PostgreSQL"
fi

# Final verification
echo "🔍 Verifying ports..."
sleep 2

# Check all ports
declare -A ports=(
    [$FASTAPI_PORT]="FastAPI Backend"
    [$GRADIO_PORT]="Gradio UI"
    [$OLLAMA_PORT]="Ollama LLM"
    [$DB_PORT]="PostgreSQL"
)

all_free=true

for port in "${!ports[@]}"; do
    if check_port $port; then
        echo "❌ Port $port (${ports[$port]}) is still in use"
        all_free=false
    else
        echo "✅ Port $port (${ports[$port]}) is free"
    fi
done

if [ "$all_free" = true ]; then
    echo "✅ All application ports are free!"
else
    echo "⚠️  Some ports are still in use. You may need to restart the services."
fi
