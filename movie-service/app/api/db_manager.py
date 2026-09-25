from app.api.db import database, movies
from app.api.models import MovieIn


async def add_movie(payload: MovieIn):
    query = movies.insert().values(**payload.model_dump())
    return await database.execute(query=query)


async def get_all_movies():
    query = movies.select()
    return await database.fetch_all(query=query)


async def get_movie(id: int):
    query = movies.select().where(movies.c.id == id)
    return await database.fetch_one(query=query)


async def delete_movie(id: int):
    query = movies.delete().where(movies.c.id == id)
    return await database.execute(query=query)


async def update_movie(id: int, payload: MovieIn):
    query = movies.update().where(movies.c.id == id).values(**payload.model_dump())
    return await database.execute(query=query)
