from sentence_transformers import SentenceTransformer
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import psycopg2
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import pandas as pd
import requests
import json
from random import randrange, choice
import datetime 
import pprint
import re

class MyUtilityFunctions:

    def __init__(self):
        #initialize code only once.
        self.llm_url = "http://localhost:11434/api/chat"
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

    def extract_text_from_pdf(self,pdf_path):
        pdf_document = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text

    def extract_text_from_txt(self,txt_path):
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    

    def preprocess_text(self, text):
        # Remove multiple spaces, newlines, and tabs
        text = re.sub(r'\s+', ' ', text)
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        return paragraphs
    

    def split_text_into_chunks(self, text, chunk_size, overlap_size):
        words = text[0].split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = start + chunk_size - overlap_size
        return chunks
    
    # def load_text(self, documents):
    #     # documents = loader.load()  # if txt file
    #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    #     texts = text_splitter.split_documents(documents)

    #     return texts


    def prompt_to_llm(self,database_text,userprompt):
       
       promptrule = "removing any unnecessary spacing or extra lines or intendent error. "

       finalprompt = f"""
        
        Summarize these {database_text} to best answer the user question, do not keep repetative lines and if the the results are empty list then responce with no data found.

        User Question: {userprompt}
        {promptrule} """

       data = {
            "model": "mistral:7b-instruct-q4_K_M",
            "temperature": 0.2,
            "messages": [
                {"role": "user", "content": finalprompt,},
            ],
            "stream": False
        }

        #print("User: ", finalprompt)
       response = requests.post(self.llm_url, json=data)
       content = res = json.loads(response.text)



        #print("CyLLM:")
       return content["message"]["content"].replace("<|eot_id|>", "")

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
                    text_value = sentence#.page_content  # Make sure 'sentence' has the attribute 'page_content'
                    
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
        LIMIT 2;
        """

        cursor.execute(query, (prompt_embedding,))
        results = cursor.fetchall()
        text = [t for _, t, _ in results]
        return text #returns only the text 


    def clear_db(self,connection):
        cursor = connection.cursor()
        # SQL statement to clear the data in the embeddings_table
        clear_data_query = """
        TRUNCATE TABLE embeddings_table;
        """
        try:
            cursor.execute(clear_data_query)
            connection.commit()
            print("Data in 'embeddings_table' cleared successfully.")

        except Exception as e:
            print(f"Error: {e}")
            if connection:
                connection.rollback()  # Rollback the transaction in case of error
        finally:
            # Close the connection
            if connection:
                connection.close()
                print("Database connection closed.")
        return "Data in 'embeddings_table' cleared successfully."