import asyncio

import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))


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
