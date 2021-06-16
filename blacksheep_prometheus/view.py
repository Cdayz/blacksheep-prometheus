import os

from blacksheep.contents import Content
from blacksheep.messages import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector


def metrics(request: Request) -> Response:
    if "prometheus_multiproc_dir" in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(
        status=200,
        headers=None,
        content=Content(
            content_type=CONTENT_TYPE_LATEST.encode('utf-8'),
            data=generate_latest(registry),
        ),
    )
