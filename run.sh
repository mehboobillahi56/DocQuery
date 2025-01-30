#!/bin/bash

# Function to check if a command was successful
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i ":$port" >/dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Function to check if any of our services are running
check_running_services() {
    local services_running=false

    echo "🔍 Checking for running services..."
    
    # Check tmux sessions
    if tmux ls 2>/dev/null | grep -qE '(backend|frontend|ollama|mistral)'; then
        echo "⚠️  Found existing tmux sessions"
        services_running=true
    fi

    # Check FastAPI port (8080)
    if check_port 8080; then
        echo "⚠️  Port 8080 (FastAPI) is already in use"
        services_running=true
    fi

    # Check Gradio port (7860)
    if check_port 7860; then
        echo "⚠️  Port 7860 (Gradio UI) is already in use"
        services_running=true
    fi

    # Check Docker containers
    if docker ps 2>/dev/null | grep -q "postgres:pdfencoder"; then
        echo "⚠️  Found running Docker containers"
        services_running=true
    fi

    # Check Ollama process
    if pgrep -f "ollama" >/dev/null; then
        echo "⚠️  Ollama service is running"
        services_running=true
    fi

    if [ "$services_running" = true ]; then
        echo ""
        echo "❗ Some services are already running."
        read -p "Would you like to stop them before continuing? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🛑 Stopping existing services..."
            ./stop.sh
            sleep 2 # Give services time to stop
        else
            echo "⚠️  Warning: Starting new instances might conflict with running services"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "❌ Aborting startup"
                exit 1
            fi
        fi
    fi
}

# Check for running services before starting
check_running_services

echo "🚀 Starting DocQuery Setup..."

# Check and install tmux if not present
if ! command -v tmux &> /dev/null; then
    echo "📦 Installing tmux..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y tmux
    elif command -v yum &> /dev/null; then
        sudo yum install -y tmux
    elif command -v brew &> /dev/null; then
        brew install tmux
    else
        echo "Error: Could not install tmux. Please install it manually."
        exit 1
    fi
    check_status "tmux installation"
fi

# 1. Clone repository and install requirements
cd DocQuery
echo "📥 Installing Python requirements..."
pip install -r requirements.txt
check_status "Requirements installation"

# 2. Build and run Docker containers
echo "🐳 Checking PostgreSQL Docker image..."
if ! docker images postgres:pdfencoder | grep -q pdfencoder; then
    echo "🏗️ Building PostgreSQL Docker image..."
    docker build --no-cache -t postgres:pdfencoder .
    check_status "Docker build"
else
    echo "✅ PostgreSQL Docker image already exists"
fi

echo "🚀 Starting Docker containers..."
docker compose up -d
check_status "Docker compose"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# 3. Create database tables
echo "🗄️ Creating database tables..."
python3 create_table.py
check_status "Database table creation"

# 4. Setup Ollama and run model
if ! command -v ollama &> /dev/null; then
    echo "🤖 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    check_status "Ollama installation"
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service in detached mode
echo "🔄 Starting Ollama service..."
tmux new-session -d -s ollama 'ollama serve'
check_status "Ollama service start"

# Wait for Ollama service to start
sleep 5

echo "📥 Pulling Mistral model..."
ollama pull mistral:7b-instruct-q4_K_M
check_status "Model pull"

echo "🚀 Running Mistral model..."
tmux new-session -d -s mistral 'ollama run mistral:7b-instruct-q4_K_M'
check_status "Model run"

# 5. Run the main application
echo "🌟 Starting FastAPI backend..."
cd "$(dirname "$0")"  # Change to the script's directory
tmux new-session -d -s backend 'python3 main.py'
check_status "FastAPI backend"

# Wait for FastAPI to start
echo "⏳ Waiting for FastAPI to initialize..."
sleep 5

# 6. Run the UI application
echo "🌟 Starting Gradio UI..."
tmux new-session -d -s frontend 'python3 Ui.py'
check_status "Gradio UI"

echo "✅ Setup complete! Your application is running."
echo "📝 tmux sessions created:"
echo "   - ollama: Ollama service"
echo "   - mistral: Mistral model"
echo "   - backend: FastAPI backend"
echo "   - frontend: Gradio UI"
echo ""
echo "To view sessions, use: tmux ls"
echo "To attach to a session, use: tmux attach -t SESSION_NAME"
echo "Access the FastAPI docs at: http://localhost:8080/docs"
echo "Access the Gradio UI at: http://localhost:7860"
