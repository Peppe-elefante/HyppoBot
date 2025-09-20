from typing import List, Dict, Any, Optional
import logging
from .qdrant_client import QdrantManager
from .embeddings import EmbeddingManager, DataIngestion
from .retrieval import DocumentRetriever, AdvancedRetriever
from rag.utils import extract_text_files
logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self,
                collection_name: str = "chatbot_knowledge",
                embedding_model: str = "BAAI/bge-small-en-v1.5",
                recreate_collection: bool = True,
                use_advanced_retrieval: bool = False):
        """
        Initialize the complete RAG pipeline.

        Args:
            collection_name: Qdrant collection name
            embedding_model: FastEmbed model name
            use_advanced_retrieval: Whether to use advanced retrieval features
        """
        self.collection_name = collection_name

        # Initialize components
        self.qdrant_manager = QdrantManager(collection_name, recreate_collection)
        self.embedding_manager = EmbeddingManager(embedding_model)
        self.data_ingestion = DataIngestion(self.qdrant_manager, self.embedding_manager)

        # Initialize retriever
        if use_advanced_retrieval:
            self.retriever = AdvancedRetriever(self.qdrant_manager, self.embedding_manager)
        else:
            self.retriever = DocumentRetriever(self.qdrant_manager, self.embedding_manager)

        logger.info(f"RAG Pipeline initialized with collection: {collection_name}")

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the knowledge base.

        Args:
            documents: List of documents with 'content', 'source', and optional 'metadata'
        """
        self.data_ingestion.ingest_documents(documents)

    def add_text_files(self, directory: str):
        """
        Add text files to the knowledge base.

        Args:
            file_paths: List of file paths to ingest
        """
        file_paths = extract_text_files(directory)
        
        self.data_ingestion.ingest_text_files(file_paths)

    def search(self,
               query: str,
               limit: int = 5,
               score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents
        """
        return self.retriever.search(query, limit, score_threshold)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            info = self.qdrant_manager.get_collection_info()
            return {
                'collection_name': self.collection_name,
                'total_documents': info.points_count if info else 0,
                'vector_size': info.config.params.vectors.size if info else 0,
                'distance_metric': info.config.params.vectors.distance if info else 'unknown'
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}

    def cleanup(self):
        """Clean up resources and delete the collection."""
        try:
            self.qdrant_manager.clear_db()
            logger.info("RAG Pipeline cleaned up successfully")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup on exit."""
        self.cleanup()


