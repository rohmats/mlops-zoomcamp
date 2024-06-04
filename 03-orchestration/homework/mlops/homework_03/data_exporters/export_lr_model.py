import os
import pickle

import mlflow

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_model_to_mlflow(data, *args, **kwargs):
    """
    Log our model and vectorizer to mlflow.

    Args:
        data: The output from the upstream parent block
    """
    # Specify your data exporting logic here
    lr, dv = data
    os.makedirs("models", exist_ok=True)
    with open("models/dict_vectorizer.b", "wb") as f_out:
        pickle.dump(dv, f_out)

    experiment_name = kwargs.get("experiment_name")
    mlflow.set_tracking_uri("http://mlflow:5012")
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run():
        mlflow.sklearn.log_model(lr, "artifacts")
        mlflow.log_artifact("models/dict_vectorizer.b", artifact_path="preprocessor")
