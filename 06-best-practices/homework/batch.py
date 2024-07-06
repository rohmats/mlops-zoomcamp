#!/usr/bin/env python
# coding: utf-8

import warnings
import sys
import pickle
import pandas as pd
import click

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')


def generate_output_file_path(year, month):
 return f'./output/yellow_tripdata_{year:04d}-{month:02d}.parquet'


def read_data(filename, categorical):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df, categorical

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

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    df, categorical = read_data(input_file, categorical = ['PULocationID', 'DOLocationID'])

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())


    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    output_file = generate_output_file_path(year, month)
    df_result.to_parquet(output_file, engine='pyarrow', index=False)


if __name__ == '__main__':
    main()