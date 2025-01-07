import logging

import syncopate
from syncopate.framework import Syncopate

logger = logging.getLogger(__name__)


app = Syncopate()


@app.route("/")
def index():
    return "<h1>Hello, World!</h1>"


if __name__ == "__main__":
    syncopate.run(app)
