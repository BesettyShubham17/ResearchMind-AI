import logging
from typing import List, Optional
from app.config.settings import settings

logger = logging.getLogger("researchmind.pinecone")

class PineconeService:
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        if self.api_key:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=self.api_key)
                self.index = pc.Index(self.index_name)
                logger.info("Pinecone connected successfully.")
            except Exception as e:
                logger.warning(f"Pinecone init failed: {e}")

    def upsert_documents(self, documents: list, project_id: str):
        """Embed and store documents in Pinecone."""
        if not self.index:
            logger.warning("Pinecone not configured, skipping upsert.")
            return
        from app.services.openai_service import openai_service
        vectors = []
        for i, doc in enumerate(documents):
            text = f"{doc.get('title', '')} {doc.get('content', '')}".strip()
            embedding = openai_service.get_embedding(text)
            if embedding:
                vectors.append({
                    "id": f"{project_id}-{i}",
                    "values": embedding,
                    "metadata": {
                        "project_id": project_id,
                        "title": doc.get("title", ""),
                        "url": doc.get("url", ""),
                        "content": text[:1000],
                    }
                })
        if vectors:
            try:
                self.index.upsert(vectors=vectors, namespace=project_id)
                logger.info(f"Upserted {len(vectors)} vectors for project {project_id}")
            except Exception as e:
                logger.error(f"Pinecone upsert error: {e}")

    def similarity_search(self, query: str, project_id: str, top_k: int = 5) -> list:
        """Search for similar documents by query embedding."""
        if not self.index:
            return []
        from app.services.openai_service import openai_service
        embedding = openai_service.get_embedding(query)
        if not embedding:
            return []
        try:
            result = self.index.query(
                vector=embedding,
                top_k=top_k,
                namespace=project_id,
                include_metadata=True,
            )
            return [match.metadata for match in result.matches]
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            return []

pinecone_service = PineconeService()
