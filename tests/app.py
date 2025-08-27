import logging
import time

import syncopate
from syncopate.framework import Syncopate
from syncopate.framework.background import BackgroundTask, BackgroundTasks
from syncopate.framework.requests import Request
from syncopate.framework.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


app = Syncopate()


async def async_background_task():
    logger.info("Async Background Task")


def sync_background_task():
    time.sleep(1)
    logger.info("Sync Background Task")


@app.route("/async/get")
async def async_get(request: Request):
    if request.scope["method"] != "GET":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    return HTMLResponse("/async/get")


@app.route("/async/post")
async def async_post(request: Request):
    if request.scope["method"] != "POST":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    tasks = BackgroundTasks()
    tasks.add_task(BackgroundTask(async_background_task))
    tasks.add_task(BackgroundTask(sync_background_task))
    return JSONResponse(await request.json(), background=tasks)


if __name__ == "__main__":
    syncopate.run(app)
