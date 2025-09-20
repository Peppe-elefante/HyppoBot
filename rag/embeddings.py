from typing import List, Dict, Any, Optional
import logging
from fastembed import TextEmbedding
import re
import uuid

logger = logging.getLogger(__name__)


class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the FastEmbed model to use
        """
        self.model = TextEmbedding(model_name=model_name)
        self.model_name = model_name
        logger.info(f"Initialized embedding model: {model_name}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = list(self.model.embed([text]))[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = list(self.model.embed(texts))
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        return self.embed_text(query)


class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor for chunking and preparing documents.

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        text = self.clean_text(text)

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundaries
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break

        return chunks

    def process_document(self, content: str, source: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Process a document into chunks with metadata.

        Args:
            content: Document content
            source: Source identifier (e.g., filename, URL)
            metadata: Additional metadata

        Returns:
            List of document chunks with metadata
        """
        chunks = self.chunk_text(content)
        documents = []

        base_metadata = metadata or {}

        for i, chunk in enumerate(chunks):
            point_id = str(uuid.uuid4())
            doc = {
                'id': point_id,
                'content': chunk,
                'source': source,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'metadata': {
                    **base_metadata,
                    'chunk_size': len(chunk)
                }
            }
            documents.append(doc)

        return documents

    def process_multiple_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents.

        Args:
            documents: List of documents with 'content', 'source', and optional 'metadata'

        Returns:
            List of processed document chunks
        """
        all_chunks = []

        for doc in documents:
            content = doc['content']
            source = doc['source']
            metadata = doc.get('metadata', {})

            chunks = self.process_document(content, source, metadata)
            all_chunks.extend(chunks)

        logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks


class DataIngestion:
    def __init__(self, qdrant_manager, embedding_manager: Optional[EmbeddingManager] = None):
        """
        Initialize data ingestion pipeline.

        Args:
            qdrant_manager: QdrantManager instance
            embedding_manager: EmbeddingManager instance
        """
        self.qdrant_manager = qdrant_manager
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.processor = DocumentProcessor()

    def ingest_documents(self, documents: List[Dict[str, str]]):
        """
        Complete pipeline to ingest documents into vector database.

        Args:
            documents: List of documents with 'content', 'source', and optional 'metadata'
        """
        logger.info(f"Starting ingestion of {len(documents)} documents")

        # Process documents into chunks
        processed_docs = self.processor.process_multiple_documents(documents)

        # Generate embeddings
        contents = [doc['content'] for doc in processed_docs]
        embeddings = self.embedding_manager.embed_texts(contents)

        # Add to vector database
        self.qdrant_manager.add_documents(processed_docs, embeddings)

        logger.info(f"Successfully ingested {len(processed_docs)} document chunks")

    def ingest_text_files(self, file_paths: List[str]):
        """
        Ingest text files from file paths.

        Args:
            file_paths: List of file paths to ingest
        """
        documents = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                documents.append({
                    'content': content,
                    'source': file_path,
                    'metadata': {
                        'file_type': 'text',
                        'file_path': file_path
                    }
                })
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")

        if documents:
            self.ingest_documents(documents)