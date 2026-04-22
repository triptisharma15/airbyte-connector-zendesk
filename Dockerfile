FROM docker.io/airbyte/python-connector-base:1.1.0

WORKDIR /airbyte/integration_code

COPY main.py manifest.yaml setup.py requirements.txt ./
COPY source_declarative_manifest ./source_declarative_manifest

RUN pip install --no-cache-dir .

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-zendesk-custom
