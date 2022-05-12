from typing import Optional

from blacksheep.server import Application

from .middleware import PrometheusMiddleware
from .view import metrics


def use_prometheus_metrics(
    app: Application,
    *,
    endpoint: str = "/metrics/",
    middleware: Optional[PrometheusMiddleware] = None,
) -> None:
    """
    Configures the given application to use Prometheus and provide services that can be
    injected in request handlers.
    """
    middleware = middleware or PrometheusMiddleware()
    app.middlewares.append(middleware)
    app.router.add_get(endpoint, metrics)


__all__ = [
    'use_prometheus_metrics',
    'PrometheusMiddleware',
]
