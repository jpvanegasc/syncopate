from syncopate.framework.routing import Route


class Syncopate:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(endpoint):
            self.routes[path] = Route(path, endpoint)
            return endpoint

        return decorator

    async def __call__(self, scope, receive, send):
        assert scope["type"] == "http"

        path = scope["path"]
        handler = self.routes.get(path)
        if handler is None:
            msg = b"<h1>Not Found</h1>"
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "status_message": "Not Found",
                    "headers": [("Content-Length", len(msg))],
                }
            )

            await send({"type": "http.response.body", "body": msg, "more_body": False})
            return

        await handler(scope, receive, send)
