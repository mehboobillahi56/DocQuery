import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from utils import MyUtilityFunctions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
my_utilities = MyUtilityFunctions()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/store_text_embeddings")
async def process_text_embeddings(doc: UploadFile = File(...)):
    try:
        print("-" * 50)
        print(f"Received file upload request:")
        print(f"Filename: {doc.filename}")
        
        # Create temp directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Save the uploaded file temporarily
        file_location = f"temp/{doc.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await doc.read())
        print(f"Saved file to: {file_location}")
        
        # Read the text content
        with open(file_location, "r", encoding="utf-8") as file:
            text_content = file.read()
            print(f"File content length: {len(text_content)} characters")
        
        # Connect to database
        dbconnection = my_utilities.connect_db()
        
        if dbconnection:
            print("Connected to database successfully")
            
            # Process text and generate embeddings
            processed_text = my_utilities.preprocess_text(text_content)
            print(f"Processed text into {len(processed_text)} chunks")
            
            chunks, metadata = my_utilities.split_text_into_chunks(processed_text)
            print(f"Split into {len(chunks)} chunks with metadata")
            
            doc_vectors = my_utilities.get_embeddings(chunks)
            print(f"Generated {len(doc_vectors)} embeddings")
            
            # Store in database
            my_utilities.store_embeddings(dbconnection, chunks, doc_vectors, metadata)
            print("Stored embeddings in database")
            
            # Close database connection
            dbconnection.close()
            print("Database connection closed")
            
            # Clean up temporary file
            os.remove(file_location)
            print(f"Temporary file removed: {file_location}")
            
            return {"message": "Text embeddings completed successfully"}
        else:
            return {"error": "Failed to connect to the database"}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

@app.get("/text_matching")
async def chat(text: str):
    try:
        # Connect to the database
        dbconnection = my_utilities.connect_db()
        
        if dbconnection:
            # Get results from database
            results = my_utilities.get_results(dbconnection, text)
            
            # Close database connection
            dbconnection.close()
            
            # Format results in a more readable way
            formatted_response = {
                "query": text,
                "total_results": len(results),
                "summary": my_utilities.format_results_summary(text, results),
                "passages": []
            }
            
            for i, result in enumerate(results, 1):
                formatted_response["passages"].append({
                    "rank": i,
                    "text": result["text"],
                    "relevance_score": f"{result['similarity']:.2%}",
                    "metadata": {
                        "paragraph": f"{result['chunk_start']}",
                        "is_complete": result["is_complete_para"]
                    }
                })
            
            return formatted_response
        else:
            return {"error": "Failed to connect to the database"}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

@app.get("/clear_data")
async def clear_db():
    try:
        # Connect to the database
        dbconnection = my_utilities.connect_db()
        print(dbconnection)
        
        if dbconnection:
            # Clear data from database
            message = my_utilities.clear_db(dbconnection)
            return {"message": message}
        else:
            return {"error": "Failed to connect to the database"}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)