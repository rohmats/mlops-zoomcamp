import datetime
import logging
import os
import time
from calendar import monthrange
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
import psycopg
import typer
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    ColumnQuantileMetric,
    ColumnSummaryMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.report import Report
from joblib import load
from rich.logging import RichHandler
from rich.progress import track
from rich.traceback import install
from sklearn.linear_model import LinearRegression
from typing_extensions import Annotated
from utils import read_dataframe

# Sets up the logger to work with rich
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()


num_features = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
cat_features = ["PULocationID", "DOLocationID"]
column_mapping = ColumnMapping(
    target=None,
    prediction="prediction",
    numerical_features=num_features,
    categorical_features=cat_features,
)
SEND_TIMEOUT = 10

password = os.getenv("HW5_PASS")
create_table_statement = """
drop table if exists hw_metrics;
create table hw_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float,
    fare_amount_median float,
    prediction_std float
)
"""


def extract_metric_data(result: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
    """Extract the numbers relevant to each metric

    Args:
        result (Dict[str, Any]): The result dict from evidently

    Returns:
        Dict[str, Union[int, float, str]]: A dictionary of the metrics
    """
    result_metrics = {}
    metrics = result["metrics"]
    result_metrics["prediction_drift"] = metrics[0]["result"]["drift_score"]
    result_metrics["num_drifted_columns"] = metrics[1]["result"][
        "number_of_drifted_columns"
    ]
    result_metrics["share_missing_values"] = metrics[2]["result"]["current"][
        "share_of_missing_values"
    ]
    result_metrics["fare_amount_median"] = metrics[3]["result"]["current"]["value"]
    result_metrics["prediction_std"] = metrics[4]["result"]["current_characteristics"][
        "std"
    ]
    return result_metrics


def insert_row_into_table(curr: psycopg.Cursor, row: Dict[str, Any], table_name: str):
    """Insert a given row into the PostgreSQL table

    Args:
        curr (psycopg.Cursor): The current cursor
        row (Dict[str, Any]): The row to insert
        table_name (str): The table into which to insert the row
    """
    ks = row.keys()
    fields = ", ".join(ks)
    values = [row[k] for k in ks]
    pls = ", ".join(["%s"] * len(ks))
    sql_cmd = f"insert into {table_name}({fields}) values ({pls})"
    curr.execute(sql_cmd, values)


def compute_metrics(
    current_data: pd.DataFrame, ref_data: pd.DataFrame
) -> Dict[str, Union[int, float]]:
    """Compute metrics on the current data using Evidently

    Args:
        current_data (pd.DataFrame): The current data
        ref_data (pd.DataFrame): Reference data

    Returns:
        Dict[str, Union[int, float]]: Dict of the most important metrics
    """

    # Generate the report
    report = Report(
        metrics=[
            ColumnDriftMetric(column_name="prediction"),
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
            ColumnQuantileMetric(column_name="fare_amount", quantile=0.5),
            ColumnSummaryMetric(column_name="prediction"),
        ]
    )
    report.run(
        reference_data=ref_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )
    result = report.as_dict()
    # Extract the metric results
    metrics = extract_metric_data(result)
    return metrics


def prep_db():
    with psycopg.connect(
        f"host=localhost port=5432 user=postgres password={password}", autocommit=True
    ) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(
            f"host=localhost port=5432 dbname=test user=postgres password={password}"
        ) as conn:
            conn.execute(create_table_statement)


def get_current_data(
    data: pd.DataFrame, model: LinearRegression, begin: datetime.datetime, i: int
) -> pd.DataFrame:
    """Return the data on a daily cadence, including the model prediction.

    Args:
        data (pd.DataFrame): The data for the new month
        model (LinearRegression): The linear regression sklearn model
        begin (datetime.datetime): Start of the month data
        i (int): The current day, as an integer from the start of the month

    Returns:
        pd.DataFrame: The data for the given day
    """
    current_data = data[
        (data.lpep_pickup_datetime >= (begin + datetime.timedelta(i)))
        & (data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))
    ]

    # Predict on current data
    current_data["prediction"] = model.predict(
        current_data[num_features + cat_features].fillna(0)
    )
    return current_data


def main(
    data_file: Annotated[
        str, typer.Option(help="File containing the new data", default=...)
    ],
    ref_data_file: Annotated[
        str, typer.Option(help="File containing the reference data", default=...)
    ],
    model_file: Annotated[
        str, typer.Option(help="The file with the model")
    ] = "models/lin_reg.bin",
    year: Annotated[
        int, typer.Option(help="The year corresponding to new data")
    ] = 2024,
    month: Annotated[int, typer.Option(help="The month corresponding to new data")] = 3,
):
    # Load the data
    logger.info("Loading data")
    data = read_dataframe(data_file)
    ref_data = read_dataframe(ref_data_file)

    # Load the model
    logger.info("Loading model")
    model = load(model_file)

    # Figure out the the start date and length of month
    begin = datetime.datetime(year, month, 1, 0, 0)
    ndays = monthrange(year, month)[1]

    all_res = []
    logger.info("Starting analysis")
    # Prepare the database
    prep_db()
    with psycopg.connect(
        f"host=localhost port=5432 dbname=test user=postgres password={password}",
        autocommit=True,
    ) as conn:

        last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)

        # Loop over all the days of the given month
        for i in track(range(0, ndays), "Processing data..."):
            # Get the data for the current day, including model prediction
            current_data = get_current_data(data, model, begin, i)

            # Compute the metrics
            res = compute_metrics(current_data, ref_data)
            res["timestamp"] = begin + datetime.timedelta(i)

            # Insert things into the sql database
            with conn.cursor() as curr:
                insert_row_into_table(curr, res, "hw_metrics")

            all_res.append(res["fare_amount_median"])

            # This is here to *simulate* new data coming in,
            # by sending the records for each day with a delay
            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)

    all_res = np.array(all_res)
    print(
        f"The maximum daily median for fare_amount for {month}/{year} is {np.amax(all_res)}"
    )


if __name__ == "__main__":
    typer.run(main)