FROM ghcr.io/astral-sh/uv:python3.13-alpine

LABEL maintainer="Tom Wigley" \
    description="Speedtest cli ingestion of stats into influxdb"

ENV UV_COMPILE_BYTECODE=1

RUN wget https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz speedtest -q -O - | tar xzvf - -C /bin

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "main.py"]