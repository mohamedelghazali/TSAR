# Local demonstration image. Pin the base image by digest for production builds.
FROM python:3.12.8-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --chown=10001:10001 app.py /app/app.py

USER 10001:10001
EXPOSE 8443
ENTRYPOINT ["python", "/app/app.py"]
