import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./teste.db"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base, engine
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_headers(client):
    await client.post("/auth/cadastro", json={"nome": "Léo", "cpf": "123.456.789-00", "senha": "segredo123"})
    r = await client.post("/auth/login", data={"username": "12345678900", "password": "segredo123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
