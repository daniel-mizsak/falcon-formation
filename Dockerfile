# Set basic image data
FROM python:3.12-slim
LABEL org.opencontainers.image.source https://github.com/daniel-mizsak/falcon-formation

ENV LANG=C.UTF-8
ENV TZ=Europe/Copenhagen

# Copy files
WORKDIR /workspace
COPY dist/*.tar.gz .
COPY run_server.py .

# Install python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ./*.tar.gz

# Run command
CMD ["python", "run_server.py"]
