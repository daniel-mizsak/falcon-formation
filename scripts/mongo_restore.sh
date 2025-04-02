#!/bin/bash

DATE=$(date +%Y-%m-%d)

docker exec falcon-formation-mongo-1 mongorestore \
    --username "${MONGO_USERNAME}" \
    --password "${MONGO_PASSWORD}" \
    --archive="/mongo_backup/${DATE}.gz" \
    --gzip \
    --drop \
    --nsExclude="admin.*"
