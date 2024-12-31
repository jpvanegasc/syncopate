import logging

import syncopate
from syncopate.framework import Syncopate

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = Syncopate()
    syncopate.run(app)
