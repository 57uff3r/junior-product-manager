import os
import logging
from typing import Dict, List, Optional
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str, openai_api_key: str):
        """Initialize the vector store with persistence directory."""
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        # Create the directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize or load the vector store
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
        )

    def add_texts(self, texts: Dict[str, str]) -> None:
        """Add texts to the vector store."""
        documents = []
        
        for source, content in texts.items():
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create documents
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": source,
                        "chunk": i
                    }
                )
                documents.append(doc)
        
        # Add documents to the vector store
        if documents:
            self.db.add_documents(documents)
            self.db.persist()
            logger.info(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for documents similar to the query."""
        return self.db.similarity_search(query, k=k)
    
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )
        self.db.persist()
        logger.info("Vector store cleared")