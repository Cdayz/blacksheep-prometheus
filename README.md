# Blacksheep Prometheus

[![Build Status](https://github.com/Cdayz/blacksheep-prometheus/workflows/Continuous%20Integration/badge.svg)](https://github.com/Cdayz/blacksheep-prometheus/actions)
[![codecov](https://codecov.io/gh/Cdayz/blacksheep-prometheus/branch/master/graph/badge.svg?token=YJTGKBTQSE)](https://codecov.io/gh/Cdayz/blacksheep-prometheus)
[![Package Version](https://img.shields.io/pypi/v/blacksheep-prometheus?logo=PyPI&logoColor=white)](https://pypi.org/project/blacksheep-prometheus/)
[![PyPI Version](https://img.shields.io/pypi/pyversions/blacksheep-prometheus?logo=Python&logoColor=white)](https://pypi.org/project/blacksheep-prometheus/)

## Introduction

Prometheus integration for Blacksheep.

## Requirements

* Python 3.7+
* Blacksheep 1.0.7+

## Installation

```console
$ pip install blacksheep-prometheus
```

## Usage

A complete example that exposes prometheus metrics endpoint under default `/metrics/` endpoint.

```python
from blacksheep.server import Application
from blacksheep_prometheus import use_prometheus_metrics

app = Application()
use_prometheus_metrics(app)
```

### Options

| Option name                       | Description                                         | Default value                     |
|-----------------------------------|-----------------------------------------------------|-----------------------------------|
|`requests_total_metric_name`       | name of metric for total requests                   |`'backsheep_requests_total'`       |
|`responses_total_metric_name`      | name of metric for total responses                  |`'backsheep_responses_total'`      |
|`request_time_seconds_metric_name` | name of metric for request timings                  |`'backsheep_request_time_seconds'` |
|`exceptions_metric_name`           | name of metric for exceptions                       |`'backsheep_exceptions'`           |
|`requests_in_progress_metric_name` | name of metric for in progress requests             |`'backsheep_requests_in_progress'` |
|`filter_paths`                     | list of path's where do not need to collect metrics |`[]`                               |


### Custom metrics

blacksheep-prometheus will export all the prometheus metrics from the process, so custom metrics can be created by using the prometheus_client API.

*Example:*
```python
from prometheus_client import Counter
from blacksheep.server.responses import redirect

REDIRECT_COUNT = Counter("redirect_total", "Count of redirects", ("from_view",))

async def some_view(request):
    REDIRECT_COUNT.labels(from_view="some_view").inc()
    return redirect("https://example.com")
```

The new metric will now be included in the the `/metrics` endpoint output:
```
...
redirect_total{from_view="some_view"} 2.0
...
```

## Contributing

This project is absolutely open to contributions so if you have a nice idea, create an issue to let the community 
discuss it.
