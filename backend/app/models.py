from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OdooModule(Base):
    __tablename__ = "odoo_modules"

    # Identificadores
    id = Column(Integer, primary_key=True, index=True)
    technical_name = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)

    # Metadata Odoo
    version = Column(String, nullable=False, index=True)  # "16.0", "17.0", "18.0"
    depends = Column(ARRAY(String), default=[])
    author = Column(String)
    license = Column(String, default="AGPL-3")

    # Descripciones
    summary = Column(String)
    description = Column(Text)

    # GitHub info
    repo_name = Column(String, nullable=False)
    repo_url = Column(String)
    module_path = Column(String)  # Ruta en el repo

    # Métricas GitHub
    github_stars = Column(Integer, default=0)
    github_issues_open = Column(Integer, default=0)
    last_commit_date = Column(DateTime)

    # Embedding (vector de 2560 dimensiones para Qwen3-Embedding 4B)
    embedding = Column(Vector(2560))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<OdooModule {self.technical_name} v{self.version}>"


