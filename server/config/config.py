import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT_NUMBER = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPEN_API_SECRET_KEY")
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "1000"))
    UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "60"))