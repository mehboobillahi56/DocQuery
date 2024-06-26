# DocQuery

Welcome to the DocQuery project, a versatile tool designed to extract and interact with textual content from PDFs and text files. This project initially targets Linux environments but can be adapted for Windows with minor modifications.

## Table of Contents

- [About the Project](#about-the-project)
- [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)


## About the Project

The DocQuery facilitates deep understanding and interaction with lengthy documents such as lease agreements, academic papers, or extensive reports. By storing these documents in a structured database and allowing real-time querying, this tool offers an innovative approach to document management and analysis.

### Built With

This project leverages cutting-edge technologies and frameworks to ensure high performance and scalability:
- **Sentence Transformers**: Utilized for converting textual data into meaningful embeddings. [Learn more](https://www.sbert.net/)
- **FastAPI**: Chosen for its high performance and ease of use in building APIs. [Learn more](https://fastapi.tiangolo.com/)
- **pgvector**: Used for efficient storage and retrieval of vector data in PostgreSQL. [Learn more](https://github.com/pgvector/pgvector)
- **LangChain**: Integrated to enhance natural language processing capabilities. [Learn more](https://github.com/langchain-ai/langchain)
- **Mistral-7B**: Deployed for advanced language understanding and generation. [Learn more](https://www.mistral.ai/)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Docker
- Python 3.x or later
- PostgreSQL, enhanced with the pgvector extension for vector operations

### Installation

Follow these steps to set up the DocQuery on your machine:
1. Clone the repository:
   ```sh
   git clone https://github.com/mehboobillahi56/DocQuery.git
   ```
   Alternatively, download the ZIP folder and extract it.

2. Navigate to the project directory:
   ```sh
   cd DocQuery
   ```

3. Install required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Build and run the PostgreSQL setup using Docker:
   ```sh
   docker build --no-cache -t postgres:pdfencoder .
   docker-compose up -d
   ```
   This will create a PostgreSQL database equipped with the pgvector extension.

5. Initialize the database:
   Execute the `create_db_table.ipynb` notebook to set up the necessary tables (`id`, `text`, `embeddings`) in your database.

## Usage

### Download and Install the LLM Model

1. **Install Ollama**: Download and install Ollama on your platform by visiting the following link:
   ```
   https://ollama.com/download
   ```

2. **Pull and Run the LLM Model**: Use the following command to pull and run the Mistral model:
   ```bash
   ollama run mistral:7b-instruct-q4_K_M
   ```

3. **Verify the LLM Model**: To ensure the model is downloaded and running correctly, execute:
   ```bash
   python mistral-7b.py
   ```

To use the DocQuery:
1. Launch the application:
   ```sh
   python main.py
   ```

2. Access the API in your web browser:
   ```
   http://localhost:8000/docs
   ```

3. Interact with the API to:
   - Upload PDF or text files and save their contents in the database.
   - Query and chat about the stored documents using provided API endpoints.

