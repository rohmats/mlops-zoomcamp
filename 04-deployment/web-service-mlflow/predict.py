import os
import pickle

import mlflow
from flask import Flask, request, jsonify


# RUN_ID = os.getenv('RUN_ID')
RUN_ID = 'a82e85f4e96a4c91b50b5713979c3f71'

# logged_model = f'mlflow-artifacts:/5/a82e85f4e96a4c91b50b5713979c3f71/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
logged_model = 'runs:/087af0c88531400a8b427127b36431a7/model'
loaded_model = mlflow.pyfunc.load_model(logged_model)

model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
