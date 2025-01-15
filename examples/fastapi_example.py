import sniffio
from fastapi import FastAPI

import syncopate

sniffio.current_async_library_cvar.set("asyncio")


app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}


if __name__ == "__main__":
    syncopate.run(app)
