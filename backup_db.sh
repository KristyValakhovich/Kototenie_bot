#!/bin/bash
BACKUP_DIR="/opt/date-ideas-bot/backups"
DB_FILE="/opt/date-ideas-bot/date_ideas.db"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/date_ideas_$DATE.db"
find $BACKUP_DIR -type f -name "*.db" -mtime +30 -delete