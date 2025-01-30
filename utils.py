import json
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import datetime 
import pprint
import re
import numpy as np

class MyUtilityFunctions:
    def __init__(self):
        #initialize code only once.
        self.llm_url = "http://localhost:11434/api/chat"
        load_dotenv()
        self.embeddingsmodel = SentenceTransformer("all-MiniLM-L6-v2")
        self.dbname = os.getenv('DB_NAME')
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')

    def get_embeddings(self, sentences, print_flag=False):
        """Get embeddings for sentences"""
        embeddings = self.embeddingsmodel.encode(sentences, show_progress_bar=False)
        return embeddings

    def connect_db(self):
        try:
            connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
            return connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def clean_text(self, text):
        """Clean and normalize text"""
        text = text.replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def preprocess_text(self, text):
        """Preprocess text with improved paragraph and semantic boundary detection"""
        # Remove multiple spaces, newlines, and tabs
        text = re.sub(r'\s+', ' ', text)
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        
        processed_chunks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Split very long paragraphs
            if len(para.split()) > 50:  # Reduced from 100 to 50 words
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_chunk = []
                current_length = 0
                
                for sentence in sentences:
                    words = sentence.split()
                    if current_length + len(words) <= 50:
                        current_chunk.append(sentence)
                        current_length += len(words)
                    else:
                        if current_chunk:
                            processed_chunks.append(' '.join(current_chunk))
                        current_chunk = [sentence]
                        current_length = len(words)
                
                if current_chunk:
                    processed_chunks.append(' '.join(current_chunk))
            else:
                processed_chunks.append(para)
        
        return processed_chunks

    def split_text_into_chunks(self, paragraphs, max_chunk_size=256, overlap_size=25):
        """Split text into chunks while preserving semantic boundaries"""
        chunks = []
        chunk_metadata = []
        
        for i, para in enumerate(paragraphs):
            words = para.split()
            if len(words) <= max_chunk_size:
                chunks.append(para)
                chunk_metadata.append({
                    'start_idx': i,
                    'end_idx': i,
                    'is_complete_para': True
                })
                continue
            
            # Process longer paragraphs
            start = 0
            while start < len(words):
                end = min(start + max_chunk_size, len(words))
                chunk = ' '.join(words[start:end])
                chunks.append(chunk)
                
                chunk_metadata.append({
                    'start_idx': i,
                    'end_idx': i,
                    'start_pos': start,
                    'end_pos': end,
                    'is_complete_para': end >= len(words) and start == 0
                })
                
                start = end - overlap_size
                if start < 0:
                    break
        
        return chunks, chunk_metadata

    def store_embeddings(self, connection, texts, doc_vectors, metadata=None):
        """Store embeddings in database"""
        with connection.cursor() as cursor:
            # First check if table exists and has the correct schema
            check_table = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'embeddings_table'
            );
            """
            cursor.execute(check_table)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("Table doesn't exist! Please run create_table.py first")
                return
            
            # Get the dimension of the first vector to verify
            if len(doc_vectors) > 0:
                vector_dim = len(doc_vectors[0])
                print(f"Vector dimension: {vector_dim}")
            
            insert_statement = """
            INSERT INTO embeddings_table 
            (text_data, embeddings, chunk_start, chunk_end, is_complete_para, metadata) 
            VALUES (%s, %s::vector, %s, %s, %s, %s)
            RETURNING id;
            """
            
            inserted_count = 0
            for ind, (text, embedding) in enumerate(zip(texts, doc_vectors)):
                try:
                    meta = metadata[ind] if metadata else {}
                    chunk_start = meta.get('start_idx', 0)
                    chunk_end = meta.get('end_idx', 0)
                    is_complete = meta.get('is_complete_para', True)
                    
                    cursor.execute(insert_statement, (
                        text,
                        embedding.tolist(),
                        chunk_start,
                        chunk_end,
                        is_complete,
                        json.dumps(meta)
                    ))
                    inserted_id = cursor.fetchone()[0]
                    inserted_count += 1
                    
                except Exception as e:
                    print(f"Failed to insert record {ind}: {e}")
                    connection.rollback()
                    continue
                    
            connection.commit()
            print(f"Successfully inserted {inserted_count} embeddings")

    def get_results(self, connection, prompt):
        prompt_embedding = self.get_embeddings([prompt], False)[0]
        print(f"Search vector dimension: {len(prompt_embedding)}")
        
        with connection.cursor() as cursor:
            # First check if we have any data
            cursor.execute("SELECT COUNT(*) FROM embeddings_table")
            count = cursor.fetchone()[0]
            print(f"Total records in database: {count}")
            
            if count == 0:
                print("No data in database!")
                return []
            
            # Query to find similar texts using cosine similarity with proper vector casting
            query = """
            WITH similarity_scores AS (
                SELECT 
                    text_data,
                    1 - (embeddings <=> %s::vector) as similarity,
                    chunk_start,
                    chunk_end,
                    is_complete_para,
                    metadata
                FROM embeddings_table
                WHERE 1 - (embeddings <=> %s::vector) > 0.4
                ORDER BY similarity DESC
                LIMIT 5
            )
            SELECT 
                text_data,
                similarity,
                chunk_start,
                chunk_end,
                is_complete_para,
                metadata
            FROM similarity_scores
            ORDER BY chunk_start, chunk_end;
            """
            
            cursor.execute(query, (prompt_embedding.tolist(), prompt_embedding.tolist()))
            results = cursor.fetchall()
            print(f"Found {len(results)} matching results")
            
            formatted_results = []
            for row in results:
                text, similarity, start, end, is_complete, meta = row
                formatted_results.append({
                    'text': text,
                    'similarity': float(similarity),
                    'chunk_start': start,
                    'chunk_end': end,
                    'is_complete_para': is_complete,
                    'metadata': meta
                })
            
            return formatted_results

    def format_results_summary(self, query, results):
        """Create a human-readable summary of the search results"""
        if not results:
            return "No relevant information found."
            
        summary = f"Search Results for: '{query}'\n"
        summary += f"Found {len(results)} relevant passages:\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"Passage {i} (Relevance: {result['similarity']:.1%})\n"
            summary += f"{'─' * 80}\n"
            summary += f"{result['text']}\n\n"
        
        return summary

    def clear_db(self, connection):
        """Clear all data from the embeddings table"""
        try:
            with connection.cursor() as cursor:
                # SQL statement to clear the data in the embeddings_table
                clear_data_query = "TRUNCATE TABLE embeddings_table;"
                cursor.execute(clear_data_query)
                connection.commit()
                print("Data in 'embeddings_table' cleared successfully")
                return "Data in 'embeddings_table' cleared successfully"
                
        except Exception as e:
            print(f"Error clearing database: {e}")
            if connection:
                connection.rollback()
            return f"Error clearing database: {e}"