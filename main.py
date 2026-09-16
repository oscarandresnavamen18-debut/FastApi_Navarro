# Mini Blog v2 - FastAPI
# Validaciones avanzadas y modelos en FastAPI
# + Guía 2: Path Parameters y Query Parameters

from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal


app = FastAPI(title="Mini Blog v2", version="1.0.0")

TAG_POSTS = ["Posts"]
TAG_SISTEMA = ["Sistema"]


BLOG_POST: List[dict] = [
    {
        "id": 1,
        "titulo": "Hola desde FastAPI",
        "contenido": "Mi primer post con FastAPI",
        "autor": {"nombre": "Edison Suarez", "email": "edison@example.com"},
        "estado": "borrador",
        "comentarios": [],
    },
    {
        "id": 2,
        "titulo": "Segundo post",
        "contenido": "Mi segundo post con FastAPI",
        "autor": {"nombre": "Edison Suarez", "email": "edison@example.com"},
        "estado": "borrador",
        "comentarios": [],
    },
    {
        "id": 3,
        "titulo": "Django vs FastAPI",
        "contenido": "FastAPI es más rápido por xxxxx",
        "autor": {"nombre": "Edison Suarez", "email": "edison@example.com"},
        "estado": "borrador",
        "comentarios": [],
    },
]


class Autor(BaseModel):
    nombre: str
    email: str

    @field_validator("email")
    @classmethod
    def email_valido(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("El email del autor no es válido")
        return value


class Comentario(BaseModel):
    id: int
    contenido: str
    autor: str


class ComentarioCreate(BaseModel):
    contenido: str
    autor: str


class PostCreate(BaseModel):
    titulo: str = Field(..., min_length=1, description="Título del post")
    contenido: str
    autor: Autor

    @field_validator("titulo")
    @classmethod
    def title_sin_espacios_extra(cls, value: str) -> str:
        limpio = value.strip()
        if not limpio:
            raise ValueError("El título no puede estar vacío ni contener solo espacios")
        return limpio

    @model_validator(mode="after")
    def titulo_distinto_de_contenido(self):
        if self.titulo.strip().lower() == self.contenido.strip().lower():
            raise ValueError("El título no puede ser igual al contenido")
        return self


class PostUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None

    @field_validator("titulo")
    @classmethod
    def title_sin_espacios_extra(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        limpio = value.strip()
        if not limpio:
            raise ValueError("El título no puede estar vacío ni contener solo espacios")
        return limpio


class AutorPublico(BaseModel):
    nombre: str


class PostPublicoOut(BaseModel):
    id: int
    titulo: str
    contenido: str
    autor: AutorPublico
    estado: str
    comentarios: List[Comentario] = []


@app.get("/", tags=TAG_SISTEMA, summary="Mensaje de bienvenida")
def home():
    return {"mensaje": "Bienvenidos a mi blog Edison Suares"}


@app.get(
    "/posts",
    response_model=List[PostPublicoOut],
    summary="Listar posts del blog",
    description="Devuelve los posts, con soporte de búsqueda, orden y paginación.",
    response_description="Lista de posts que cumplen los filtros solicitados",
    tags=TAG_POSTS,
)
def list_posts(
    query: str | None = Query(default=None, min_length=2, max_length=50, description="Texto para buscar por título"),
    skip: int = Query(default=0, ge=0, description="Cuántos posts saltar desde el inicio"),
    limit: int = Query(default=10, ge=1, le=50, description="Cuántos posts devolver como máximo"),
    order_by: Literal["id", "titulo"] = Query(default="id", description="Campo por el cual ordenar"),
    order: Literal["asc", "desc"] = Query(default="asc", description="Dirección del orden"),
):
    resultados = BLOG_POST
    if query:
        resultados = [post for post in resultados if query.lower() in post["titulo"].lower()]
    resultados = sorted(resultados, key=lambda post: post[order_by], reverse=(order == "desc"))
    return resultados[skip: skip + limit]


@app.get("/posts/buscar", summary="Buscar varios posts por id", tags=TAG_POSTS)
def buscar_posts_por_id(id: list[int] = Query(default=[], description="Puede repetirse: ?id=1&id=3")):
    if not id:
        return {"datos": []}
    return {"datos": [post for post in BLOG_POST if post["id"] in id]}


@app.get(
    "/posts/buscar-avanzado",
    summary="Búsqueda avanzada de posts",
    description="Combina búsqueda por texto, filtro por ids, orden y paginación.",
    response_description="Lista de posts que cumplen los filtros, ya ordenada y paginada",
    tags=TAG_POSTS,
)
def buscar_avanzado(
    query: str | None = Query(default=None, min_length=2, max_length=50, description="Texto para buscar por título"),
    buscar: str | None = Query(default=None, deprecated=True, description="OBSOLETO: usa 'query'"),
    ids: list[int] = Query(default=[], description="Lista de ids para filtrar (puede repetirse: ?ids=1&ids=2)"),
    order_by: Literal["id", "titulo"] = Query(default="id", description="Campo por el cual ordenar"),
    order: Literal["asc", "desc"] = Query(default="asc", description="Dirección del orden"),
    skip: int = Query(default=0, ge=0, description="Cuántos posts saltar desde el inicio"),
    limit: int = Query(default=10, ge=1, le=50, description="Cuántos posts devolver como máximo"),
):
    texto_busqueda = query if query is not None else buscar
    resultados = BLOG_POST
    if texto_busqueda:
        resultados = [post for post in resultados if texto_busqueda.lower() in post["titulo"].lower()]
    if ids:
        resultados = [post for post in resultados if post["id"] in ids]
    total_sin_paginar = len(resultados)
    resultados = sorted(resultados, key=lambda post: post[order_by], reverse=(order == "desc"))
    paginados = resultados[skip: skip + limit]
    return {"datos": paginados, "total_sin_paginar": total_sin_paginar, "skip": skip, "limit": limit}


@app.get("/posts/destacado", tags=TAG_POSTS, summary="Post destacado")
def post_destacado():
    if not BLOG_POST:
        return {"error": "No hay posts todavía"}
    return {"destacado": BLOG_POST[0]}


@app.get("/posts/vacios", tags=TAG_POSTS, summary="Verificar si hay posts")
def posts_vacios():
    if not BLOG_POST:
        return {"total": 0}
    return {"total": len(BLOG_POST)}


@app.get(
    "/posts/{post_id}",
    summary="Consultar un post por id",
    response_description="Datos del post solicitado",
    tags=TAG_POSTS,
)
def get_post(
    post_id: int = Path(gt=0, description="ID del post a consultar"),
    incluir_contenido: bool = Query(default=True, description="Incluir o no el contenido"),
    include_content: bool | None = Query(default=None, deprecated=True, description="OBSOLETO: usa 'incluir_contenido' en su lugar"),
):
    valor_final = include_content if include_content is not None else incluir_contenido
    for post in BLOG_POST:
        if post["id"] == post_id:
            if not valor_final:
                return {"id": post["id"], "titulo": post["titulo"]}
            return PostPublicoOut(**post)
    raise HTTPException(status_code=404, detail="No se encontró el post")


@app.post("/posts", status_code=201, summary="Crear un post nuevo", response_description="El post recién creado", tags=TAG_POSTS)
def create_post(post: PostCreate):
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
    new_post = {
        "id": new_id,
        "titulo": post.titulo,
        "contenido": post.contenido,
        "autor": post.autor.model_dump(),
        "estado": "borrador",
        "comentarios": [],
    }
    BLOG_POST.append(new_post)
    return {"mensaje": "Post creado con éxito", "data": new_post}


@app.put("/posts/{post_id}", summary="Actualizar un post", response_description="El post ya actualizado", tags=TAG_POSTS)
def update_post(post_id: int = Path(gt=0, description="ID del post a actualizar"), data: PostUpdate = None):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "titulo" in payload:
                post["titulo"] = payload["titulo"]
            if "contenido" in payload:
                post["contenido"] = payload["contenido"]
            return {"mensaje": "Post actualizado", "data": post}
    raise HTTPException(status_code=404, detail="No se encontró el post")


@app.delete("/posts/{post_id}", status_code=204, summary="Eliminar un post", tags=TAG_POSTS)
def delete_post(post_id: int = Path(gt=0, description="ID del post a eliminar")):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail="Post no encontrado para eliminar")


@app.post("/posts/{post_id}/comentarios", status_code=201, summary="Agregar un comentario a un post", response_description="El comentario recién agregado", tags=TAG_POSTS)
def add_comentario(post_id: int = Path(gt=0, description="ID del post a comentar"), comentario: ComentarioCreate = None):
    for post in BLOG_POST:
        if post["id"] == post_id:
            new_comment_id = (post["comentarios"][-1]["id"] + 1) if post["comentarios"] else 1
            nuevo_comentario = {"id": new_comment_id, "contenido": comentario.contenido, "autor": comentario.autor}
            post["comentarios"].append(nuevo_comentario)
            return {"mensaje": "Comentario agregado", "data": nuevo_comentario}
    raise HTTPException(status_code=404, detail="No se encontró el post")


@app.patch("/posts/{post_id}/publicar", summary="Publicar un post", response_description="El post ya publicado", tags=TAG_POSTS)
def publicar_post(post_id: int = Path(gt=0, description="ID del post a publicar")):
    for post in BLOG_POST:
        if post["id"] == post_id:
            post["estado"] = "publicado"
            return {"mensaje": "Post publicado", "data": post}
    raise HTTPException(status_code=404, detail="No se encontró el post")