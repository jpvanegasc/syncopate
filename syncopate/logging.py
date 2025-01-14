import logging

# TODO: add non-blocking handler
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("syncopate")
