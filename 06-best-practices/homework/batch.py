#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import pandas as pd


def get_s3_options():
    if os.getenv("S3_ENDPOINT_URL"):
        options = {
            'client_kwargs': {
            'endpoint_url': os.getenv("S3_ENDPOINT_URL")
            }
        }
    return options
    return None


def read_data(path: str):
    options = get_s3_options() if path.startswith("s3://") else None
    return pd.read_parquet(path, storage_options=options)


def save_data(path: str, df: pd.DataFrame):
    options = get_s3_options() if path.startswith("s3://") else None
    df.to_parquet(path, engine='pyarrow', index=False, storage_options=options)


def prepare_data(df: pd.DataFrame, categorical: list):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


def get_input_path(year: int, month: int):
    default_input_pattern = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year: int, month: int):
    default_output_pattern = 's3://nyc-duration/yellow/{year:04d}/{month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def main(year: int, month: int):
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)
    categorical = ['PULocationID', 'DOLocationID']
    df = prepare_data(read_data(input_file), categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print('Predicted mean duration:', y_pred.mean())
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    
    save_data(output_file, df_result)


if __name__ == "__main__":
    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    except IndexError:
        try:
            os.environ["INPUT_FILE_PATTERN"]
        except KeyError:
            print("Enter two arguments: year month")
            sys.exit(1)
    main(year, month)
