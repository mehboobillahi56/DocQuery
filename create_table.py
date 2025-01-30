import psycopg2
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from the .env file
load_dotenv()

def create_table():
    # Get embedding dimension from the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sample_text = "This is a test sentence."
    embedding = model.encode([sample_text])[0]
    embedding_dim = len(embedding)
    logging.debug(f"Model embedding dimension: {embedding_dim}")
    
    # Database connection parameters
    connection_params = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

    # Enable required PostgreSQL extensions
    enable_extension_query = """
    CREATE EXTENSION IF NOT EXISTS vector;
    """

    # Drop existing table if it exists
    drop_table_query = """
    DROP TABLE IF EXISTS embeddings_table;
    """

    # SQL statement to create a new table with improved schema
    create_table_query = f"""
    CREATE TABLE embeddings_table (
        id SERIAL PRIMARY KEY,
        text_data TEXT NOT NULL,
        embeddings vector({embedding_dim}) NOT NULL,
        chunk_start INTEGER NOT NULL,
        chunk_end INTEGER NOT NULL,
        is_complete_para BOOLEAN DEFAULT true,
        metadata JSONB DEFAULT '{{}}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        similarity_threshold FLOAT DEFAULT 0.6
    );
    """

    # Create indexes for better query performance
    create_indexes_query = """
    CREATE INDEX idx_embeddings ON embeddings_table USING ivfflat (embeddings vector_cosine_ops)
    WITH (lists = 100);
    
    CREATE INDEX idx_chunk_positions ON embeddings_table(chunk_start, chunk_end);
    """

    try:
        # Establish a database connection
        connection = psycopg2.connect(**connection_params)

        # Open a cursor to perform database operations
        with connection.cursor() as cursor:
            logging.debug("Enabling required extensions...")
            cursor.execute(enable_extension_query)
            connection.commit()

            logging.debug("Dropping existing table if present...")
            cursor.execute(drop_table_query)
            connection.commit()

            logging.debug("Creating new table with updated schema...")
            cursor.execute(create_table_query)
            connection.commit()

            logging.debug("Creating indexes for better query performance...")
            cursor.execute(create_indexes_query)
            connection.commit()

        logging.info("✅ Table 'embeddings_table' created successfully with the following improvements:")
        logging.info(f"  - Vector dimension set to {embedding_dim}")
        logging.info("  - Added chunk position tracking")
        logging.info("  - Added paragraph completeness flag")
        logging.info("  - Added metadata storage in JSONB format")
        logging.info("  - Added creation timestamp")
        logging.info("  - Added similarity threshold")
        logging.info("  - Added optimized indexes for faster queries")

    except Exception as e:
        logging.error(f"❌ Error creating table: {e}")
    finally:
        # Close the connection
        if connection:
            connection.close()
            logging.debug("Database connection closed.")

if __name__ == "__main__":
    create_table()