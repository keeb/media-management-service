#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check each service unit for its last run status
for timer in "$SCRIPT_DIR/units"/*.timer; do
    if [ -f "$timer" ]; then
        unit=$(basename "$timer" .timer)
        service_unit="$unit.service"
        
        # Check if the service failed on its last run
        if systemctl is-failed "$service_unit" >/dev/null 2>&1; then
            echo "$unit ❌"
        else
            echo "$unit ✅"
        fi
    fi
done