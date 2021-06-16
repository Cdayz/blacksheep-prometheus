# Blacksheep Prometheus

[![Build Status](https://github.com/Cdayz/blacksheep-prometheus/workflows/Continuous%20Integration/badge.svg)](https://github.com/Cdayz/blacksheep-prometheus/actions)[![codecov](https://codecov.io/gh/Cdayz/blacksheep-prometheus/branch/master/graph/badge.svg?token=YJTGKBTQSE)](https://codecov.io/gh/Cdayz/blacksheep-prometheus)

## Introduction

Prometheus integration for Blacksheep.

## Requirements

* Python 3.6+
* Blacksheep 1.0.7+

## Installation

```console
$ pip install blacksheep-prometheus
```

## Usage

A complete example that exposes prometheus metrics endpoint under `/metrics/` path.

```python
from blacksheep.server import Application
from blacksheep_prometheus import PrometheusMiddleware, metrics

app = Application()

app.middlewares.append(PrometheusMiddleware())
app.router.add_get('/metrics/', metrics)
```

## Contributing

This project is absolutely open to contributions so if you have a nice idea, create an issue to let the community 
discuss it.
