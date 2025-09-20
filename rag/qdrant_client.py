from dotenv import load_dotenv
import os
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
load_dotenv()


class QdrantManager:
    def __init__(self, collection_name: str = "chatbot_knowledge", recreate: bool = True):
        """
        Initialize Qdrant client and create collection on startup.
        Collection will be recreated fresh each time on startup, but during execution it will be kept the same.
        """
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        self.collection_name = collection_name

        if recreate:
            # Delete collection if it exists, then create fresh
            self._recreate_collection()

    def _recreate_collection(self):
        """Delete existing collection and create a new one."""
        try:
            # Try to delete existing collection
            self.client.delete_collection(collection_name=self.collection_name)
            logging.info(f"Deleted existing collection: {self.collection_name}")
        except Exception as e:
            logging.info(f"Collection {self.collection_name} didn't exist or couldn't be deleted: {e}")

        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.DOT),
        )
        logging.info(f"Created fresh collection: {self.collection_name}")

    def add_embeddings(self, embeddings: Dict[int, List[float]], metadata: Dict[str, Any]):
        """
        Add embeddings to the vector database.

        Args:
            embeddings: Dictionary with id as key and embedding vector as value
            metadata: Metadata to attach to all points (e.g., {"source": "document.pdf"})
        """
        points = []
        for point_id, embedding in embeddings.items():
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata
                )
            )

        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points,
        )
        logging.info(f"Added {len(points)} embeddings to collection")
        logging.info(operation_info)

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add documents with embeddings to the vector database.

        Args:
            documents: List of document dictionaries with content and metadata
            embeddings: List of embedding vectors corresponding to documents
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            points.append(
                PointStruct(
                    id=doc.get('id', i),
                    vector=embedding,
                    payload={
                        'content': doc.get('content', ''),
                        'source': doc.get('source', 'unknown'),
                        'metadata': doc.get('metadata', {})
                    }
                )
            )

        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points,
        )
        logging.info(f"Added {len(points)} documents to collection")
        logging.info(operation_info)

    def query(self, query_embedding: List[float], limit: int = 5):
        """
        Query the vector database for similar documents.

        Args:
            query_embedding: Embedding vector of the query
            limit: Maximum number of results to return

        Returns:
            List of similar documents with scores and metadata
        """
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            with_payload=True,
            with_vectors=True,
            limit=limit
        ).points

        return search_result

    def search_documents(self, query_embedding: List[float], limit: int = 5, score_threshold: Optional[float] = None):
        """
        Search for similar documents with optional score filtering.

        Args:
            query_embedding: Embedding vector of the query
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold

        Returns:
            List of search results with formatted output
        """
        results = self.query(query_embedding, limit)

        formatted_results = []
        for result in results:
            if score_threshold is None or result.score >= score_threshold:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'content': result.payload.get('content', ''),
                    'source': result.payload.get('source', 'unknown'),
                    'metadata': result.payload.get('metadata', {})
                })

        return formatted_results

    def clear_db(self):
        """Delete the collection and clean up."""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logging.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logging.error(f"Failed to delete collection: {e}")

    def get_collection_info(self):
        """Get information about the current collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            logging.info(f"Collection info: {info}")
            return info
        except Exception as e:
            logging.error(f"Failed to get collection info: {e}")
            return None