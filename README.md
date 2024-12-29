# 🎶 Syncopate
Syncopate is an experimental ASGI framework that thrives on the polyrhythmic magic of async Python. This project is built as a learning exercise, so it re-implements all the wheels posible: the `asyncio` event loop and HTTP server, [uvicorn](https://www.uvicorn.org/) ASGI server, and [starlette](https://www.starlette.io/) ASGI toolkit. __It is not meant for production!__ Use under your own risk.

### 📖 Table of Contents
- ⚒ [Env Setup and Development](#-env-setup-and-development)
- ⚙ [Running Locally](#-running-locally)

## ⚒ Env Setup and Development
To set up your local environment run
```shell
make envsetup
```
This will create a virtual environment for the project and install the pre-commit hooks. Syncopate doesn't have any requirements, it does everything itself!

## Running Locally
From the root of the project run
```shell
make run
```
This will start the syncopate server on [http://localhost:8888](http://localhost:8888).
