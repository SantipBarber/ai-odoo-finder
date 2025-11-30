#!/bin/bash
# AI-OdooFinder - Install systemd service
# Run this script once to set up automatic startup on boot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="ai-odoo-finder"

echo "=== AI-OdooFinder: Installing systemd service ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (sudo)"
    exit 1
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SCRIPT_DIR/start_system.sh"
chmod +x "$SCRIPT_DIR/stop_system.sh"
chmod +x "$SCRIPT_DIR/status_system.sh"

# Copy service file to systemd
echo "Installing systemd service..."
cp "$SCRIPT_DIR/$SERVICE_NAME.service" /etc/systemd/system/

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service (start on boot)
echo "Enabling service to start on boot..."
systemctl enable $SERVICE_NAME

echo ""
echo "=== Installation complete ==="
echo ""
echo "Usage:"
echo "  systemctl status $SERVICE_NAME    # Check status"
echo "  systemctl start $SERVICE_NAME     # Start services"
echo "  systemctl stop $SERVICE_NAME      # Stop services"
echo "  systemctl restart $SERVICE_NAME   # Restart services"
echo "  journalctl -u $SERVICE_NAME       # View logs"
echo "  journalctl -u $SERVICE_NAME -f    # Follow logs"
echo ""
echo "The service will now start automatically on system boot."
echo ""
echo "To start the service now, run:"
echo "  systemctl start $SERVICE_NAME"
