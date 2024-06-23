import logging

import pandas as pd
import pandera as pa
from rich.logging import RichHandler
from rich.traceback import install

# Sets up the logger to work with rich
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()

# Basic pandera validation schema for our data
schema = pa.DataFrameSchema(
    columns={
        "PULocationID": pa.Column(int, coerce=True),
        "DOLocationID": pa.Column(int, coerce=True),
        "passenger_count": pa.Column(int, pa.Check.ge(0), coerce=True),
        "trip_distance": pa.Column(float, pa.Check.ge(0.0)),
        "fare_amount": pa.Column(float),
        "total_amount": pa.Column(float),
        "duration": pa.Column(float, pa.Check.ge(0.0)),
    }
)


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Check that the features we care about are present
    and obey some basic sanity checks

    Args:
        df (pd.DataFrame): Raw data

    Returns:
        pd.DataFrame: Validated data
    """
    try:
        validated_df = schema(df)
    except pa.errors.SchemaError as exc:
        logger.error(exc)

        exit(-1)
    return validated_df


def read_dataframe(filename: str) -> pd.DataFrame:
    """Read in the NYC Taxi input data.
    Does some preprocessing. Note that unlike in previous
    HWs, this one:
    - includes all durations <=60 minutes
    - filters by passenger count
    - does not convert pickup and dropoff to categorical vars
    Args:
        filename (str): Name of file with data

    Returns:
        pd.DataFrame: The data in DataFrame form
    """
    df = pd.read_parquet(filename)

    df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 0) & (df.duration <= 60)]
    df = df[(df.passenger_count > 0) & (df.passenger_count <= 8)]
    validate_dataframe(df)

    return df