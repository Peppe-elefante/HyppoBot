from typing import List, Dict, Any, Optional
import logging
from .embeddings import EmbeddingManager

logger = logging.getLogger(__name__)


class DocumentRetriever:
    def __init__(self, qdrant_manager, embedding_manager: Optional[EmbeddingManager] = None):
        """
        Initialize document retriever.

        Args:
            qdrant_manager: QdrantManager instance
            embedding_manager: EmbeddingManager instance for query embeddings
        """
        self.qdrant_manager = qdrant_manager
        self.embedding_manager = embedding_manager or EmbeddingManager()

    def search(self,
               query: str,
               limit: int = 5,
               score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on a text query.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold

        Returns:
            List of relevant documents with scores and metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedding_manager.embed_query(query)

            # Search in vector database
            results = self.qdrant_manager.search_documents(
                query_embedding=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )

            logger.info(f"Found {len(results)} relevant documents for query: '{query[:50]}...'")
            return results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise

    def get_context(self,
                    query: str,
                    limit: int = 3,
                    score_threshold: Optional[float] = 0.3) -> str:
        """
        Retrieve and format context for RAG generation.

        Args:
            query: Search query
            limit: Maximum number of documents to retrieve
            score_threshold: Minimum similarity score

        Returns:
            Formatted context string for LLM
        """
        results = self.search(query, limit, score_threshold)

        if not results:
            return "No relevant context found."

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"Context {i} (Score: {result['score']:.3f}, Source: {result['source']}):\n"
                f"{result['content']}\n"
            )

        context = "\n".join(context_parts)
        logger.info(f"Generated context with {len(results)} documents for query")
        return context

    def get_sources(self, query: str, limit: int = 5) -> List[str]:
        """
        Get unique sources that are relevant to the query.

        Args:
            query: Search query
            limit: Maximum number of results to search

        Returns:
            List of unique source identifiers
        """
        results = self.search(query, limit)
        sources = list(set(result['source'] for result in results))
        return sources

    def search_by_source(self,
                        query: str,
                        source_filter: str,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents from a specific source.

        Args:
            query: Search query
            source_filter: Source to filter by
            limit: Maximum number of results

        Returns:
            List of relevant documents from the specified source
        """
        all_results = self.search(query, limit * 2)  # Get more results to filter
        filtered_results = [
            result for result in all_results
            if result['source'] == source_filter
        ]
        return filtered_results[:limit]


class AdvancedRetriever(DocumentRetriever):
    """Extended retriever with additional search strategies."""

    def hybrid_search(self,
                     query: str,
                     keywords: List[str] = None,
                     limit: int = 5) -> List[Dict[str, Any]]:
        """
        Combine vector search with keyword-based filtering.

        Args:
            query: Main search query
            keywords: Additional keywords that must be present
            limit: Maximum number of results

        Returns:
            List of documents matching both vector similarity and keywords
        """
        # Get initial vector search results
        vector_results = self.search(query, limit * 2)

        if not keywords:
            return vector_results[:limit]

        # Filter by keywords
        filtered_results = []
        for result in vector_results:
            content_lower = result['content'].lower()
            if all(keyword.lower() in content_lower for keyword in keywords):
                filtered_results.append(result)

        logger.info(f"Hybrid search found {len(filtered_results)} documents with keywords {keywords}")
        return filtered_results[:limit]

    def multi_query_search(self,
                          queries: List[str],
                          limit: int = 5,
                          deduplicate: bool = True) -> List[Dict[str, Any]]:
        """
        Search using multiple queries and combine results.

        Args:
            queries: List of search queries
            limit: Maximum total results
            deduplicate: Whether to remove duplicate documents

        Returns:
            Combined search results from all queries
        """
        all_results = []
        seen_ids = set()

        for query in queries:
            results = self.search(query, limit)

            for result in results:
                if deduplicate:
                    if result['id'] not in seen_ids:
                        all_results.append(result)
                        seen_ids.add(result['id'])
                else:
                    all_results.append(result)

        # Sort by score descending
        all_results.sort(key=lambda x: x['score'], reverse=True)

        logger.info(f"Multi-query search with {len(queries)} queries found {len(all_results)} unique documents")
        return all_results[:limit]

    def contextual_search(self,
                         conversation_history: List[str],
                         current_query: str,
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search considering conversation context.

        Args:
            conversation_history: Previous messages in conversation
            current_query: Current user query
            limit: Maximum number of results

        Returns:
            Contextually relevant documents
        """
        # Combine recent conversation for context
        context = " ".join(conversation_history[-3:])  # Last 3 messages
        enhanced_query = f"{context} {current_query}"

        # Search with enhanced query
        results = self.search(enhanced_query, limit)

        logger.info(f"Contextual search using conversation history found {len(results)} documents")
        return results