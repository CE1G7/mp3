FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
RUN echo "hello from fog" > index.html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "http.server", "8080"]
