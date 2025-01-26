import psycopg2
import os
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()


def create_table():
    # Database connection parameters
    connection_params = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    enable_extension_query = """
    CREATE EXTENSION IF NOT EXISTS vector;
    """
    # SQL statement to create a new table
    create_table_query = """
    CREATE TABLE embeddings_table (
        id SERIAL PRIMARY KEY,
        text_data TEXT NOT NULL,
        embeddings vector NOT NULL
    );
    """

    try:
        # Establish a database connection
        connection = psycopg2.connect(**connection_params)

        # Open a cursor to perform database operations
        with connection.cursor() as cursor:
            cursor.execute(enable_extension_query)
            connection.commit()
            # Execute the SQL statement to create the table
            cursor.execute(create_table_query)
            # Commit the transaction
            connection.commit()

        print("Table 'embeddings_table' created successfully")

    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        # Close the connection
        if connection:
            connection.close()

# Call the function to create the table
create_table()