#!/bin/bash

set -e

echo "Installing all systemd units from units/ directory..."

# Copy all unit files
sudo cp units/*.service units/*.timer /etc/systemd/system/ 2>/dev/null || true

# Reload systemd
sudo systemctl daemon-reload

# Enable and start all timers (they will handle the services)
for timer in units/*.timer; do
    if [ -f "$timer" ]; then
        unit=$(basename "$timer")
        echo "Enabling and starting $unit"
        sudo systemctl enable "$unit"
        sudo systemctl start "$unit"
    fi
done

echo "All units installed and enabled!"