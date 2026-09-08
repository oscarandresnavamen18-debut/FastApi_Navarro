
# todos los metodos
from fastapi import FastAPI, Query, Body, HTTPException


app = FastAPI(title="mini Blog")

BLOG_POST = [
    {'id': 1, 'titulo': 'Hola desde fastApi',
        'contenido': 'mi primer post con fastApi'},
    {'id': 2, 'titulo': 'segundo post', 'contenido': 'mi segundo post con fastApi'},
    {'id': 3, 'titulo': 'django vs FastApi',
        'contenido': 'fastApi es mas rapido por xxxxx'},
]


@app.get("/")  # esta es la ruta principal o la ruta raiz
def home():
    return {'mensaje': 'Bienvenidos  a mi blog edison suares'}


@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="texto para buscar por titulo")):
    if query:
        results = [post for post in BLOG_POST if query.lower()
            in post["titulo"].lower()]
        
        return {"datos": results, "query": query}
    return {"datos": BLOG_POST}

# @app.get("/posts/{post_id}") # este es el path parameters
# def get_post(post_id: int):
#     for post in BLOG_POST:
#         if post['id'] == post_id:
#             return{"datos": post}
#     return{"error": "Post no Encontrado"}


@app.get("/posts/{post_id}")
def list_posts(post_id: int, include_content: bool = Query(default=True, description="incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not include_content:
                return {"id": post['id'], "titulo": post['titulo']}
            return {"datos": post}

    # return{"error": "post no encontrado con query y path params"}
    raise HTTPException(status_code=404, detail="no se encontro el post")

# -----------------------
# metodo post
# -----------------------


@app.post("/posts")
def crearte_post(post: dict = Body(...)):

    if "titulo" not in post or "content" not in post:
        return {"error": "titulo y con content son obligatorio"}

    if not str(post["titulo"]).strip():
        return {"error": "el titulo no puede estar vacio"}

    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    new_post = {"id": new_id,
                "titulo": post["titulo"], "content": post["content"]}

    BLOG_POST.append(new_post)

    return {"mensaje": "post creado con exito", "data": new_post}

# -----------------------
# metodo put
# -----------------------


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if "titulo" in data:
                post["titulo"] = data["titulo"]

            if "content" in data:
                post["content"] = data["content"]

            return {"message": "post actualizado", "data": post}

    # return{"error": "post no encontrado"}
    # raise para personalizar el error

    raise HTTPException(status_code=404, detail="no se encontro el post")


# metododili

@app.delete("/post/{post_id}",status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
    return


    raise HTTPException(
        status_code=404, detail="post no encontrado para eliminar")
