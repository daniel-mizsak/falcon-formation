# Set basic image data
FROM python:3.12-slim
LABEL org.opencontainers.image.source=https://github.com/daniel-mizsak/falcon-formation
LABEL org.opencontainers.image.description="Create evenly distributed hockey teams."
LABEL org.opencontainers.image.licenses=MIT

ENV LANG=C.UTF-8
ENV TZ=Europe/Copenhagen

# Copy files
WORKDIR /workspace
COPY dist/*.tar.gz .
COPY gunicorn.conf.py .

# Install python packages
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./*.tar.gz

# Run command
EXPOSE 80
CMD ["gunicorn", "--config", "gunicorn.conf.py", "falcon_formation.server:server"]
