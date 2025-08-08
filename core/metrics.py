from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Metrics
REQUEST_COUNT = Counter(
    "adf_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("adf_request_duration_seconds", "Request duration")
AI_REQUESTS = Counter("adf_ai_requests_total", "AI model requests", ["model", "status"])
SECURITY_EVENTS = Counter(
    "adf_security_events_total", "Security events", ["event_type"]
)


class MetricsMiddleware:
    """Middleware to collect metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        # Get request info
        method = scope["method"]
        path = scope["path"]

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time

                # Record metrics
                REQUEST_COUNT.labels(
                    method=method, endpoint=path, status=status_code
                ).inc()
                REQUEST_DURATION.observe(duration)

            await send(message)

        await self.app(scope, receive, send_wrapper)


def get_metrics():
    """Return Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
