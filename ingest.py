import os
import logging
from dotenv import load_dotenv
from utils.notion_processor import NotionReader
from utils.file_processor import FileProcessor
from utils.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_data(clear_existing:bool=False) -> dict:
    results = {
        "total_documents": 0,
        "notion_documents": 0,
        "local_documents": 0
    }

    # Get configuration from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_root_page_id = os.getenv("NOTION_ROOT_PAGE_ID")
    local_files_dir = os.getenv("LOCAL_FILES_DIR")
    vector_db_dir = os.getenv("VECTOR_DB_DIR")

    # Validate required environment variables
    if not all([openai_api_key, vector_db_dir]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return results

    # Initialize vector store
    vector_store = VectorStore(vector_db_dir, openai_api_key)

    # Clear existing data if requested
    if clear_existing:
        vector_store.clear()
        logger.info("Vector store cleared.")

    all_texts = {}
    notion_texts_counter = 0
    local_texts_counter = 0

    # Process Notion pages if configured
    if notion_api_key and notion_root_page_id:
        logger.info("Processing Notion pages...")
        notion_reader = NotionReader(notion_api_key)
        notion_pages = notion_reader.get_all_pages_from_root(notion_root_page_id)

        # Add prefix to distinguish Notion sources
        notion_texts = {f"notion:{page_id}": content for page_id, content in notion_pages.items()}
        all_texts.update(notion_texts)

        logger.info(f"Processed {len(notion_texts)} Notion pages.")
        notion_texts_counter = len(notion_pages.items())

    # Process local files if configured
    if local_files_dir:
        logger.info("Processing local files...")
        file_processor = FileProcessor(local_files_dir)
        local_files = file_processor.process_all_files()

        # Add prefix to distinguish local file sources
        local_texts = {f"file:{file_path}": content for file_path, content in local_files.items()}
        all_texts.update(local_texts)
        local_texts_counter = len(local_files.items())

        logger.info(f"Processed {len(local_texts)} local files.")

    # Add all texts to vector store
    if all_texts:
        logger.info(f"Adding {len(all_texts)} documents to vector store...")
        vector_store.add_texts(all_texts)
        logger.info("Ingestion complete!")
        results = {
            "total_documents": len(all_texts),
            "notion_documents": notion_texts_counter,
            "local_documents": local_texts_counter
        }

        return results
    else:
        logger.warning("No documents were processed. Check your configuration.")
        return results


if __name__ == "__main__":
    load_dotenv()

    # Clear existing data (optional)
    should_clear = input("Clear existing vector store? (y/n): ").lower() == 'y'
    stats = ingest_data(clear_existing=should_clear)

    logger.info(f"Total documents ingested: {stats}")