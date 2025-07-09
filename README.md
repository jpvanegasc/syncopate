# 🎶 Syncopate
An experimental ASGI framework that thrives on the polyrhythmic magic of async Python.
This project is built as a learning exercise, so it re-implements all the wheels posible:
the `asyncio` event loop and server, [uvicorn](https://www.uvicorn.org/) HTTP ASGI
server and [h11](https://h11.readthedocs.io/en/latest/) protocol library,
and [starlette](https://www.starlette.io/) ASGI toolkit.
__It is not meant for production!__ Use under your own risk.

### 📖 Table of Contents
- ⚒ [Env Setup and Development](#-env-setup-and-development)
- ⚙ [Running Syncopate](#-running-syncopate)

## ⚒ Env Setup and Development
To set up your local environment for development run
```shell
make init
```
This will install all dev requirements using [uv](https://docs.astral.sh/uv/) and add
the pre-commit hooks.

## ⚙ Running Syncopate
Build an ASGI app:
```python
from syncopate.framework import Syncopate

app = Syncopate()


@app.route("/")
async def index(request):
    return "Hello, World!"


@app.route("/api")
def api(request):
    return {"hello": "world"}
```
and run it:
```python
import syncopate

syncopate.run(app, host="localhost", port=8888)
```
This will start the syncopate server and run the app on [http://localhost:8888](http://localhost:8888).
