#!/bin/bash

set -e

echo "Uninstalling all systemd units from units/ directory..."

# Stop and disable all timers first
for timer in units/*.timer; do
    if [ -f "$timer" ]; then
        unit=$(basename "$timer")
        echo "Stopping and disabling $unit"
        sudo systemctl stop "$unit" 2>/dev/null || true
        sudo systemctl disable "$unit" 2>/dev/null || true
    fi
done

# Stop and disable all services
for service in units/*.service; do
    if [ -f "$service" ]; then
        unit=$(basename "$service")
        echo "Stopping and disabling $unit"
        sudo systemctl stop "$unit" 2>/dev/null || true
        sudo systemctl disable "$unit" 2>/dev/null || true
    fi
done

# Remove all unit files
for unit in units/*.service units/*.timer; do
    if [ -f "$unit" ]; then
        name=$(basename "$unit")
        if [ -f "/etc/systemd/system/$name" ]; then
            echo "Removing /etc/systemd/system/$name"
            sudo rm -f "/etc/systemd/system/$name"
        fi
    fi
done

# Reload systemd
sudo systemctl daemon-reload

echo "All units uninstalled!"
