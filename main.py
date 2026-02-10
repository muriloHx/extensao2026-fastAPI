from fastapi import FastAPI 

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

items = []
@app.post("/items")
def create_item(item: str):
    items.append(item)
    return items
    