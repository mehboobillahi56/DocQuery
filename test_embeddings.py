from utils import MyUtilityFunctions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embeddings():
    utils = MyUtilityFunctions()
    
    # Test data
    test_texts = [
        "This is a test sentence about artificial intelligence.",
        "Machine learning is transforming the world.",
        "Natural language processing helps computers understand human language.",
        "Deep learning models can recognize patterns in data."
    ]
    
    logger.info(f"Processing {len(test_texts)} test sentences")
    
    # Get embeddings
    embeddings = utils.get_embeddings(test_texts)
    logger.info(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Connect to database
    connection = utils.connect_db()
    if not connection:
        logger.error("Failed to connect to database")
        return
    
    logger.info("Connected to database")
    
    # Store embeddings
    utils.store_embeddings(connection, test_texts, embeddings)
    
    # Test retrieval
    test_query = "What is AI and machine learning?"
    logger.info(f"Testing retrieval with query: {test_query}")
    
    results = utils.get_results(connection, test_query)
    logger.info(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        logger.info(f"{i}. Text: {result['text']}")
        logger.info(f"   Similarity: {result['similarity']:.4f}")
    
    connection.close()
    logger.info("Test completed")

if __name__ == "__main__":
    test_embeddings()
