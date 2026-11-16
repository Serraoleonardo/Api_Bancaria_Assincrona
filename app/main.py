from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, contas


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="API Bancária Assíncrona",
    description="API RESTful assíncrona para depósitos, saques e extrato, com autenticação JWT.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(contas.router)


@app.get("/", tags=["Status"])
async def raiz():
    return {"status": "ok", "docs": "/docs"}
