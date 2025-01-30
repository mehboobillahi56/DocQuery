import gradio as gr
import requests
import os

# API Endpoints
BASE_URL = "http://localhost:8080"  # Base URL without /docs
EMBEDDING_API = f"{BASE_URL}/store_text_embeddings"
QUERY_API = f"{BASE_URL}/text_matching"
CLEAR_API = f"{BASE_URL}/clear_data"

# Define Functions
def process_document(file):
    if file is None:
        return "Please upload a file first!"
    
    print(f"Processing file: {file.name}")
    print(f"File object type: {type(file)}")
    print(f"File size: {os.path.getsize(file.name) if os.path.exists(file.name) else 'File not found'}")
    
    try:
        # Directly send the file object that Gradio provides
        files = {"doc": (os.path.basename(file.name), open(file.name, 'rb'), "application/octet-stream")}
        print(f"Sending file to API: {os.path.basename(file.name)}")
        
        response = requests.post(EMBEDDING_API, files=files)
        print(f"API Response status: {response.status_code}")
        print(f"API Response content: {response.text}")
        
        if response.status_code == 200:
            return "Document embedded successfully!"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        print(f"Error in process_document: {str(e)}")
        return f"Error occurred: {str(e)}"
    finally:
        # Close the file if it was opened
        if 'files' in locals() and hasattr(files['doc'][1], 'close'):
            files['doc'][1].close()

def query_text_matching(query):
    try:
        response = requests.get(f"{QUERY_API}", params={"text": query})
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

def clear_database():
    response = requests.get(CLEAR_API)
    if response.status_code == 200:
        return "Database cleared successfully!"
    else:
        return f"Error: {response.text}"

# Create Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Document Embedding and Query App")

    # Embedding Section
    with gr.Tab("Upload Document"):
        file = gr.File(label="Upload your document (txt, pdf, etc.)")
        upload_button = gr.Button("Process Document")
        upload_result = gr.Textbox()
        upload_button.click(process_document, inputs=file, outputs=upload_result)

    # Query Section
    with gr.Tab("Query Text"):
        query_input = gr.Textbox(label="Enter your query")
        query_button = gr.Button("Submit Query")
        query_result = gr.Textbox()
        query_button.click(query_text_matching, inputs=query_input, outputs=query_result)

    # Clear Database Section
    with gr.Tab("Clear Database"):
        clear_button = gr.Button("Clear Database")
        clear_result = gr.Textbox()
        clear_button.click(clear_database, outputs=clear_result)

# Launch the Interface
demo.launch()