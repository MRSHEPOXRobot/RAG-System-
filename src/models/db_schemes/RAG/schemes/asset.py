from RAG_Base import SQLAlchemyBase
from sqlalchemy import Column , Integer,DateTime ,func,String,ForeignKey
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import Index

class Asset(SQLAlchemyBase):
    __tablename__ = "assets"

    asset_id=Column(Integer,primary_key=True,autoincrement=True)
    uuid=Column(UUID,default=uuid.uuid4,unique=True,nullable=False)
    asset_type=Column(String,nullable=True)
    asset_name=Column(String,nullable=True)
    asset_size=Column(Integer,nullable=True)
    asset_config=Column(JSONB,nullable=True)
    #  different from JSON, JSONB is a binary representation of JSON data that allows for faster access and manipulation of the data. It also supports indexing, which can improve query performance. الكتابة أسرع هنا
    # JSONB is a PostgreSQL-specific data type for storing JSON data in a binary format, which allows for efficient storage and querying of JSON data.

    asset_project_id=Column(Integer,ForeignKey("projects.project_id"),nullable=False)


    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdate=func.now(),nullable=True)


    project=relationship("Project",back_populates="assets")
    chunk_data=relationship("ChunkData",back_populates="asset")

    __tableargs__ = (
        Index ("ix_asset_project_id", "asset_project_id"),
        Index ( "ix_asset_type", "asset_type")
    )