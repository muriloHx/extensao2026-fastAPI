import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao definido")

if not os.path.exists("./db.sqlite3"):
    raise RuntimeError("arquivo do banco de dados nao encontrado")

if not CLIENT_API_KEY:
    raise ValueError("API_KEY client nao definida")

if not INTERNAL_API_KEY:
    raise ValueError("API_KEY interna não definida")
