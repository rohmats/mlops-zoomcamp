import os
import pickle
import click

import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)

@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)

def run_train(data_path: str):

        mlflow.set_tracking_uri("sqlite:///hw2.sqlite")
        mlflow.set_experiment("homework-2")
        mlflow.sklearn.autolog()

        with mlflow.start_run():

            mlflow.set_tag("type", "homework")
            mlflow.set_tag("model", "rf-regressor")

            X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
            X_valid, y_valid = load_pickle(os.path.join(data_path, "val.pkl"))

            rf = RandomForestRegressor(max_depth=10, random_state=0)
            rf.fit(X_train, y_train)
            y_pred = rf.predict(X_valid)

            rmse = mean_squared_error(y_valid, y_pred, squared=False)


if __name__ == '__main__':
    run_train()