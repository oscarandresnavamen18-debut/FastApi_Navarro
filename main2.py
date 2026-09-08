# usando metodos get
from fastapi import FastAPI

app = FastAPI(title="mini blog")

BLOG_POST = [
    {"id": 1, "tile":"hola desde fastAPI", "content": "mi primer post con FastAPI"},
    {"id": 2, "tile":"segundo Post", "content": "mi segundo post con FastAPI"},
    {"id": 3, "tile":"Tercer Post", "content": "FastAPI es mas rapido por xxxxxxxxxxx"}
]

@app.get("/")

def home():
    return {'mensaje':'Bienvenidos a mi blog elian martinez'}

@app.get("/posts")
def list_post():
    return {"datos": BLOG_POST}