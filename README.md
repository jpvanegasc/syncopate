# 🎶 Syncopate

> An experimental ASGI runtime and framework that thrives on the polyrhythmic magic of
> async Python.

This project is built as a learning exercise, so it re-implements all the wheels posible:
the `asyncio` event loop and server, [uvicorn](https://www.uvicorn.org/) HTTP ASGI
server and [h11](https://h11.readthedocs.io/en/latest/) protocol library,
and [starlette](https://www.starlette.io/) ASGI toolkit.
**It is not meant for production!** Use under your own risk.

### 📖 Table of Contents

- ⚙ [Running Syncopate](#-running-syncopate)
- ⚒ [Env Setup and Development](#-env-setup-and-development)
- 🧪 [Testing](#-testing)

## ⚙ Running Syncopate

Build an ASGI app:

```python
from syncopate import Syncopate

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

## ⚒ Env Setup and Development

To set up your local environment for development run

```shell
just init
```

This will install all (Python) dev requirements using [uv](https://docs.astral.sh/uv/)
and add the pre-commit hooks.

## 🧪 Testing

Testing syncopate is done via:

- `tests/app.py` defines an e2e ASGI app+runtime which will be tested against.
- `tests/suite.hurl` defines a [Hurl](https://hurl.dev) suite that will be fired at the live
  app+runtime instance.
- `coverage` measures code coverage when firing the hurl suite agains the app+runtime.
- `tests/run.sh` orchestrates the entire testing flow.

Run them with:

```shell
just test
```
