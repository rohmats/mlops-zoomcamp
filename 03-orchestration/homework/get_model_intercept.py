import argparse

import mlflow

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model-uri", type=str, help="The model uri to load", required=True)
    args = p.parse_args()
    mlflow.set_tracking_uri("http://localhost:5012")
    mlflow.set_experiment("nyc-taxi-analysis")

    skmodel = mlflow.sklearn.load_model(f"runs:/{args.model_uri}/artifacts")
    print(f"The model intercept is {skmodel.intercept_}")
