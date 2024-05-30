# This is my personal repo for MLOps Zoomcamp from DataTalksClub
> Course repository [link](https://github.com/DataTalksClub/mlops-zoomcamp)

## Ch. 2 Experiment Tracking
<details>
    <summary>Details</summary>

### Create environment
``` bash
conda create --name exp-tracking-env python=3.9
```

### Activate experiment tracking environment
``` bash
conda activate exp-tracking-env
```

### Change to directory
```bash
cd 02-experiment-tracking
```
### Install requirements.txt
```bash
pip install -r requirements.txt
```

### Run MLFlow
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.sqlite
```
</details>
