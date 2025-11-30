from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OdooModule(Base):
    __tablename__ = "odoo_modules"

    id = Column(Integer, primary_key=True, index=True)
    technical_name = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)

    version = Column(String, nullable=False, index=True)
    depends = Column(ARRAY(String), default=[])
    author = Column(String)
    license = Column(String, default="AGPL-3")

    summary = Column(String)
    description = Column(Text)
    readme = Column(Text)

    repo_name = Column(String, nullable=False)
    repo_url = Column(String)
    module_path = Column(String)

    github_stars = Column(Integer, default=0)
    github_issues_open = Column(Integer, default=0)
    last_commit_date = Column(DateTime)

    embedding = Column(Vector(2560))

    searchable_text = Column(TSVECTOR)

    ai_description = Column(Text)
    functional_tags = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    enriched_at = Column(DateTime)
    enrichment_version = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<OdooModule {self.technical_name} v{self.version}>"
