# FastAPI Escola

API simples para gerenciamento de turmas, jogos e sessões.
## Estrutura
```
├── api
│   ├── config.py
│   ├── database.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── __pycache__
│   ├── routers
│   ├── schemas.py
│   └── services
├── dashboard
│   ├── .streamlit
│   └── streamlit.py
├── db.sqlite3
├── .env
├── scripts
│   ├── create_db.py
│   └── populate_db.py

```

##Rodar o projeto
1. Criar e ativar ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

2. Instalar Dependências 
```
pip install -r requirements.txt
```
3. Criar banco de dados e (opcional) popular
```
python scripts/create_db.py
python scripts/populate_db.py
```
4. Crie .env e configure como em .env.example
```
#.env file
API_KEY=""
DATABASE_URL="sqlite:///./db.sqlite3"
```
5. Rodar fastapi com
```
uvicorn api.main:app --reload
```
6. Abrir o dashboard
```
streamlit run dashboard/streamlit.py
```
Documentação automática do FastAPI disponivel em localhost:8000/docs




