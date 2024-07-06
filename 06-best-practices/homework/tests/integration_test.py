import json
import os

import docker
import pandas as pd
import typer
from typing_extensions import Annotated

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

from datetime import datetime


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def write_to_s3(df_input, year=2024, month=1):
    input_file = f"s3://nyc-duration/test_input_{year:04d}-{month:02d}.parquet"
    options = {"client_kwargs": {"endpoint_url": S3_ENDPOINT_URL}}
    df_input.to_parquet(
        input_file,
        engine="pyarrow",
        compression=None,
        index=False,
        storage_options=options,
    )


def setup_fake_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),  # <1 minute
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),  # >1 hour
    ]

    columns = [
        "PULocationID",
        "DOLocationID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ]
    df_input = pd.DataFrame(data, columns=columns)
    write_to_s3(df_input)


def perform_integration_test(
    env_file: Annotated[
        str,
        typer.Option(help="File containing the environmental variables", default=...),
    ]
):
    setup_fake_data()
    client = docker.from_env()
    with open(env_file, "r") as fp:
        env_vars = json.load(fp)
    client.containers.run(
        "hw6_integration",
        command=["--year=2024", "--month=1"],
        environment=env_vars,
        network_mode="host",
    )


if __name__ == "__main__":
    typer.run(perform_integration_test)
