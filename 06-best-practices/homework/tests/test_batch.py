from datetime import datetime

import pandas as pd
import pytest
from batch import prepare_data


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


@pytest.fixture
def example_input():
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
    df = pd.DataFrame(data, columns=columns)
    return df


def test_prepare_data(example_input):
    categorical = ["PULocationID", "DOLocationID"]
    actual_data = prepare_data(example_input, categorical)
    tmp = [("-1", "-1", dt(1, 1), dt(1, 10), 9.0), ("1", "1", dt(1, 2), dt(1, 10), 8.0)]
    columns = [
        "PULocationID",
        "DOLocationID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "duration",
    ]
    expected_data = pd.DataFrame(tmp, columns=columns)
    assert actual_data.equals(expected_data)
