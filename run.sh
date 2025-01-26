#!/bin/bash

# Function to check if a command was successful
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

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
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
check_status "Ollama installation"

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
echo "🌟 Starting main application..."
tmux new-session -d -s docquery 'python3 main.py'
check_status "Main application"

echo "✅ Setup complete! Your application is running."
echo "📝 tmux sessions created:"
echo "   - ollama: Ollama service"
echo "   - mistral: Mistral model"
echo "   - docquery: Main application"
echo ""
echo "To view sessions, use: tmux ls"
echo "To attach to a session, use: tmux attach -t SESSION_NAME"
echo "Access the API at: http://localhost:8000/docs"
