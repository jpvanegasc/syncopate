import logging

import syncopate
from syncopate.framework import Syncopate
from syncopate.framework.responses import HTMLResponse

logger = logging.getLogger(__name__)


app = Syncopate()


@app.route("/get/sync")
async def root(request):
    if request.scope["method"] != "GET":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    return HTMLResponse("/get/sync")


if __name__ == "__main__":
    syncopate.run(app)
