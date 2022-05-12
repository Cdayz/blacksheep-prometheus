import pytest
from blacksheep.server import Application
from blacksheep.server.responses import text
from blacksheep.testing import TestClient
from prometheus_client import REGISTRY, Counter

from blacksheep_prometheus import PrometheusMiddleware, use_prometheus_metrics


@pytest.fixture(scope="session")
def app():
    app_ = Application()
    use_prometheus_metrics(
        app_,
        middleware=PrometheusMiddleware(
            filter_paths=['/no-metrics'],
        ),
    )

    @app_.router.get('/aio')
    async def aio_text_response_ok(request):
        return text('test response')

    @app_.router.get('/text')
    def text_response_ok(request):
        return text('test response')

    @app_.router.get('/err')
    def exception(request):
        raise ValueError('test')

    @app_.router.get('/pp/{path}/{params}')
    def pp(path: str, params: str):
        return text(f'{path}/{params} called')

    @app_.router.get('/no-metrics')
    def no_metrics():
        return text('no metrics collected from that route')

    my_custom_metric = Counter('my_custom_metric', 'Custom metric', registry=REGISTRY)

    @app_.router.get('/custom-metrics')
    def custom_metrics():
        my_custom_metric.inc()
        return text('custom metrics also collected!')

    return app_


@pytest.fixture
@pytest.mark.asyncio
async def client(app: Application):
    await app.start()
    try:
        yield TestClient(app)
    finally:
        await app.stop()


@pytest.mark.asyncio
async def test_aio_text_view_ok(client: TestClient):
    await client.get('/aio')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/aio"} 1.0' in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/aio",status_code="200"} 1.0' in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/aio"} 0.0' in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text


@pytest.mark.asyncio
async def test_text_view_ok(client: TestClient):
    await client.get('/text')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/text"} 1.0' in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/text",status_code="200"} 1.0' in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/text"} 0.0' in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text


@pytest.mark.asyncio
async def test_custom_metrics_ok(client: TestClient):
    await client.get('/custom-metrics')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/custom-metrics"} 1.0' in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/custom-metrics",status_code="200"} 1.0' in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/custom-metrics"} 0.0' in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text

    # Custom metrics
    assert 'my_custom_metric_total 1.0' in metrics_text


@pytest.mark.asyncio
async def test_error_view(client: TestClient):
    await client.get('/err')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/err"} 1.0' in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/err",status_code="500"} 1.0' in metrics_text
    assert 'blacksheep_exceptions_total{exception_type="ValueError",method="GET",path="/err"} 1.0' in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/err"} 0.0' in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text


@pytest.mark.asyncio
async def test_path_parameters(client: TestClient):
    await client.get('/pp/test1/test2')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/pp/test1/test2"} 1.0' in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/pp/test1/test2",status_code="200"} 1.0' in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/pp/test1/test2"} 0.0' in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text


@pytest.mark.asyncio
async def test_filter_paths(client: TestClient):
    await client.get('/no-metrics')

    metrics_response = await client.get('/metrics/')
    metrics_text = await metrics_response.text()

    # Requests
    assert 'blacksheep_requests_total{method="GET",path="/no-metrics"} 1.0' not in metrics_text

    # Responses
    assert 'blacksheep_responses_total{method="GET",path="/no-metrics",status_code="200"} 1.0' not in metrics_text

    # Requests in progress
    assert 'blacksheep_requests_in_progress{method="GET",path="/no-metrics"} 0.0' not in metrics_text
    assert 'blacksheep_requests_in_progress{method="GET",path="/metrics/"} 1.0' in metrics_text
