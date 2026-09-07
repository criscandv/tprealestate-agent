"""Dependencias compartidas de la API.

Aqui viviran las dependencias de autenticacion (verificacion del JWT de Django
reenviado y de la API key de servicio) y de acceso a datos. De momento solo se
re-exporta la sesion de base de datos.
"""

from app.services.database import get_db

__all__ = ["get_db"]
