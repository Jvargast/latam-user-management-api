from sqlalchemy.orm import DeclarativeBase

# Base para los modelos de SQLAlchemy -> Para hacer separación entre infra y dominio
class Base(DeclarativeBase):
    pass
