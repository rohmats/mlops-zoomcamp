## Getting the model for deployment from MLflow

* Take the code from the previous video
* Train another model, register with MLflow
* Put the model into a scikit-learn pipeline
* Model deployment with tracking server
* Model deployment without the tracking server

Starting the MLflow:

```bash
mlflow ui --port 8080 --backend-store-uri sqlite:///mlflow.sqlite
```

Downloading the artifact

```bash
export MLFLOW_TRACKING_URI="http://127.0.0.1:8080"
export MODEL_RUN_ID="3c55362ba332448e95ccf981547f7eaa"

mlflow artifacts download \
    --run-id ${MODEL_RUN_ID} \
    --artifact-path model \
    --dst-path .
```