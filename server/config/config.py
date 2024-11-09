import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    PORT_NUMBER = os.getenv("PORT")
    DEBUG = os.getenv("DEBUG")