# Mini Blog v2 - FastAPI
# Validaciones avanzadas y modelos en FastAPI

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List


app = FastAPI(title="Mini Blog v2")


# -----------------------
# Almacenamiento en memoria
# -----------------------

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


# =========================================================
# MÓDULO 1: Field y validaciones avanzadas
# =========================================================
# Caso: título vacío o solo espacios -> debe devolver 422

class Autor(BaseModel):
    nombre: str
    email: str

    # -----------------------
    # MÓDULO 2: Validaciones personalizadas
    # -----------------------
    # Caso: email sin '@' -> 422
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


# -----------------------
# MÓDULO 4: Modelos anidados
# -----------------------
# El post incluye un objeto Autor completo (nombre + email),
# un estado por defecto "borrador" y una lista de comentarios.

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

    # MÓDULO 2: título igual al contenido -> 422
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


# =========================================================
# MÓDULO 3: Modelos de respuesta
# =========================================================
# El email del autor nunca se expone en las respuestas públicas.

class AutorPublico(BaseModel):
    nombre: str


class PostPublicoOut(BaseModel):
    id: int
    titulo: str
    contenido: str
    autor: AutorPublico
    estado: str
    comentarios: List[Comentario] = []


# -----------------------
# Método GET - Ruta principal
# -----------------------

@app.get("/")
def home():
    return {
        "mensaje": "Bienvenidos a mi blog Edison Suares"
    }


# -----------------------
# Método GET - Listar posts (modelo de respuesta público)
# -----------------------

@app.get("/posts", response_model=List[PostPublicoOut])
def list_posts(
    query: str | None = Query(
        default=None,
        description="Texto para buscar por título"
    )
):
    if query:
        return [
            post
            for post in BLOG_POST
            if query.lower() in post["titulo"].lower()
        ]

    return BLOG_POST


# -----------------------
# Método GET - Obtener un post
# -----------------------

@app.get("/posts/{post_id}")
def get_post(
    post_id: int,
    include_content: bool = Query(
        default=True,
        description="Incluir o no el contenido"
    )
):
    for post in BLOG_POST:

        if post["id"] == post_id:

            if not include_content:
                return {
                    "id": post["id"],
                    "titulo": post["titulo"]
                }

            return PostPublicoOut(**post)

    raise HTTPException(
        status_code=404,
        detail="No se encontró el post"
    )


# -----------------------
# Método POST - Crear post (con autor anidado)
# -----------------------

@app.post("/posts", status_code=201)
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

    return {
        "mensaje": "Post creado con éxito",
        "data": new_post
    }


# -----------------------
# Método PUT - Actualizar post
# -----------------------

@app.put("/posts/{post_id}")
def update_post(
    post_id: int,
    data: PostUpdate
):
    for post in BLOG_POST:

        if post["id"] == post_id:

            payload = data.model_dump(exclude_unset=True)

            if "titulo" in payload:
                post["titulo"] = payload["titulo"]

            if "contenido" in payload:
                post["contenido"] = payload["contenido"]

            return {
                "mensaje": "Post actualizado",
                "data": post
            }

    raise HTTPException(
        status_code=404,
        detail="No se encontró el post"
    )


# -----------------------
# Método DELETE - Eliminar post
# -----------------------

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):

    for index, post in enumerate(BLOG_POST):

        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return

    raise HTTPException(
        status_code=404,
        detail="Post no encontrado para eliminar"
    )


# =========================================================
# MÓDULO 2 (continuación): endpoint anidado de comentarios
# =========================================================
# Caso: agregar comentario -> POST /posts/{post_id}/comentarios -> 201

@app.post("/posts/{post_id}/comentarios", status_code=201)
def add_comentario(post_id: int, comentario: ComentarioCreate):

    for post in BLOG_POST:

        if post["id"] == post_id:

            new_comment_id = (
                (post["comentarios"][-1]["id"] + 1)
                if post["comentarios"] else 1
            )

            nuevo_comentario = {
                "id": new_comment_id,
                "contenido": comentario.contenido,
                "autor": comentario.autor,
            }

            post["comentarios"].append(nuevo_comentario)

            return {
                "mensaje": "Comentario agregado",
                "data": nuevo_comentario
            }

    raise HTTPException(
        status_code=404,
        detail="No se encontró el post"
    )


# -----------------------
# Método PATCH - Publicar post
# -----------------------
# Caso: cambiar estado a "publicado" -> 200

@app.patch("/posts/{post_id}/publicar")
def publicar_post(post_id: int):

    for post in BLOG_POST:

        if post["id"] == post_id:
            post["estado"] = "publicado"

            return {
                "mensaje": "Post publicado",
                "data": post
            }

    raise HTTPException(
        status_code=404,
        detail="No se encontró el post"
    )