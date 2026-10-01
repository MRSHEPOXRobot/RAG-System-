from RAG_Base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID # uuid type for PostgreSQL
# UUID (Universally Unique Identifier) is a 128-bit number used to identify information in computer systems.
import uuid
from sqlalchemy.orm import relationship


class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, default=uuid.uuid4, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    chunk_data = relationship("ChunkData", back_populates="project")
    assets = relationship("Asset", back_populates="project")