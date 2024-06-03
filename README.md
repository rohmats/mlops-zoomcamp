# This is my personal repo for MLOps Zoomcamp from DataTalksClub
> Course repository [link](https://github.com/DataTalksClub/mlops-zoomcamp)
## Chapter 1 - Introduction
### Environment preparation
[![Watch the video](https://img.youtube.com/vi/MzcmWXYxi2s/hqdefault.jpg){:target="_blank"}](https://youtu.be/MzcmWXYxi2s)


## Chapter 2 - Experiment Tracking
### Create environment - GiHub Codespace
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


## Chapter 3 - Orchestration and ML Pipelines
### Clone mage repository
```bash
git clone https://github.com/mage-ai/mlops.git
cd mlops
```

### Launch mage
```bash
./scripts/start.sh
```
### Open mage
Open http://localhost:6789 in your browser.

<!-- ## Chapter X - XXX
### Subjudul