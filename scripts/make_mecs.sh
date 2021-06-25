#This is the script recipe to make a mecs Pi from nothing

# Copy the waveshare setup script to /usr/local/bin
cp ./waveshare_gpio_init.sh /usr/local/bin/
chmod 777 /usr/local/bin/waveshare_gpio_init.sh

# Copy service definitions into systemd folder to be registered
cp ../services/* /etc/system.d/system

# Enable services
systemctl enable mecs-generate.service
systemctl enable waveshare-gpio.service
