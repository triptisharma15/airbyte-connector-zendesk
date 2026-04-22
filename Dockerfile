# airbyte-cdk 7.x requires Python >= 3.10. The older airbyte/python-connector-base:1.1.0
# ships Python 3.9, which cannot install those wheels (pip: "No matching distribution").
FROM docker.io/library/python:3.11-slim-bookworm

WORKDIR /airbyte/integration_code

RUN pip install --no-cache-dir --upgrade "pip>=24.0"

COPY main.py manifest.yaml setup.py requirements.txt ./
COPY source_declarative_manifest ./source_declarative_manifest

RUN pip install --no-cache-dir .

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-zendesk-custom
