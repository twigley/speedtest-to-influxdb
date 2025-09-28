import json
import subprocess
import os
import logging
import time

from schedule import every, repeat, run_pending, idle_seconds, run_all
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=os.environ.get("LOG_LEVEL", "INFO"),
)

DB_ADDRESS = os.environ.get("DB_ADDRESS", "localhost")
DB_PORT = os.environ.get("DB_PORT", 8086)
DB_TOKEN = os.environ.get("DB_TOKEN", "MyTestAdminToken0==")
DB_ORG = os.environ.get("DB_ORG", "default")
DB_BUCKET = os.environ.get("DB_BUCKET", "default")
TEST_INTERVAL = int(os.environ.get("TEST_INTERVAL", 10))
RUN_ONCE = eval(os.environ.get("RUN_ONCE", "False").title())


def format_json_to_influx(jsondata: str) -> list[dict]:
    data = json.loads(jsondata)
    influx_data = [
        {
            "measurement": "ping",
            "time": data["timestamp"],
            "fields": {
                "jitter": float(data["ping"]["jitter"]),
                "latency": float(data["ping"]["latency"]),
            },
        },
        {
            "measurement": "download",
            "time": data["timestamp"],
            "fields": {
                "bandwidth": data["download"]["bandwidth"],
                "bytes": data["download"]["bytes"],
                "elapsed": data["download"]["elapsed"],
                "latency_high": float(data["download"]["latency"]["high"]),
                "latency_low": float(data["download"]["latency"]["low"]),
                "jitter": float(data["download"]["latency"]["jitter"]),
            },
        },
        {
            "measurement": "upload",
            "time": data["timestamp"],
            "fields": {
                "bandwidth": data["upload"]["bandwidth"],
                "bytes": data["upload"]["bytes"],
                "elapsed": data["upload"]["elapsed"],
                "latency_high": float(data["upload"]["latency"]["high"]),
                "latency_low": float(data["upload"]["latency"]["low"]),
                "jitter": float(data["upload"]["latency"]["jitter"]),
            },
        },
        {
            "measurement": "packetLoss",
            "time": data["timestamp"],
            "fields": {"packetLoss": float(data.get("packetLoss", 0.0))},
        },
    ]
    return influx_data


def init_db() -> InfluxDBClient:
    client = InfluxDBClient(
        url=f"http://{DB_ADDRESS}:{DB_PORT}", token=f"{DB_TOKEN}", org=f"{DB_ORG}"
    )
    influxdb_ping(client.ping())
    return client


def influx_write(client: InfluxDBClient, data) -> None:
    with client as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(DB_BUCKET, DB_ORG, data)
        try:
            client.write_api(write_options=SYNCHRONOUS).write(DB_BUCKET, DB_ORG, data)
        except InfluxDBError as e:
            logging.error("InfluxDB: Caught InfluxDBError: ", e.message)


def influxdb_ping(ping: bool) -> None:
    if not ping:
        raise ValueError(f"InfluxDB: Failed to ping database {DB_ADDRESS}:{DB_PORT}")
    else:
        logging.info("InfluxDB: ready")


@repeat(every(TEST_INTERVAL).minutes)
def run_speedtest() -> None:
    dbclient = init_db()

    speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"],
        capture_output=True,
        text=True,
    )

    if speedtest.returncode == 0:  # Speedtest was successful.
        logging.info("Speedtest successful")
        influx_data = format_json_to_influx(speedtest.stdout)
        logging.info(influx_data)
        influx_write(dbclient, influx_data)
    else:  # Speedtest failed.
        logging.error("Speedtest failure")
        logging.error(speedtest.stderr)
        logging.info(speedtest.stdout)

    dbclient.close()


def main() -> None:
    if RUN_ONCE:
        logging.info(f"Run once mode")
        run_all()
    else:
        while 1:
            n = idle_seconds()
            if n is None:
                # no more jobs
                break
            elif n > 0:
                # sleep exactly the right amount of time
                logging.info(f"Sleeping for {n}")
                time.sleep(n)
            run_pending()


if __name__ == "__main__":
    logging.info("Starting speedtest....")
    main()
