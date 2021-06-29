#!/bin/bash

#This is the script recipe to make a mecs Pi from nothing

# 0. Exit if user is not root
if (( $EUID != 0 )); then
    echo "Please run as root (using sudo is fine)"
    exit
fi

# 1. modprobe setup

# 2. apt-get install stuff
apt install git
apt install python3-pip

# 2a. Clone the git repo
git clone https://github.com/IESD/MECS.git

# 4. Prepare python
# 4a. pip install some annoying dependencies
pip3 install numpy
pip3 install pandas

# 4b. Install MECS
python3 MECS/setup.py install

# 5. register service definitions with systemd
cp MECS/services/* /etc/system.d/system

# 6. enable services
systemctl enable mecs-generate.service
systemctl enable waveshare-gpio.service

# 7. install crontabs
# specify pi user for the pi user cron
sudo -u pi crontab MECS/cron/pi.cron
crontab MECS/cron/root.cron

# 8. copy scripts to /usr/local/bin
# Copy the waveshare setup script to /usr/local/bin
cp MECS/waveshare_gpio_init.sh /usr/local/bin/
chmod 777 /usr/local/bin/waveshare_gpio_init.sh

# 9. reboot
