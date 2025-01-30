# DocQuery

Welcome to the DocQuery project, a versatile tool designed to extract and interact with textual content from PDFs and text files. This project is specifically built for Linux environments and leverages the power of modern AI and web technologies.

## Table of Contents

- [About the Project](#about-the-project)
- [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Features](#features)

## About the Project

The DocQuery facilitates deep understanding and interaction with lengthy documents such as lease agreements, academic papers, or extensive reports. By storing these documents in a structured database and allowing real-time querying, this tool offers an innovative approach to document management and analysis.

### Platform Support
- **Primary Platform**: Linux
- **Required OS Features**: 
  - Port management (for FastAPI, Gradio, and Ollama services)
  - PostgreSQL database support
  - Python 3.x environment

### Built With

This project leverages cutting-edge technologies and frameworks to ensure high performance and scalability:
- **Sentence Transformers**: Utilized for converting textual data into meaningful embeddings. [Learn more](https://www.sbert.net/)
- **FastAPI**: Chosen for its high performance and ease of use in building APIs. [Learn more](https://fastapi.tiangolo.com/)
- **pgvector**: Used for efficient storage and retrieval of vector data in PostgreSQL. [Learn more](https://github.com/pgvector/pgvector)
- **PostgreSQL**: Robust database for storing document text and embeddings
- **Python 3.x**: Core programming language
- **Gradio**: Provides an intuitive web interface for document upload and querying (Port 7860)
- **Ollama**: Local LLM service for enhanced text processing (Port 11434)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Linux operating system
- Python 3.x or later
- PostgreSQL with pgvector extension
- Required Python packages (see requirements.txt)
- Ollama (for LLM capabilities)
  ```sh
  # Install Ollama
  curl https://ollama.ai/install.sh | sh
  # Pull the required model
  ollama pull mistral:7b-instruct-q4_K_M
  ```

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/mehboobillahi56/DocQuery.git
   cd DocQuery
   ```

2. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   DB_HOST=localhost
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   ```

4. Initialize the database:
   ```sh
   python create_table.py
   ```

## Usage

1. Start the required services:
   ```sh
   # Start Ollama service (if not already running)
   ollama serve
   
   # Start the FastAPI server
   python main.py
   
   # The services will be available at:
   # - FastAPI: http://localhost:8080
   # - Gradio UI: http://localhost:7860
   # - Ollama: http://localhost:11434
   ```

2. Clean up ports if needed:
   ```sh
   ./cleanup_ports.sh
   ```

## API Endpoints

### 1. Store Text Embeddings
- **Endpoint**: POST `/store_text_embeddings`
- **Purpose**: Upload and process text files
- **Input**: Text file
- **Output**: Confirmation of storage

### 2. Text Matching
- **Endpoint**: GET `/text_matching`
- **Purpose**: Query the document
- **Input**: Text query
- **Output**: Relevant passages with similarity scores
- **Example Response**:
  ```json
  {
    "query": "what is mentioned about covid-19",
    "total_results": 5,
    "summary": "Search Results for: 'what is mentioned about covid-19'\nFound 5 relevant passages:\n\nPassage 1 (Relevance: 66.0%)...",
    "passages": [
      {
        "rank": 1,
        "text": "For more than two years, COVID-19 has impacted every decision...",
        "relevance_score": "66.0%",
        "metadata": {
          "paragraph": "89",
          "is_complete": true
        }
      }
    ]
  }
  ```

### 3. Clear Database
- **Endpoint**: GET `/clear_data`
- **Purpose**: Clear all stored embeddings
- **Output**: Confirmation message

## Features

### 1. Smart Text Processing
- Intelligent paragraph splitting
- Semantic boundary detection
- Overlap for context preservation

### 2. Advanced Search
- Semantic similarity search
- Cosine similarity scoring
- Configurable similarity thresholds

### 3. Rich Response Format
- Ranked passages
- Relevance scores
- Paragraph metadata
- Human-readable summaries

### 4. Resource Management
- Efficient port cleanup (FastAPI: 8080, Gradio: 7860, Ollama: 11434)
- Database connection pooling
- Proper error handling

### 5. User Interface
- Gradio web interface for easy interaction
- File upload capabilities
- Real-time query responses
- Interactive result display

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
