# This is my personal repo for MLOps Zoomcamp from DataTalksClub
> Course repository [link](https://github.com/DataTalksClub/mlops-zoomcamp)

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

### Run MLFlow
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.sqlite
```