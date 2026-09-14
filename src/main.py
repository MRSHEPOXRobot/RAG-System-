from controllers import DataController,ProjectController,BaseController
from routes.data import data_router
from routes.base import base_router
from routes.nlp import nlp_router
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()

    app.mongo_conn = AsyncIOMotorClient(
        settings.MONGODB_URL
    )

    app.db_client = app.mongo_conn[
        settings.MONGODB_DATABASE
    ]
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    #generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    #embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    app.vector_db_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect() #initialize the connection to the vector database

    app.template_parser = TemplateParser(
        language=settings.DEFAULT_LANG,
        default_language=settings.DEFAULT_LANG,

    )

    yield

    #Shutdown
    app.mongo_conn.close()
    app.vector_db_client.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(data_router)
app.include_router(base_router)
app.include_router(nlp_router)

