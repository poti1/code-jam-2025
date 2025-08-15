import asyncio
from typing import Annotated

import aiohttp
import uvicorn
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def read_root() -> HTMLResponse:  # noqa: D103
    with open("index.html") as index_html:  # noqa: PTH123
        data = index_html.read()

    return HTMLResponse(data)


class WebRequestPayload(BaseModel):
    """A valid API request for a website to be fetched, bypassing CORS."""

    headers: dict[str, str]
    target: str


@app.post("/webpage/")
async def get_website_html(payload: Annotated[WebRequestPayload, Body()]) -> dict:  # noqa: D103
    headers = payload.headers
    target = payload.target

    async with aiohttp.ClientSession(headers=headers) as session, session.get(target) as resp:
        html = await resp.text()
        resp_headers = resp.raw_headers

    return {"content": html, "headers": resp_headers}


async def main() -> None:  # noqa: D103
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
