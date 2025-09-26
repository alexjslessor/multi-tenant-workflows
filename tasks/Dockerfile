FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app

ADD requirements.txt .

COPY pyproject.toml ./

RUN pip install .

COPY . .

EXPOSE ${PORT}

CMD uvicorn api.app:app --host 0.0.0.0 --port ${PORT} --loop uvloop --lifespan on
