FROM python:3.10

RUN pip install -U pip
RUN pip install uv 

COPY [ "requirements.txt",  "./" ]

RUN uv pip install --system --no-cache -r requirements.txt

COPY [ "batch.py", "batch.py" ]
COPY [ "model.bin", "model.bin" ]

ENTRYPOINT [ "python", "batch.py" ]