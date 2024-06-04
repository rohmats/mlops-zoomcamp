from io import BytesIO

import pandas as pd
import requests


@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:
    """
    Return the NYC Yellow Cab data

    Returns:
        pd.DataFrame the desired data
    """
    # Specify your data loading logic here
    month = kwargs.get("month", 3)
    year = kwargs.get("year", 2023)
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
    r = requests.get(url)
    if r.ok:
        df = pd.read_parquet(BytesIO(r.content))
    else:
        raise Exception(r.text)

    print(f"The number of rows in the loaded data is {df.shape[0]}")
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
