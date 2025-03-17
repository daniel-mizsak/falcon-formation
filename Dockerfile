# Builder Stage
FROM python:3.12-slim AS builder

WORKDIR /workspace

COPY src src
COPY pyproject.toml pyproject.toml
COPY LICENSE LICENSE
COPY README.md README.md

RUN pip install --upgrade pip && \
    pip install build && \
    python -m build


# Production Stage
FROM python:3.12-slim AS production

WORKDIR /workspace

LABEL org.opencontainers.image.source=https://github.com/daniel-mizsak/falcon-formation
LABEL org.opencontainers.image.description="Create evenly distributed hockey teams."
LABEL org.opencontainers.image.licenses=MIT

ENV LANG=C.UTF-8
ENV TZ=Europe/Copenhagen

COPY --from=builder /workspace/dist/*.tar.gz .
COPY gunicorn.conf.py gunicorn.conf.py

RUN pip install --upgrade pip && \
    pip install *.tar.gz && \
    rm *.tar.gz

EXPOSE 80
CMD ["gunicorn", "--config", "gunicorn.conf.py", "falcon_formation.server:server"]
