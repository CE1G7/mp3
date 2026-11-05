FROM python:3.12-alpine
RUN apk add --no-cache curl
WORKDIR /srv
RUN echo "hello from cloud" > index.html
CMD ["python", "-m", "http.server", "8080"]