

## if 1st time uncomment below installation 
# !pip install -U sentence-transformers
# !pip install langchain openai python-dotenv
# !pip install psycopg2-binary pgvector
# !pip install -U langchain-community
# !pip install fastapi
# !pip install uvicorn
# !pip install pypdf




from utils import *

my_utilities = MyUtilityFunctions()


def process_text_embeddings(file_location):
    try:
       
        if file_location.endswith('.txt'):
            documents = my_utilities.extract_text_from_txt(file_location)
        else:
            documents = my_utilities.extract_text_from_pdf(file_location)
        
 
        preprocess = my_utilities.preprocess_text(documents)

        texts = my_utilities.split_text_into_chunks(preprocess, 20, 10)#(text, chunk_size, overlap_size)
        # Connect to database
        connection = my_utilities.connect_db()
        
        # If connection is successful
        if connection:
            # Get embeddings for the loaded text
            doc_vectors = my_utilities.get_embeddings([t for t in texts], False)
            
            # Store embeddings in the database
            my_utilities.store_embeddings(connection, texts, doc_vectors)
            
            # Remove temp file after processing
            os.remove(file_location)
            
            return {"message": "Text embeddings completed."}
        else:
            return {"error": "Failed to connect to the database."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def chat(text):
    try:
        # Connect to the database
        dbconnection = my_utilities.connect_db()
        # print(dbconnection)
        # text = my_utilities.preprocess_text(text)
        if dbconnection:
            # Get results from the database
            result = my_utilities.get_resutls(dbconnection,text)
            print("-"*60)
            print("Result: ", result)
            llm_summary = my_utilities.prompt_to_llm(result,text)
            print("llm_summary: ", llm_summary)
            print("-"*60)
            return my_utilities.preprocess_text(llm_summary)
            
        else:
            return {"error": "Failed to connect to the database."}

    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def clear_db():
    try:
        # Connect to the database
        dbconnection = my_utilities.connect_db()
        print(dbconnection)
        
        if dbconnection:
            # Get results from the database
            result = my_utilities.clear_db(dbconnection)
            
            return result
        else:
            return {"error": "Failed to connect to the database."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    
    
if __name__ == "__main__":
    process_text_embeddings('/home/illahi/linux-projects/genai_projects/Pdf-Txt-Encoder/AttentionIsAllYouNeed.pdf')