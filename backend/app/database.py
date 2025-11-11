from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings
from .models import Base

settings = get_settings()

# Crear engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=3600,   # Reciclar conexiones cada hora
    echo=False           # True para debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")


def get_db():
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


