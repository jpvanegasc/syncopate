class Syncopate:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(view):
            self.routes[path] = view
            return view

        return decorator

    async def __call__(self, scope, receive, send):
        assert scope["type"] == "http"

        path = scope["path"]
        handler = self.routes.get(path)
        if handler is None:
            send("<h1>404 Not Found</h1>", status_code=404, status_message="Not Found")

        # TODO: pass arguments to handler
        response = handler()
        send(response)
