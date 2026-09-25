from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.db import database, engine, metadata
from app.api.movies import movies

metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/v1/movies/openapi.json",
    docs_url="/api/v1/movies/docs",
)


@app.get("/health", include_in_schema=False)
async def health():
    await database.fetch_val("SELECT 1")
    return {"status": "ok"}


app.include_router(movies, prefix="/api/v1/movies", tags=["movies"])
