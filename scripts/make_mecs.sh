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
modprobe i2c-dev

# 2. apt-get install stuff
apt install git
apt install python3-pip
apt install python-smbus      # For i2c bus provision
apt install i2c-tools         # For i2c bus comms
apt install libatlas-base-dev # for numpy blas issues
apt install nginx             # For data transfer over local wifi
apt instal hostapd            # for hosting access point
# apt install dnsmasq           # basic domain name lookup

# 3. Clone the git repo
git clone https://github.com/IESD/MECS.git

# 4. Prepare python
# 4a. pip install some annoying dependencies
pip3 install numpy
pip3 install pandas
pip3 install matplotlib   # matplotlib could be removed - its not used on the pi (yet)

# 4b. Install MECS
cd MECS
python3 setup.py install
cd ..

# 4c. Prepare configuration
sudo -u pi cp MECS/MECS.ini.template ./MECS.ini
sudo -u pi cp MECS/calibration.ini.template ./calibration.ini
sudo -u pi mkdir logs

#4d. Ensure i2c module is loaded and uart / i2c are enabled at boot
cp MECS/config/config.txt /boot/config.txt
grep -qxF "i2c-dev" /etc/modules || echo "i2c-dev" >> /etc/modules

# 4e. Configure nginx
cp MECS/config/nginx.conf /etc/nginx/sites-available/mecs.conf
ln -s /etc/nginx/sites-available/mecs.conf /etc/nginx/sites-enabled/mecs.conf

# 5. register service definitions with systemd
cp MECS/services/mecs-generate.service /etc/systemd/system
cp MECS/services/ppp.service /etc/systemd/system
# cp MECS/services/waveshare-gpio.service /etc/systemd/system

# 6. enable services
systemctl enable mecs-generate
systemctl enable ppp
systemctl enable nginx
systemctl unmask hostapd
systemctl enable hostapd
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
# reboot
