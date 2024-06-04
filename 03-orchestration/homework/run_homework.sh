#!/bin/bash

# Do all the necessary runs to answer questions for homework 3
# Note that in Q3 one is required to look to the UI and then
# interrupt to continue

# Function to print a nicer header
header() {
    echo $1
    printf '=%.0s' {1..80}
    echo
}

echo "Beginning HW 3"

# Use a custom port for convenience
MLFLOW_PORT=5012

# Q1
header "Question 1"
echo "We are running mage version v0.9.70"

# Q2
header "Question 2"
nlines=$(cat mlops/homework_03/metadata.yaml  | wc -l)
echo "The number of lines in the metadata file is ${nlines}"



# Q3
header "Question 3"
echo "Running the data preparation pipeline"
# First we run the data preparation pipeline
curl -X POST http://localhost:6789/api/pipeline_schedules/19/pipeline_runs/e915d5aaa09f4e1984eaffb849839ec2   --header 'Content-Type: application/json'
# Wait for it to finish
echo "Waiting 30 seconds for the pipeline to finish"
sleep 30
# Now get the rows
nrows=$(curl -s --location 'http://localhost:6789/api/pipelines/data_preparation/blocks/ingest' | jq '.block.outputs[0].shape[0]')

echo "The number of rows in our data is ${nrows}"

# Q4
header "Question 4"
nrows_processed=$(curl -s --location 'http://localhost:6789/api/pipelines/data_preparation/blocks/prepare' | jq '.block.outputs[0].shape[0]')

echo "The number of rows after processing is ${nrows_processed}"

# Q5
header "Question 5"
echo "Running the training pipeline"
# Run the training pipeline
curl -X POST http://localhost:6789/api/pipeline_schedules/20/pipeline_runs/93d00aa4ae324b0495552f7d6b68645c   --header 'Content-Type: application/json'
# Wait for pipeline to finish
echo "Waiting 140 seconds for the training pipeline to finish"
sleep 140

# Get the run_id from mlflow

run_id=$(curl -s -X POST "http://localhost:${MLFLOW_PORT}/api/2.0/mlflow/runs/search" -H "Content-Type: application/json" -d '{"experiment_ids":["1"],"max_results":1}' | jq -r '.runs[0].info.run_id')

echo "The run ID in mlflow is ${run_id}"

# Now get the model intercept. For this we have to load the model

python get_model_intercept.py --model-uri=${run_id}

# Q6
header "Question 6"
# Extract the model size info

msize=$(curl -s -X GET "http://localhost:${MLFLOW_PORT}/api/2.0/mlflow/runs/get?run_id=${run_id}" | jq -c '.run.data.tags | .[] | select(.key | contains("history")) .value | fromjson | .[0].model_size_bytes')
echo "The size of the model is ${msize} bytes"
