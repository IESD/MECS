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
apt install -y python3-smbus      # For i2c bus provision
apt install -y i2c-tools         # For i2c bus comms
apt install -y pigpio            # For "bit banging" second i2c bus and direct python control of gpio pins
apt install -y libatlas-base-dev # for numpy blas issues
apt install -y nginx             # For data transfer over local wifi
apt install -y hostapd            # for hosting access point
apt install -y dnsmasq           # basic domain name lookup
apt install -y ufw

# 3. Clone the git repo (or pull if it already exists)
repo="https://github.com/IESD/MECS.git"
folder="MECS"
if [ ! -d "$folder" ] ; then
    git clone "$repo" "$folder"
else
    cd "$folder"
    git pull $repo
    cd ..
fi

# 4. Prepare python
# 4a. pip install some annoying dependencies
pip3 install numpy
pip3 install pandas
pip3 install pigpio

# 4b. Install MECS
cd "$folder"
python3 setup.py install
cd ..

# 4c. Prepare configuration
sudo -u pi cp MECS/MECS.ini.template ./MECS.ini
sudo -u pi mkdir logs
sudo -u pi cp MECS/devices/ac.json ./ac_devices.json
sudo -u pi cp MECS/devices/dc.json ./dc_devices.json

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

# 4i configure waveshare chat script for GPRS connection (for ppp to use)
# TODO : must copy the files from working Pi and put them here to be copied.

# 5. register service definitions with systemd
cp MECS/services/mecs-generate.service /etc/systemd/system
cp MECS/services/ppp.service /etc/systemd/system
cp MECS/services/hwclock-start.service /etc/systemd/system
cp MECS/services/waveshare-gpio.service /etc/systemd/system

# 6. enable services
systemctl enable mecs-generate
systemctl enable ppp
systemctl enable nginx
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl enable pigpiod
systemctl enable waveshare-gpio

# 7. install crontabs
# specify pi user for the pi user cron
sudo -u pi crontab MECS/cron/pi.cron
crontab MECS/cron/root.cron

# 8. copy scripts to /usr/local/bin
# Copy the waveshare setup script to /usr/local/bin
cp MECS/scripts/waveshare_gpio_init.sh /usr/local/bin/
chmod 777 /usr/local/bin/waveshare_gpio_init.sh

# 9. reboot
reboot

# Initialise the MECS board name and match the Wifi name to it
# sudo mecs-init?
# Fold that into mecs-init?
# sudo sed -i 's/ssid=.*/ssid=NewMECSWifiID/g' /etc/hostapd/hostapd.conf

#Initialise the Real Time Clock (RTC)
hwclock -w  # Writes the system time to the RTC.  Note Pi *must* be synced to real time somehow to make this work
apt-get -y remove fake-hwclock
update-rc.d -f fake-hwclock remove
systemctl disable fake-hwclock
systemctl enable hwclock-start

# lock down the firewall : TODO check that outgoing is always allowed on all interfaces (particularly ppp0)
ufw allow in on eth0 to any port 22 # Allows SSH access only on ethernet (i.e. wire connected)
ufw allow in on wlan0 to any port 80 # Allows HTTP requests on WiFi
ufw allow in on wlan0 to any port 443 # Allows HTTPS requests on WiFi
ufw allow in on wlan0 to any port 53 # Allows DNS requests on WiFi (enables use of "https://mecs.data" instead of raw IP
ufw allow in on wlan0 to any port 67 # Allows DHCP to get IP when device connects to Access Point.
ufw enable
