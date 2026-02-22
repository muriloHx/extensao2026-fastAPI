import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao definido")

if not os.path.exists("./db.sqlite3"):
    raise RuntimeError("Banco de dados nao encontrado")

if not API_KEY:
    raise ValueError("API_KEY nao definido")
