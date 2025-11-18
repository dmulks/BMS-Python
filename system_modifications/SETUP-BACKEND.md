
# Backend Setup (FastAPI + PostgreSQL)

## Prerequisites

- Python 3.10+
- PostgreSQL
- Terminal & git

---

## Steps

### 1. Create Project Structure

```text
backend/
  app.py
  db.py
  models.py
  routers/
  schemas/
  services/
  scripts/
```

### 2. Virtual Environment

```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dateutil pandas python-multipart
```

### 4. Configure `db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/bond_db"

engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

### 5. Define Models & Create Tables

- Implement models inheriting from `Base`.
- Create tables:

```python
from db import engine, Base
Base.metadata.create_all(bind=engine)
```

### 6. Create `app.py`

- Include routers and CORS config.
- Example:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import dashboard, members, payment_events, admin

app = FastAPI(title="Bond Management System API")

origins = ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(members.router)
app.include_router(payment_events.router)
app.include_router(admin.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

### 7. Run the Server

```bash
uvicorn app:app --reload
```

Swagger docs: `http://localhost:8000/docs`
