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

@app.get("/")
async def read_root():
    return {"message": "Text Encoder APIs"}

doc = 'state_of_the_union.txt'
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
            # Create a loader instance for the text file
            loader = TextLoader(file_location, encoding='utf-8')
            documents = loader.load()
        else:
            # Create a loader instance for the PDF file
            loader = PyPDFLoader(file_location)
            documents = loader.load_and_split()
            # print(documents[0])

        texts = my_utilities.load_text(documents)
        
        # Connect to database
        connection = my_utilities.connect_db()
        
        # If connection is successful
        if connection:
            # Get embeddings for the loaded text
            doc_vectors = my_utilities.get_embeddings([t.page_content for t in texts], False)
            
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
async def process_text_embeddigs(text: str):
    try:
        # Connect to the database
        dbconnection = my_utilities.connect_db()
        print(dbconnection)
        # if dbconnection == '0':
        #     dbconnection.rollback()  # Rollback the transaction
        # if connection is succefull 
        if dbconnection:
            # Get results from the database
            result = my_utilities.get_resutls(dbconnection, text)
            
            # for id_, text_, conf_ in result:
            #     id = id_
            #     text = text_
            #     conf = conf_

            return result
        else:
            return {"error": "Failed to connect to the database."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)