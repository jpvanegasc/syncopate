import logging

import syncopate
from syncopate.framework import Syncopate
from syncopate.framework.responses import HTMLResponse

logger = logging.getLogger(__name__)


app = Syncopate()


@app.route("/")
async def root(request):
    if request.scope["method"] == "GET":
        return HTMLResponse("<h1>Hello, World!</h1>")
    if request.scope["method"] == "POST":
        data = await request.json()
        logger.info(data)
        return HTMLResponse("<h1>Hello, World!</h1>")
    return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)


if __name__ == "__main__":
    syncopate.run(app)
