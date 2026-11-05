FROM python:3.12-alpine
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
ENV LOG_FILE=/logs/all.jsonl
CMD ["python", "app.py"]
