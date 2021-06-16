import time
from typing import Awaitable, Callable, List

from blacksheep.messages import Request, Response
from prometheus_client import REGISTRY, Counter, Gauge, Histogram


class PrometheusMiddleware:
    def __init__(
        self,
        requests_total_metric_name='blacksheep_requests_total',
        responses_total_metric_name='blacksheep_responses_total',
        request_time_seconds_metric_name='blacksheep_request_time_seconds',
        exceptions_metric_name='blacksheep_exceptions',
        requests_in_progress_metric_name='blacksheep_requests_in_progress',
        filter_paths: List[str] = [],
    ):
        self.filter_paths = filter_paths
        self.requests_total = Counter(
            requests_total_metric_name,
            'Total count of requests by method and path',
            ['method', 'path'],
            registry=REGISTRY,
        )
        self.responses_total = Counter(
            responses_total_metric_name,
            'Total count of responses by method path and status_code',
            ['method', 'path', 'status_code'],
            registry=REGISTRY,
        )
        self.request_time_seconds = Histogram(
            request_time_seconds_metric_name,
            'Histogram of request processing time by path (in seconds)',
            ['method', 'path'],
            registry=REGISTRY,
        )
        self.exceptions = Counter(
            exceptions_metric_name,
            'Total count of exceptions raised by path and exception type',
            ['method', 'path', 'exception_type'],
            registry=REGISTRY,
        )
        self.requests_in_progress = Gauge(
            requests_in_progress_metric_name,
            'Gauge of of requests by method and path currently being processed',
            ['method', 'path'],
            registry=REGISTRY,
        )

    async def __call__(self, request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
        method = request.method
        path = request.url.path.decode('utf-8')

        if path in self.filter_paths:
            return await handler(request)

        self.requests_in_progress.labels(method=method, path=path).inc()
        self.requests_total.labels(method=method, path=path).inc()

        before_time = time.perf_counter()

        try:
            response = await handler(request)
        except Exception as e:
            status_code = 500
            self.exceptions.labels(method=method, path=path, exception_type=type(e).__name__).inc()
            raise e from None
        else:
            status_code = response.status
            after_time = time.perf_counter()
            self.request_time_seconds.labels(method=method, path=path).observe(after_time - before_time)
        finally:
            self.responses_total.labels(method=method, path=path, status_code=status_code).inc()
            self.requests_in_progress.labels(method=method, path=path).dec()

        return response
