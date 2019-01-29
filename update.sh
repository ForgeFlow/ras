#!/bin/bash

say 'UPDATING FIRMWARE RAS ***************************************************'
# Stop ras-portal service
systemctl stop ras-portal
systemctl disable ras-portal
rm /lib/systemd/system/ras-portal.service
systemctl daemon-reload
# Update ras-launcher service
sed -i "/^WorkingDirectory/c\WorkingDirectory=\/home\/pi\/ras" /lib/systemd/system/ras-launcher.service
sed -i '/^ExecStart/c\ExecStart=\/usr\/bin\/python3 launcher.py' /lib/systemd/system/ras-launcher.service
