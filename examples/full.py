import logging
import time

import syncopate
from syncopate.framework import Syncopate
from syncopate.framework.background import BackgroundTask, BackgroundTasks
from syncopate.framework.responses import HTMLResponse

logger = logging.getLogger(__name__)


app = Syncopate()


async def async_background_task():
    logger.info("Async Background Task")


def sync_background_task():
    time.sleep(1)
    logger.info("Sync Background Task")


@app.route("/")
async def root(request):
    if request.scope["method"] == "GET":
        return HTMLResponse("<h1>Hello, World!</h1>")
    if request.scope["method"] == "POST":
        data = await request.json()
        logger.info(data)
        tasks = BackgroundTasks()
        tasks.add_task(BackgroundTask(async_background_task))
        tasks.add_task(BackgroundTask(sync_background_task))
        return HTMLResponse("<h1>Hello, World!</h1>", background=tasks)
    return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)


@app.route("/sync")
def sync(request):
    if request.scope["method"] != "GET":
        return HTMLResponse("<h1>Method Not Allowed</h1>", status=405)
    return HTMLResponse("<h1>Hello, World!</h1><p>Sync</p>")


if __name__ == "__main__":
    syncopate.run(app)
