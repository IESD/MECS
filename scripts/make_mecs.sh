#!/bin/bash

#This is the script recipe to make a mecs Pi from nothing

# 0. Exit if user is not root
if (( $EUID != 0 )); then
    echo "Please run as root (using sudo is fine)"
    exit
fi

# 1. modprobe setup
modprobe w1-gpio
modprobe w1-therm

# 2. apt-get install stuff
apt install git
apt install python3-pip
apt install python-smbus
apt install i2c-tools

# 3. Clone the git repo
git clone https://github.com/IESD/MECS.git

# 4. Prepare python
# 4a. pip install some annoying dependencies
pip3 install numpy
pip3 install pandas
pip3 install matplotlib

# 4b. Install MECS
cd MECS
python3 setup.py install
cd ..

# 4c. Prepare configuration
cp MECS/MECS.ini.template ./MECS.ini
cp MECS/calibration.ini.template ./calibration.ini

# 5. register service definitions with systemd
cp MECS/services/mecs-generate.service /etc/systemd/system
# cp MECS/services/waveshare-gpio.service /etc/systemd/system

# 6. enable services
systemctl enable mecs-generate
# systemctl enable waveshare-gpio

# 7. install crontabs
# specify pi user for the pi user cron
sudo -u pi crontab MECS/cron/pi.cron
crontab MECS/cron/root.cron

# 8. copy scripts to /usr/local/bin
# Copy the waveshare setup script to /usr/local/bin
# cp MECS/waveshare_gpio_init.sh /usr/local/bin/
# chmod 777 /usr/local/bin/waveshare_gpio_init.sh

# 9. reboot
