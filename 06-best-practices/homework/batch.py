#!/usr/bin/env python
# coding: utf-8

import warnings
import sys
import pickle
import pandas as pd
import click
import os

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')


def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)

def get_output_path(year, month):
    default_output_pattern = './output/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)

def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df, categorical

def read_data(year, month, categorical):
    options = {}
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    input_pattern = os.getenv('INPUT_FILE_PATTERN')
    input_file = get_input_path(year, month)

    if s3_endpoint_url and input_pattern:
        options['storage_options'] = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}
        df = pd.read_parquet(input_file, storage_options=options['storage_options'])
        print(f'Data loaded from S3, INPUT_FILE_PATTERN is {input_pattern}')
    else:
        print('else')
        df = pd.read_parquet(input_file)
        print(f'Data loaded from the internet, INPUT_FILE_PATTERN is {input_pattern}')
    return prepare_data(df, categorical)

def save_parquet_to_s3(output_file, df):
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN')
    options = {}
    if s3_endpoint_url and output_pattern:
        options['storage_options'] = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}
        df.to_parquet(output_file, engine='pyarrow', index=False, storage_options=options['storage_options'])
        print(f'File saved to S3, OUTPUT_FILE_PATTERN is {output_pattern}')
    else:
        df.to_parquet(output_file, engine='pyarrow', index=False)
        print(f'File saved locally, OUTPUT_FILE_PATTERN is {output_pattern}')


@click.command()
@click.option(
    '--year',
    type=int,
    required=True,
    help='Year of the trip data'
)
@click.option(
    '--month',
    type=int,
    required=True,
    help='Month of the trip data'
)
def main(year, month):
    with open('./model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    df, categorical = read_data(year, month, categorical = ['PULocationID', 'DOLocationID'])

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    output_file = get_output_path(year, month)
    save_parquet_to_s3(output_file, df_result)


if __name__ == '__main__':
    main()