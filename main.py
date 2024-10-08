## if 1st time uncomment below installation 
# !pip install -U sentence-transformers
# !pip install langchain openai python-dotenv
# !pip install psycopg2-binary pgvector
# !pip install -U langchain-community
# !pip install fastapi
# !pip install uvicorn
# !pip install pypdf




from fastapi import FastAPI, UploadFile, File
import uvicorn
from utils import *
app =  FastAPI()

my_utilities = MyUtilityFunctions()


@app.post("/store_text_embeddings")
async def process_text_embeddings(doc: UploadFile = File(...)):
    try:
        # Read the content of the uploaded file
        print(doc.filename)

        file_location = f"temp/{doc.filename}"
        
        # Create temp directory if it does not exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        # Save the file to the temp directory
        with open(file_location, "wb+") as file_object:
            file_object.write(doc.file.read())
        
        
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


@app.get("/text_matching")
async def chat(text: str):
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

@app.get("/clear_data")
async def clear_db():
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
    uvicorn.run(app, host="0.0.0.0", port=8000)