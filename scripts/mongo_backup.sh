#!/bin/bash

DATE=$(date +%Y-%m-%d)

# SSH to the VPS server and run mongodump
ssh hostinger << EOF
docker exec falcon-formation-mongo-1 mongodump \
    --username "${MONGO_USERNAME}" \
    --password "${MONGO_PASSWORD}" \
    --archive="/mongo_backup/${DATE}.gz" \
    --gzip

sudo cp /deploy/falcon-formation/mongo_backup/${DATE}.gz /backup/falcon-formation/${DATE}.gz

rclone sync /backup r2:vps/current --backup-dir r2:vps/archive/${DATE}
EOF
