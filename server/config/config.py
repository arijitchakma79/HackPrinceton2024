import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    PORT_NUMBER = os.getenv("PORT")
    DEBUG = os.getenv("DEBUG")
    OPENA_API_KEY = os.getenv("OPEN_API_SECRET_KEY")
    QDrantHost = os.getenv("QDRANT_HOST")
    QDrantPort = os.getenv("QDRANT_PORT")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    LLM_MODEL = os.getenv("LLM_MODEL") 