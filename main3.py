# Query Params
#lo vamos a distinguir con ?identificador= 
from fastapi import FastAPI, Query

app = FastAPI(title= "mini Blog")

BLOG_POTS = [
    {"id": 1, "title": "hola desde FastAPI", "content": "mi primer Post con FastAPI"},
    {"id": 2, "title": "Segundo post", "content": "mi segundo Post con FastAPI"},
    {"id": 3, "title": "tercer post", "content": " FastAPI es mas rapido por xxxxxxxxxx"}
]

@app.get("/")#esta es la ruta principal - raiz
def home():
    return {"message": "Bienvenido a mi primer Blog"} #como respuesta de la ruta principal, se devuelve un diccionario con un mensaje de bienvenida.

# ejecutar fastApi dev main.py




# @app.get("/posts")
# def list_posts(query: str | None = Query(default=None, description="Texto para buscar por titulo")):
#     if query:
#         result = []#creamos una lista
#         for post in BLOG_POTS: #iteramos el BLOG_POST
#             #buscamos por titulo
#             if query.lower() in post["title"].lower(): #si el query esta en el titulo del post
#                 result.append(post) #agregamos el post a la lista
#         return{"datos": result, "query": query} #devolvemos la lista de resultados

@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Texto para buscar por titulo")):
    if query:
        results = [post for post in BLOG_POTS if query.lower() in post ["title"].lower()]
        return{"datos":results, "query":query}
    return {"datos":BLOG_POTS}