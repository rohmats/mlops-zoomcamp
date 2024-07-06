#!/usr/bin/env python
# coding: utf-8

import logging
import os
import pickle
from typing import List

import pandas as pd
import typer
from rich.logging import RichHandler
from rich.traceback import install
from typing_extensions import Annotated

# Sets up the logger to work with rich
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()


S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")


def prepare_data(df: pd.DataFrame, categorical: List[str]) -> pd.DataFrame:
    df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df["duration"] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype("int").astype("str")
    return df


def save_data(df: pd.DataFrame, filename: str, bucket: str = None):
    if S3_ENDPOINT_URL is not None:
        options = {"client_kwargs": {"endpoint_url": S3_ENDPOINT_URL}}
        output_file = f"s3://{bucket}/{filename}"
        df = df.to_parquet(
            output_file,
            engine="pyarrow",
            compression=None,
            index=False,
            storage_options=options,
        )
    else:
        output_file = "{filename}.parquet"
        df = pd.to_parquet(
            output_file,
            engine="pyarrow",
            compression=None,
            index=False,
        )


def read_data(filename: str, categorical: List[str], bucket: str) -> pd.DataFrame:
    if S3_ENDPOINT_URL is not None:
        options = {"client_kwargs": {"endpoint_url": S3_ENDPOINT_URL}}

        df = pd.read_parquet(f"s3://{bucket}/{filename}", storage_options=options)
    else:
        df = pd.read_parquet(filename)

    df = prepare_data(df, categorical)

    return df


def get_input_path(year: int, month: int) -> str:
    default_input_pattern = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
    input_pattern = os.getenv("INPUT_FILE_PATTERN", default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year: int, month: int) -> str:
    default_output_pattern = "s3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet"
    output_pattern = os.getenv("OUTPUT_FILE_PATTERN", default_output_pattern)
    return output_pattern.format(year=year, month=month)


def main(
    year: Annotated[int, typer.Option(help="Year to use", default=...)],
    month: Annotated[int, typer.Option(help="Month to use", default=...)],
):

    logger.info("Getting the input and output paths")
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    logger.info("Loading model")
    with open("model.bin", "rb") as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ["PULocationID", "DOLocationID"]
    bucket = "nyc-duration"
    logger.info("Reading data")
    df = read_data(input_file, categorical, bucket)
    df["ride_id"] = f"{year:04d}/{month:02d}_" + df.index.astype("str")
    logger.info("Using model to predict")
    dicts = df[categorical].to_dict(orient="records")
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print("Predicted mean duration:", y_pred.mean())

    df_result = pd.DataFrame()
    df_result["ride_id"] = df["ride_id"]
    df_result["predicted_duration"] = y_pred
    print(df_result["predicted_duration"].sum())
    logger.info(f"Saving data to {output_file}")
    # df_result.to_parquet(output_file, engine="pyarrow", index=False)
    save_data(df_result, output_file, bucket=bucket)


if __name__ == "__main__":
    typer.run(main)
