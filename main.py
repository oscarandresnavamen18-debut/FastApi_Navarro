# Mini Blog v2 - FastAPI
# Validaciones avanzadas y modelos (Guía 1)
# + Path/Query Parameters (Guía 2)
# + Bases de datos relacionales con SQLAlchemy (Guía 3)

from fastapi import FastAPI, Query, Path, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session
from typing import Optional, List, Literal

import Models as models
from Database import engine, SessionLocal


# =========================================================
# Base de datos
# =========================================================

models.Base.metadata.create_all(bind=engine)


# =========================================================
# Aplicación FastAPI
# =========================================================

app = FastAPI(
    title="Mini Blog v2",
    version="1.0.0"
)

TAG_POSTS = ["Posts"]
TAG_SISTEMA = ["Sistema"]


# =========================================================
# Dependencia de base de datos
# =========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# Comentarios
# =========================================================

# Los comentarios se mantienen en memoria.
# Los posts sí se guardan en la base de datos.

COMENTARIOS_POR_POST: dict[int, list[dict]] = {}


# =========================================================
# Modelos Pydantic
# =========================================================

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
    titulo: str = Field(
        ...,
        min_length=1,
        description="Título del post"
    )

    contenido: str

    autor: Autor

    @field_validator("titulo")
    @classmethod
    def title_sin_espacios_extra(cls, value: str) -> str:
        limpio = value.strip()

        if not limpio:
            raise ValueError(
                "El título no puede estar vacío ni contener solo espacios"
            )

        return limpio

    @model_validator(mode="after")
    def titulo_distinto_de_contenido(self):
        if self.titulo.strip().lower() == self.contenido.strip().lower():
            raise ValueError(
                "El título no puede ser igual al contenido"
            )

        return self


class PostUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None

    @field_validator("titulo")
    @classmethod
    def title_sin_espacios_extra(
        cls,
        value: Optional[str]
    ) -> Optional[str]:

        if value is None:
            return value

        limpio = value.strip()

        if not limpio:
            raise ValueError(
                "El título no puede estar vacío ni contener solo espacios"
            )

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


# =========================================================
# Modelo de respuesta para GET /posts
# =========================================================

class PostsResponse(BaseModel):
    total: int
    data: List[PostPublicoOut]


# =========================================================
# Convertir modelo de BD a respuesta pública
# =========================================================

def post_to_out(post_db: models.Post) -> PostPublicoOut:
    """
    Arma la respuesta pública a partir del registro
    de la base de datos.
    """

    return PostPublicoOut(
        id=post_db.id,
        titulo=post_db.titulo,
        contenido=post_db.contenido,
        autor=AutorPublico(
            nombre=post_db.autor_nombre
        ),
        estado=post_db.estado,
        comentarios=COMENTARIOS_POR_POST.get(
            post_db.id,
            []
        ),
    )


# =========================================================
# GET /
# =========================================================

@app.get(
    "/",
    tags=TAG_SISTEMA,
    summary="Mensaje de bienvenida"
)
def home():
    return {
        "mensaje": "Bienvenidos a mi blog Edison Suares"
    }


# =========================================================
# GET /posts
# Listar posts con búsqueda, orden y paginación
# =========================================================

@app.get(
    "/posts",
    response_model=PostsResponse,
    summary="Listar posts del blog",
    description=(
        "Devuelve los posts, con soporte de búsqueda, "
        "orden y paginación (leído desde la base de datos)."
    ),
    response_description=(
        "Total de posts y datos filtrados, ordenados y paginados"
    ),
    tags=TAG_POSTS,
)
def list_posts(
    query: str | None = Query(
        default=None,
        min_length=2,
        max_length=50,
        description="Texto para buscar por título"
    ),

    skip: int = Query(
        default=0,
        ge=0,
        description="Cuántos posts saltar desde el inicio"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Cuántos posts devolver como máximo"
    ),

    order_by: Literal["id", "titulo"] = Query(
        default="id",
        description="Campo por el cual ordenar"
    ),

    order: Literal["asc", "desc"] = Query(
        default="asc",
        description="Dirección del orden"
    ),

    db: Session = Depends(get_db),
):
    # Consulta inicial
    consulta = db.query(models.Post)

    # -----------------------------------------
    # Búsqueda por título
    # -----------------------------------------

    if query:
        consulta = consulta.filter(
            models.Post.titulo.contains(query)
        )

    # -----------------------------------------
    # Total ANTES de aplicar paginación
    # -----------------------------------------

    total = consulta.count()

    # -----------------------------------------
    # Orden
    # -----------------------------------------

    columna = getattr(
        models.Post,
        order_by
    )

    if order == "desc":
        consulta = consulta.order_by(
            columna.desc()
        )
    else:
        consulta = consulta.order_by(
            columna.asc()
        )

    # -----------------------------------------
    # Paginación
    # -----------------------------------------

    posts = (
        consulta
        .offset(skip)
        .limit(limit)
        .all()
    )

    # -----------------------------------------
    # Respuesta
    # -----------------------------------------

    return {
        "total": total,
        "data": [
            post_to_out(post)
            for post in posts
        ]
    }


# =========================================================
# GET /posts/buscar
# Buscar varios posts por ID
# =========================================================

@app.get(
    "/posts/buscar",
    summary="Buscar varios posts por id",
    tags=TAG_POSTS
)
def buscar_posts_por_id(
    id: list[int] = Query(
        default=[],
        description="Puede repetirse: ?id=1&id=3"
    ),

    db: Session = Depends(get_db),
):
    if not id:
        return {
            "datos": []
        }

    posts = (
        db.query(models.Post)
        .filter(models.Post.id.in_(id))
        .all()
    )

    return {
        "datos": [
            post_to_out(post)
            for post in posts
        ]
    }


# =========================================================
# GET /posts/buscar-avanzado
# =========================================================

@app.get(
    "/posts/buscar-avanzado",
    summary="Búsqueda avanzada de posts",
    description=(
        "Combina búsqueda por texto, filtro por ids, "
        "orden y paginación."
    ),
    response_description=(
        "Lista de posts que cumplen los filtros, "
        "ya ordenada y paginada"
    ),
    tags=TAG_POSTS,
)
def buscar_avanzado(
    query: str | None = Query(
        default=None,
        min_length=2,
        max_length=50,
        description="Texto para buscar en el título"
    ),

    buscar: str | None = Query(
        default=None,
        deprecated=True,
        description="OBSOLETO: usa 'query'"
    ),

    ids: list[int] = Query(
        default=[],
        description=(
            "Lista de ids para filtrar "
            "(puede repetirse: ?ids=1&ids=2)"
        )
    ),

    order_by: Literal["id", "titulo"] = Query(
        default="id",
        description="Campo por el cual ordenar"
    ),

    order: Literal["asc", "desc"] = Query(
        default="asc",
        description="Dirección del orden"
    ),

    skip: int = Query(
        default=0,
        ge=0,
        description="Cuántos posts saltar desde el inicio"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Cuántos posts devolver como máximo"
    ),

    db: Session = Depends(get_db),
):
    texto_busqueda = (
        query
        if query is not None
        else buscar
    )

    consulta = db.query(models.Post)

    if texto_busqueda:
        consulta = consulta.filter(
            models.Post.titulo.contains(texto_busqueda)
        )

    if ids:
        consulta = consulta.filter(
            models.Post.id.in_(ids)
        )

    total_sin_paginar = consulta.count()

    columna = getattr(
        models.Post,
        order_by
    )

    if order == "desc":
        consulta = consulta.order_by(
            columna.desc()
        )
    else:
        consulta = consulta.order_by(
            columna.asc()
        )

    posts = (
        consulta
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "datos": [
            post_to_out(post)
            for post in posts
        ],
        "total_sin_paginar": total_sin_paginar,
        "skip": skip,
        "limit": limit,
    }


# =========================================================
# GET /posts/destacado
# =========================================================

@app.get(
    "/posts/destacado",
    tags=TAG_POSTS,
    summary="Post destacado"
)
def post_destacado(
    db: Session = Depends(get_db)
):
    post = (
        db.query(models.Post)
        .order_by(models.Post.id.asc())
        .first()
    )

    if not post:
        return {
            "error": "No hay posts todavía"
        }

    return {
        "destacado": post_to_out(post)
    }


# =========================================================
# GET /posts/vacios
# =========================================================

@app.get(
    "/posts/vacios",
    tags=TAG_POSTS,
    summary="Verificar si hay posts"
)
def posts_vacios(
    db: Session = Depends(get_db)
):
    total = db.query(models.Post).count()

    if total == 0:
        return {
            "total": 0
        }

    return {
        "total": total
    }


# =========================================================
# GET /posts/{post_id}
# =========================================================

@app.get(
    "/posts/{post_id}",
    summary="Consultar un post por id",
    response_description="Datos del post solicitado",
    tags=TAG_POSTS,
)
def get_post(
    post_id: int = Path(
        gt=0,
        description="ID del post a consultar"
    ),

    incluir_contenido: bool = Query(
        default=True,
        description="Incluir o no el contenido"
    ),

    include_content: bool | None = Query(
        default=None,
        deprecated=True,
        description=(
            "OBSOLETO: usa 'incluir_contenido' en su lugar"
        )
    ),

    db: Session = Depends(get_db),
):
    valor_final = (
        include_content
        if include_content is not None
        else incluir_contenido
    )

    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el post"
        )

    if not valor_final:
        return {
            "id": post.id,
            "titulo": post.titulo
        }

    return post_to_out(post)


# =========================================================
# POST /posts
# =========================================================

@app.post(
    "/posts",
    status_code=201,
    response_model=PostPublicoOut,
    summary="Crear un post nuevo",
    response_description="El post recién creado",
    tags=TAG_POSTS,
)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db)
):
    nuevo_post = models.Post(
        titulo=post.titulo,
        contenido=post.contenido,
        autor_nombre=post.autor.nombre,
        autor_email=post.autor.email,
        estado="borrador",
    )

    db.add(nuevo_post)

    db.commit()

    db.refresh(nuevo_post)

    return post_to_out(nuevo_post)


# =========================================================
# PUT /posts/{post_id}
# =========================================================

@app.put(
    "/posts/{post_id}",
    summary="Actualizar un post",
    response_description="El post ya actualizado",
    tags=TAG_POSTS,
)
def update_post(
    post_id: int = Path(
        gt=0,
        description="ID del post a actualizar"
    ),

    data: PostUpdate = None,

    db: Session = Depends(get_db),
):
    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el post"
        )

    payload = data.model_dump(
        exclude_unset=True
    )

    for campo, valor in payload.items():
        setattr(post, campo, valor)

    db.commit()

    db.refresh(post)

    return {
        "mensaje": "Post actualizado",
        "data": post_to_out(post)
    }


# =========================================================
# DELETE /posts/{post_id}
# =========================================================

@app.delete(
    "/posts/{post_id}",
    status_code=204,
    summary="Eliminar un post",
    tags=TAG_POSTS
)
def delete_post(
    post_id: int = Path(
        gt=0,
        description="ID del post a eliminar"
    ),

    db: Session = Depends(get_db),
):
    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post no encontrado para eliminar"
        )

    db.delete(post)

    db.commit()

    COMENTARIOS_POR_POST.pop(
        post_id,
        None
    )

    return


# =========================================================
# POST /posts/{post_id}/comentarios
# =========================================================

@app.post(
    "/posts/{post_id}/comentarios",
    status_code=201,
    summary="Agregar un comentario a un post",
    response_description="El comentario recién agregado",
    tags=TAG_POSTS,
)
def add_comentario(
    post_id: int = Path(
        gt=0,
        description="ID del post a comentar"
    ),

    comentario: ComentarioCreate = None,

    db: Session = Depends(get_db),
):
    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el post"
        )

    lista_actual = COMENTARIOS_POR_POST.setdefault(
        post_id,
        []
    )

    nuevo_id = (
        lista_actual[-1]["id"] + 1
        if lista_actual
        else 1
    )

    nuevo_comentario = {
        "id": nuevo_id,
        "contenido": comentario.contenido,
        "autor": comentario.autor
    }

    lista_actual.append(
        nuevo_comentario
    )

    return {
        "mensaje": "Comentario agregado",
        "data": nuevo_comentario
    }


# =========================================================
# PATCH /posts/{post_id}/publicar
# =========================================================

@app.patch(
    "/posts/{post_id}/publicar",
    summary="Publicar un post",
    response_description="El post ya publicado",
    tags=TAG_POSTS
)
def publicar_post(
    post_id: int = Path(
        gt=0,
        description="ID del post a publicar"
    ),

    db: Session = Depends(get_db),
):
    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el post"
        )

    post.estado = "publicado"

    db.commit()

    db.refresh(post)

    return {
        "mensaje": "Post publicado",
        "data": post_to_out(post)
    }