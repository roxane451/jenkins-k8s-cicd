import os

import httpx

CAST_SERVICE_HOST_URL = "http://localhost:8002/api/v1/casts/"


async def is_cast_present(cast_id: int) -> bool:
    url = os.environ.get("CAST_SERVICE_HOST_URL") or CAST_SERVICE_HOST_URL
    # La route du cast-service se termine par "/" : sans elle, la réponse
    # est une redirection 307 et le cast serait considéré comme absent.
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{url}{cast_id}/")
    return r.status_code == 200
