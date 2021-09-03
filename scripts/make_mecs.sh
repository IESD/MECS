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
apt update
apt install -y git
apt install -y python3-pip
apt install -y python-smbus      # For i2c bus provision
apt install -y i2c-tools         # For i2c bus comms
apt install -y libatlas-base-dev # for numpy blas issues
apt install -y nginx             # For data transfer over local wifi
apt install -y hostapd            # for hosting access point
apt install -y dnsmasq           # basic domain name lookup
apt install -y ufw

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
cp MECS/config/nginx.conf /etc/nginx/sites-available/default

# 4f configure hostapd
cp MECS/config/hostapd.conf /etc/hostapd/hostapd.conf

# 4g configure dhcpcd
cp MECS/config/dhcpcd.conf /etc/dhcpcd.conf

# 4h configure dhcpcd
cp MECS/config/dnsmasq.conf /etc/dnsmasq.conf

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
systemctl enable dnsmasq
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

# Initialise the MECS board name and match the Wifi name to it
# sudo mecs-init?
# Fold that into mecs-init?
# sudo sed -i 's/ssid=.*/ssid=NewMECSWifiID/g' /etc/hostapd/hostapd.conf

# lock down the firewall
ufw allow in on eth0 to any port 22
ufw allow in on wlan0 to any port 80
ufw allow in on wlan0 to any port 53
ufw enable
