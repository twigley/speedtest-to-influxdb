# Speedtest to influxdb

This repository contains code for a script that runs the [Ookla Speedtest CLI](https://www.speedtest.net/apps/cli) and sends the data to an [InfluxDBv2](https://github.com/influxdata/influxdb) instance.

![Grafana dashboard showing speed test results](/assets/dashboard.jpg)

## Requirements
Script can be ran standalone or within a container.
Running within the container provides the environment required, primarily the speedtest-cli itself.

### InfluxDB Token

This script makes use of token authentication which can be created following the docs here https://docs.influxdata.com/influxdb/v2/admin/tokens/create-token/ 

## Docker

Image is available from ```ghcr.io/twigley/speedtest-to-influxdb:latest```

or build locally:

```
docker build ./ -t speedtesttoinflux
docker run speedtesttoinflux
```

## Standalone
### Linux
Tested in debian/ubuntu but should work for most modern distros.
- Python 3
- curl
- git

1. Clone this repo
2. Install Speedtest CLI as below
```
> curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash
```
3. Run as below
```
> pip install uv

> uv sync --frozen

> uv run main.py

```

### Windows
You can do this but it's a pain, you'll need as above:
- Python 3
- Git

1. Clone this repo

2. Download the speedtest cli from https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-win64.zip

3. Place the executable within the root of this repo

```
> pip install uv

> uv sync --frozen

> uv run main.py
```

# Configuration

All configuration is handled via environment variables:

| Variable | Default | Info |
| ----------- | ----------- | ----------- |
| DB_ADDRESS | localhost | InfluxDB Address|
| DB_PORT | 8086 | InfluxDB port |
| DB_TOKEN | MyTestAdminToken0== | InfluxDB token |
| DB_ORG | default | InfluxDB organisation |
| DB_BUCKET | default | InfluxDB bucket|
| TEST_INTERVAL | 30m | Repeat test every TEST_INTERVAL (s, m, h, d for seconds, minutes etc.) |
| RUN_ONCE | False | Run test once and exit, no schedule |
| LOG_LEVEL | INFO | Log level one of [ DEBUG, INFO, WARNING, ERROR, CRITICAL ] |