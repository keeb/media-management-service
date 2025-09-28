# LLM Parser and Mover Service

## Systemd Installation

To install and enable the systemd units for running `run-remote.sh` every hour:

### 1. Copy the unit files to systemd directory (requires sudo)
```bash
sudo cp llm-parser-mover.service llm-parser-mover.timer /etc/systemd/system/
```

### 2. Reload systemd daemon
```bash
sudo systemctl daemon-reload
```

### 3. Enable and start the timer
```bash
sudo systemctl enable llm-parser-mover.timer
sudo systemctl start llm-parser-mover.timer
```

### 4. Check timer status
```bash
sudo systemctl status llm-parser-mover.timer
```

### 5. List all timers to verify it's running
```bash
sudo systemctl list-timers
```

### 6. To test the service manually (optional)
```bash
sudo systemctl start llm-parser-mover.service
```

### 7. To view logs
```bash
journalctl -u llm-parser-mover.service
```