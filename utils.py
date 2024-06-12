from sentence_transformers import SentenceTransformer
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI


class MyUtilityFunctions:

    def __init__(self):
        #initialize code only once.
        load_dotenv()
        self.embeddingsmodel = SentenceTransformer("all-MiniLM-L6-v2")

        #  database connection details
        self.host = os.getenv('DB_HOST')
        self.dbname = os.getenv('DB_NAME')
        self.user =  os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')


    def get_embeddings(self, sentences, print_flag=False):
        # Sentences are encoded by calling model.encode()
        embeddings = self.embeddingsmodel.encode(sentences)

        if print_flag:
            # Print the embeddings
            for sentence, embedding in zip(sentences, embeddings):
                print("Sentence:", sentence)
                # Print a summary of the embedding instead of the full embedding
                print("Embedding", embedding)
                print("")

        return embeddings


    def connect_db(self):
        try:
            return psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
            print("Database connection established.")
        except Exception as e:
            return "no connection"
            print(f"Failed to connect to the database: {e}")

    
    def load_text(self, documents):
        # documents = loader.load()  # if txt file
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        texts = text_splitter.split_documents(documents)

        return texts

    def store_embeddings(self, connection, texts, doc_vectors):
        with connection.cursor() as cursor:
        # Construct the SQL INSERT statement
            insert_statement = """
            INSERT INTO embeddings_table (text_data, embeddings) VALUES (%s, %s)
            """
            
            # Process each item
            for ind, (sentence, embedding) in enumerate(zip(texts, doc_vectors)):
                try:
                    # Data to insert
                    embedding_value = embedding.tolist()  # Convert numpy array to list
                    text_value = sentence.page_content  # Make sure 'sentence' has the attribute 'page_content'
                    
                    # Execute the SQL command
                    cursor.execute(insert_statement, (text_value, embedding_value))
                    
                except Exception as e:
                    print(f"Failed to insert record {ind}: {e}")
                    connection.rollback()  # Rollback the transaction
                    continue  # Continue with the next record
                
            connection.commit()  # Commit the transaction
    #
        connection.rollback()  # Rollback the transaction

    def get_resutls(self, connection, prompt):
        prompt_embedding = self.get_embeddings(prompt, False)
        prompt_embedding = prompt_embedding.tolist()
        #print(prompt_embedding)

        cursor = connection.cursor()

        query = """
        SELECT id, text_data, 1 - (embeddings <=> %s::vector) AS similarity
        FROM embeddings_table
        ORDER BY similarity DESC
        LIMIT 1;
        """

        cursor.execute(query, (prompt_embedding,))
        results = cursor.fetchall()
        text = [t for _, t, _ in results]
        return text #returns only the text 
