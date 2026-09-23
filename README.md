# mini-rag

This is a minimal implementation of the RAG model for question answering.

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- API keys for at least one LLM provider (OpenAI or Cohere) and one OCR provider (Mistral or Gemini)

### 1. Clone & Configure

git clone https://github.com/MRSHEPOXRobot/RAG-System-
cd RAG-System

# App environment
cp Src/.env.example Src/.env

# Edit Src/.env with your API keys
# (see Environment Variables below)

## 3. Start Services with Docker

[svg](https://github.com/MohamedEhab155/RAG-System#3-start-services-with-docker)

```bash
cd docker

# Copy and configure each env file
cp env/.env.examble_app        env/.env.app
cp env/.env.examble.postgres   env/.env.postgres
cp env/.env.examble.grafana    env/.env.grafana

# Start all services
sudo docker compose up -d
```

**svg**

Or start only core services (no monitoring):

```bash
docker compose up -d fastapi nginx pgvector qdrant
```

**svg**

### 4. Run the API (Local Development)

[svg](https://github.com/MRSHEPOXRobot/RAG-System-#4-run-the-api-local-development)

```bash
cd Src
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

**svg**

API docs available at: [**http://localhost:5000/docs**](http://localhost:5000/docs)

<img width="1204" height="517" alt="image" src="https://github.com/user-attachments/assets/fc345a30-cf3e-473d-b273-945ce713bedb" />


## Environment Variables

Key variables in `Src/.env`:

```env
# App
APP_NAME=mini-rag
APP_VERSION=1.0.0

# LLM Providers (pick one or both)
GENERATION_BACKEND=COHERE        # OPENAI or COHERE
EMBEDDING_BACKEND=COHERE         # OPENAI or COHERE
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...

# Model Config
GENERATION_MODEL_ID=command-r-plus
EMBEDDING_MODEL_ID=embed-multilingual-v3.0
EMBEDDING_MODEL_SIZE=1024

# Vector DB
VECTOR_DB_BACKEND=PGVECTOR       # QDRANT or PGVECTOR
VECTOR_DB_DISTANCE_METHOD=cosine

# OCR
OCR_BACKEND=MISTRAL              # MISTRAL or GEMENAI
MISTRAL_API_KEY=...
GEMENAI_API_KEY=...

# PostgreSQL
POSTGRES_USERNAME=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=pgvector
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE=minirag

# Language
PRIMARY_LANG=en                   # en or ar
```


# API Reference

## Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/app/v2/data/upload/{project_id}` | Upload a PDF or TXT document |
| `POST` | `/app/v2/data/process/{project_id}` | Chunk and store document content |

## NLP / RAG Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/app/v2/nlp/index/push/{project_id}` | Embed chunks and push to vector DB |
| `GET` | `/app/v2/nlp/index/info/{project_id}` | Get vector collection metadata |
| `POST` | `/app/v2/nlp/index/search/{project_id}` | Semantic similarity search |
| `POST` | `/app/v2/nlp/index/answer/{project_id}` | Full RAG answer generation |

## Project Structure

```text
├── Src/
│   ├── main.py                  # FastAPI app entry point
│   ├── Contoroller/             # Business logic layer
│   │   ├── NLPContoroller.py    # RAG pipeline orchestration
│   │   ├── ProcessContoroller.py# Document chunking
│   │   └── DataContoroller.py   # File validation & storage
│   ├── Stores/
│   │   ├── LLM/                 # OpenAI + Cohere providers
│   │   ├── VectorDB/            # Qdrant + PgVector providers
│   │   └── OCR/                 # Mistral + Gemini providers
│   ├── models/
│   │   ├── db_Schema/           # SQLAlchemy models + Alembic
│   │   └── Enums/               # Response signals, processing types
│   ├── Routers/                 # FastAPI route definitions
│   └── utils/
│       ├── PDFLoader.py         # Parallel OCR PDF processor
│       ├── CleanText.py         # Arabic/English text cleaner
│       └── metrics.py           # Prometheus middleware
└── docker/
    ├── docker-compose.yml
    ├── nginx/
    └── Prometheus/
