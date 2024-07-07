#!/bin/bash

# Set environment variables
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"

# Run the test python script
python integration_test.py