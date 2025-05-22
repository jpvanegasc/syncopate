# 🎶 Syncopate
Syncopate is an experimental ASGI framework that thrives on the polyrhythmic magic of async Python. This project is built as a learning exercise, so it re-implements all the wheels posible: the `asyncio` event loop and server, [uvicorn](https://www.uvicorn.org/) HTTP ASGI server, and [starlette](https://www.starlette.io/) ASGI toolkit. __It is not meant for production!__ Use under your own risk.

### 📖 Table of Contents
- ⚒ [Env Setup and Development](#-env-setup-and-development)
- ⚙ [Running Syncopate](#-running-syncopate)
- [Event loop diagram](#loop-diagram)

## ⚒ Env Setup and Development
To set up your local environment for development run
```shell
make envsetup
```
This will create a virtual environment for the project and install the pre-commit hooks. Syncopate doesn't have any third-party requirements, it does everything itself!

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

## Loop Diagram
```mermaid
sequenceDiagram
    box Loop
    participant Q as Task Queue
    participant H as Handle
    participant A as API
    end
    box Task
    participant T as Task API
    participant F as Future API
    end

    A->>T: create_task
    activate T
    Note right of T: __init__
    T->>A: call_soon
    deactivate T

    activate A
    activate H
    A->>H: 
    note right of H: __init__
    H->>A: 
    deactivate H
    A->>Q: queue.append
    deactivate A

    activate Q
    loop every Handle in queue
    Q->>H: Handle.step
    activate Q
    activate H
    H->>T: Task.coro.send
    activate T
    activate T
    alt send()
        T->>A: call_soon
        deactivate T
activate A
        activate H
        A->>H: 
        note right of H: __init__
        H->>A: 
        deactivate H
        A->>Q: queue.append
        deactivate A
        deactivate Q
    else raise StopIteration
        deactivate T
        T->>H: 
        H->>F: set_result
    end
    deactivate H
    end

    activate F
    Note right of F: _state, _result
    deactivate F
    F->>T: result
```
