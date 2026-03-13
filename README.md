# FastAPI Escola
## Projeto de Extensão 2026/1

API FastAPI e dashboard para recebimento e analise de relatorios sobre jogos
## Estrutura
```
.
├── api
│   ├── config.py
│   ├── database.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routers
│   │   ├── client
│   │   ├── internal
│   ├── schemas.py
│   ├── scripts
│   │   ├── create_db.py
│   │   ├── populate_db.py
│   └── services
│       ├── alunos_services.py
│       ├── jogos_services.py
│       ├── sessoes_services.py
│       └── turmas_services.py
├── dashboard
│   ├── App.py
│   ├── pages
│   │   └── Turmas.py
│   └── services.py
├── db.sqlite3


```

## Rodar o projeto
1. Criar e ativar ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  
```

2. Instalar Dependências 
```
pip install -r requirements.txt
```
3. Criar banco de dados e (opcional) popular
```
python3 -m api.scripts.create_db
python3 -m api.scripts.populate_db
```
4. Crie .env e configure como em .env.example

5. Rodar a api
```
uvicorn api.main:app
```
6. Abrir o dashboard
```
streamlit run dashboard/streamlit.py
```
