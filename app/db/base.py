import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr

Base = declarative_base()


class BaseModel(Base):
    """Clase base para todos los modelos de la aplicación."""

    __abstract__ = True

    __name__: ClassVar[str]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Genera automáticamente el nombre de la tabla a partir del nombre de la clase."""
        return f"t_{cls.__name__.lower()}"

    # Campos comunes para todos los modelos
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
