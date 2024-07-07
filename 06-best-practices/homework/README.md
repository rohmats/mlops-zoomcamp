Activate environment
```
pipenv shell
```

First build the image with the batch model:

```bash
docker build -t hw6 .
```

Build and launch the community `localstack` image that will act as S3:

```bash
docker compose up -d --build
```

Make the bucket to store our results as thought we are on S3:

```bash
aws --endpoint-url="http://localhost:4566" s3 mb s3://nyc-duration
```
Make sure to set the end-point url env var:
```bash
export S3_ENDPOINT_URL="http://localhost:4566"
```



Now you can run the unit and integration tests as 

```bash
pytest -vvv tests
```
and

```bash
python tests/integration_test.py --env-file tests/env.json
```

You can also run the integration test "manually" by running[^1]:

```bash
docker run --network=host -e S3_ENDPOINT_URL="http://localhost:4566" -e INPUT_FILE_PATTERN="test_input_{year:04d}-{month:02d}.parquet"  -e OUTPUT_FILE_PATTERN="test_otuput_{year:04d}-{month:02d}.parquet" -e AWS_ACCESS_KEY_ID=foo -e AWS_SECRET_ACCESS_KEY=bar -e AWS_DEFAULT_REGION=us-east-1 hw6_integration --year 2024 --month 1
```