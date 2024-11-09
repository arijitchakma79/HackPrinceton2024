import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    PORT_NUMBER = os.getenv("PORT")
    DEBUG = os.getenv("DEBUG")
    OPENA_API_KEY = os.getenv("OPEN_API_SECRET_KEY")
    QDrantHost = os.getenv("QDRANT_HOST")
    QDrantPort = os.getenv("QDRANT_PORT")
    CollectionName = os.getenv("COLLECTION_NAME")
    EmbeddingModel = os.getenv("EMBEDDING_MODEL")
    LLM_model = os.getenv("LLM_MODEL") 