import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

if not os.path.exists(DATABASE_URL):
    raise RuntimeError("Banco de dados não encontrado")

if not API_KEY:
    raise ValueError("API_KEY is not set")
