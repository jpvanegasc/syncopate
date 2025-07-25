import logging

import syncopate
from syncopate.framework import Syncopate
from syncopate.framework.requests import Request
from syncopate.framework.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


app = Syncopate()


@app.route("/async/get")
async def async_get(request: Request):
    if request.scope["method"] != "GET":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    return HTMLResponse("/async/get")


@app.route("/async/post")
async def async_post(request: Request):
    if request.scope["method"] != "POST":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    return JSONResponse(await request.json())


if __name__ == "__main__":
    syncopate.run(app)
