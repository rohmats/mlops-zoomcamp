import pandas as pd
from datetime import datetime
import numpy as np

from batch import prepare_data


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def prepare_test_data():
    data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1))
    ]

    columns_test_df = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    test_df = pd.DataFrame(data, columns=columns_test_df)

    categorical = ['PULocationID', 'DOLocationID']

    prepared_test_df, categorical = prepare_data(test_df, categorical)
    print(prepared_test_df)

    expected_prepared_test_df = [
        ('-1', '-1', 9.),
        ('1', '1', 8.),
    ]
    columns_expected_df = ['PULocationID', 'DOLocationID', 'duration']
    expected_prepared_test_df = pd.DataFrame(expected_prepared_test_df, columns=columns_expected_df)

    catigorial_cols = ['PULocationID', 'DOLocationID']
    for col in catigorial_cols:
        assert (prepared_test_df[col] == expected_prepared_test_df[col]).all()

    float_cols = ['duration']
    epsilon = 1e-9
    for col in float_cols:
        np.allclose(prepared_test_df[col], expected_prepared_test_df[col], atol=epsilon)