echo "17" > /sys/class/gpio/export
sleep 0.1
echo "out" > /sys/class/gpio/gpio17/direction
echo "0" > /sys/class/gpio/gpio17/value
