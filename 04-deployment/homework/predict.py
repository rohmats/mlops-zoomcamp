#!/usr/bin/env python
# coding: utf-8

import os
import pickle
import pandas as pd


with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)


categorical = ['PULocationID', 'DOLocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


year = 2023
month = 3
df = read_data(
    f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet"
)


dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = model.predict(X_val)


print(f"The standard deviation of the prediction is {y_pred.std()}")


df_result = pd.DataFrame()
ride_id = f"{year:04d}/{month:02d}_" + df.index.astype("str")
df_result["ride_id"] = ride_id
df["ride_id"] = ride_id
df_result["duration"] = y_pred


df_result.head()


prediction_name = f"prediction_{year}_{month}.parquet"
pred_dir = "predictions"
os.makedirs(pred_dir, exist_ok=True)
df_result.to_parquet(
    os.path.join(pred_dir, prediction_name),
    engine="pyarrow",
    compression=None,
    index=False,
)


print(
    f"The size of the prediction file is {os.path.getsize(os.path.join(pred_dir, prediction_name))/(1024**2)} MB"
)

