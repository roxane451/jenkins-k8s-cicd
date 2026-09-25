from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.casts import casts
from app.api.db import database, engine, metadata

metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/v1/casts/openapi.json",
    docs_url="/api/v1/casts/docs",
)


@app.get("/health", include_in_schema=False)
async def health():
    await database.fetch_val("SELECT 1")
    return {"status": "ok"}


app.include_router(casts, prefix="/api/v1/casts", tags=["casts"])
