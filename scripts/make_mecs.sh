#!/bin/bash

#This is the script recipe to make a mecs Pi from nothing

# 0. Exit if user is not root
if (( $EUID != 0 )); then
    echo "Please run as root (using sudo is fine)"
    exit
fi

# 1. modprobe setup

# 2. apt-get install stuff

# 3. copy scripts to /usr/local/bin
# Copy the waveshare setup script to /usr/local/bin
cp ./waveshare_gpio_init.sh /usr/local/bin/
chmod 777 /usr/local/bin/waveshare_gpio_init.sh

# 4. Prepare python
# 4a. pip install some annoying dependencies
pip3 install numpy
pip3 install pandas

# 4b. Install MECS
python3 setup.py install

# 5. register service definitions with systemd
cp ../services/* /etc/system.d/system

# 6. enable services
systemctl enable mecs-generate.service
systemctl enable waveshare-gpio.service

# 7. install crontabs
# specify pi user for the pi user cron
sudo -u pi crontab ../cron/pi.cron
crontab ../cron/root.cron

# 8. reboot
