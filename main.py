import asyncio

import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))

origins = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
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


@app.get("/webpage/")
async def get_website_html(domain: str) -> dict:  # noqa: D103
    async with aiohttp.ClientSession() as session, session.get(domain) as resp:
        html = await resp.text()

    return {domain: html}


async def main() -> None:  # noqa: D103
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
