FROM python:3.10.9-slim

RUN pip install -U pip & pip install pipenv

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy
RUN pip install click

# Set up AWS credentials
RUN mkdir -p /root/.aws
RUN echo "[default]\naws_access_key_id = dummyAccessKeyId\naws_secret_access_key = dummySecretAccessKey" > /root/.aws/credentials
RUN echo "[default]\nregion = us-east-1" > /root/.aws/config

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME=World

COPY [ "batch.py", "batch.py" ]
COPY [ "model.bin", "model.bin" ]

ENTRYPOINT [ "python", "batch.py" ]