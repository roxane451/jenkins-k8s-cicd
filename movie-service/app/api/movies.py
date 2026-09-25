from typing import List

from fastapi import APIRouter, HTTPException

from app.api import db_manager
from app.api.models import MovieIn, MovieOut, MovieUpdate
from app.api.service import is_cast_present

movies = APIRouter()


async def ensure_casts_exist(casts_id: List[int]):
    for cast_id in casts_id:
        if not await is_cast_present(cast_id):
            raise HTTPException(status_code=404, detail=f"Cast with given id:{cast_id} not found")


@movies.post("/", response_model=MovieOut, status_code=201)
async def create_movie(payload: MovieIn):
    await ensure_casts_exist(payload.casts_id)
    movie_id = await db_manager.add_movie(payload)
    return {"id": movie_id, **payload.model_dump()}


@movies.get("/", response_model=List[MovieOut])
async def get_movies():
    return [dict(movie._mapping) for movie in await db_manager.get_all_movies()]


@movies.get("/{id}/", response_model=MovieOut)
async def get_movie(id: int):
    movie = await db_manager.get_movie(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return dict(movie._mapping)


@movies.put("/{id}/", response_model=MovieOut)
async def update_movie(id: int, payload: MovieUpdate):
    movie = await db_manager.get_movie(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "casts_id" in update_data:
        await ensure_casts_exist(payload.casts_id)

    movie_in_db = MovieIn(**dict(movie._mapping))
    updated_movie = movie_in_db.model_copy(update=update_data)
    await db_manager.update_movie(id, updated_movie)
    return {"id": id, **updated_movie.model_dump()}


@movies.delete("/{id}/", status_code=204)
async def delete_movie(id: int):
    movie = await db_manager.get_movie(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    await db_manager.delete_movie(id)
