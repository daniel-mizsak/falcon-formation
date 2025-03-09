#!/bin/bash

BACKUP_DIRECTORY="/backup"
BACKUP_DATE=$(date +%Y-%m-%d)

docker exec falcon-formation-mongo-1 mongodump \
    --username "${MONGO_USERNAME}" \
    --password "${MONGO_PASSWORD}" \
    --archive="${BACKUP_DIRECTORY}/${BACKUP_DATE}.gz" \
    --gzip
