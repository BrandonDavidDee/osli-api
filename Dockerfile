FROM tiangolo/uvicorn-gunicorn:python3.11-slim

COPY requirements.txt app/requirements.txt

COPY ./app /app/app

RUN pip install --upgrade pip

RUN pip install -r app/requirements.txt

EXPOSE 80
