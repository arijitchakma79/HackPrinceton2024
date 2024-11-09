from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional
from qdrant_client.http.models import Filter, PointStruct

class QdrantDB:
    def __init__(self, collection_name: str):
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=models.Distance.COSINE
                )
            )

    def add_points(self, points: List[PointStruct]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: List[float], filter: Optional[Filter] = None, limit: int = 3):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter,
            limit=limit
        )

    def search_by_metadata(self, filter: Filter, limit: int = 100):
        return self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter,
            limit=limit
        )[0]

    def delete_points(self, points_selector: Filter):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=points_selector
        )