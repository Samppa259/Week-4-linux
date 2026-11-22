
#!/bin/bash

# Website backup settings
SOURCE="/var/www/html/"
DESTINATION="ubuntu@192.168.1.186:/srv/backups/website/"
SSH_KEY="/home/ubuntu/.ssh/id_ed25519_backup"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG="/home/ubuntu/backup-website.log"

# Create timestamped backup on Server B
rsync -a \
    -e "ssh -i $SSH_KEY" \
    "$SOURCE" \
    "${DESTINATION}${TIMESTAMP}/" \
    >> "$LOG" 2>&1

# Record result
if [ $? -eq 0 ]; then
    echo "$(date): Backup successful: $TIMESTAMP" >> "$LOG"
else
    echo "$(date): ERROR: Backup failed: $TIMESTAMP" >> "$LOG"
fi

