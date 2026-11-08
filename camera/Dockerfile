FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY camera/camera.py ./camera/
COPY camera/bigcat.jpg ./camera/
COPY camera/smallcat.jpg ./camera/
COPY shared/util.py ./shared/

WORKDIR /app/camera