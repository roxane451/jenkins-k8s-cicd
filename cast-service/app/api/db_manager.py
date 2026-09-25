from app.api.db import casts, database
from app.api.models import CastIn


async def add_cast(payload: CastIn):
    query = casts.insert().values(**payload.model_dump())
    return await database.execute(query=query)


async def get_cast(id: int):
    query = casts.select().where(casts.c.id == id)
    return await database.fetch_one(query=query)
