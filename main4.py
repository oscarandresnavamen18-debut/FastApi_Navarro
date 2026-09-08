#Todos los metodos 

from fastapi import FastAPI, Query, Body

app = FastAPI(title="mini Blog")

BLOG_POTS = [
    {"id": 1, "title": "hola desde FastAPI",
        "content": "mi primer Post con FastAPI"},
    {"id": 2, "title": "Segundo post", "content": "mi segundo Post con FastAPI"},
    {"id": 3, "title": "tercer post",
        "content": " FastAPI es mas rapido por xxxxxxxxxx"}
]


@app.get("/") 
def home():
    
    return {"message": "Bienvenido a mi primer Blog"}



@app.get("/posts/{post_id}")
def get_post_content(post_id: int, include_content: bool = Query(default=True, description="Incluir el contenido del post")):
    for post in BLOG_POTS:
        if post["id"] == post_id:
            if not include_content:
                return {"datos": {"id": post["id"], "title": post["title"]}}
        return {"datos": post}
        
    return {"error": "Post no encontrado"}

#----------------
#Metodo Post
#----------------

