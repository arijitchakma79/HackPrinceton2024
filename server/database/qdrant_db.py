from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config.config import Config


class QdrantDB:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(Config.QDrantHost, port=Config.QDrantPort)
        self.collection_name = collection_name
        self._create_collection()

    def _create_collection(self):
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size= 1536,
                    distance=Distance.COSINE
                )
            )
            print(f"Created new collection: {self.collection_name}")

    def add_points(self, points):
        return self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search(self, query_vector, limit: int = 3):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )