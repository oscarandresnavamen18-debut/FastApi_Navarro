from sqlalchemy import Column, Integer, String
from Database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    contenido = Column(String, nullable=False)
    # El autor se guarda "aplanado" en la misma tabla (autor_nombre, autor_email).
    # Relacionar Post con una tabla Autor aparte (clave foránea) es un tema de
    # "relaciones entre tablas" que la Guía 3 deja para una guía futura.
    autor_nombre = Column(String(100), nullable=False)
    autor_email = Column(String(150), nullable=False)
    estado = Column(String(20), nullable=False, default="borrador")