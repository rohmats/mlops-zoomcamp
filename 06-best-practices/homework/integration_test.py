import pandas as pd
from datetime import datetime
import os

from batch import get_input_path


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1))
]

columns_test_df = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
test_df = pd.DataFrame(data, columns=columns_test_df)

s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
options = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}

input_file = get_input_path(2023, 1)
test_df.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)
print(f'File saved to S3, input_file is {input_file}')
