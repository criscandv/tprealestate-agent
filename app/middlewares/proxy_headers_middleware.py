class ProxyHeadersMiddleware:
    """
    Middleware to handle proxy headers in requests.
    This middleware is used to extract and set the original client IP address
    and other relevant headers when the application is behind a proxy.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])

            # Handle X-Forwarded-Proto header
            if b"x-forwarded-proto" in headers:
                scope["scheme"] = headers[b"x-forwarded-proto"].decode()

            # Handle X-Forwarded-Host header
            if b"x-forwarded-host" in headers:
                scope["server"] = (headers[b"x-forwarded-host"].decode(), None)
                # Remove port from host header to avoid :8000 duplication
                host = headers[b"x-forwarded-host"].decode()
                if ":" in host:
                    host = host.split(":")[0]
                headers[b"host"] = host.encode()
                scope["headers"] = list(headers.items())

        await self.app(scope, receive, send)
