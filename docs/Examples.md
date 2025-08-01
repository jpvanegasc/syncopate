# Examples

You can use Syncopate as a framework (like Starlette or FastAPI):
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

and you can run it using Syncopate's internal server:

```python
import syncopate

syncopate.run(app, host="localhost", port=8888)
```
