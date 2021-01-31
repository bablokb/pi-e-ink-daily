#!/bin/bash
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# This script checks the value of GPIO24 and exits with return code 3 if low.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

# pin to check, must also be set in /boot/config.txt (see tools/install)
PIN_ADMIN="24"

# configure pin
if [ ! -d /sys/class/gpio/gpio$PIN_ADMIN ]; then
  echo "$PIN_ADMIN" > /sys/class/gpio/export
  echo "in"  > /sys/class/gpio/gpio$PIN_ADMIN/direction
fi
logger -t "pi-e-ink-daily" "checking GPIO$PIN_ADMIN"

val=$(cat /sys/class/gpio/gpio$PIN_ADMIN/value)
logger -t "pi-e-ink-daily" "GPIO$PIN_ADMIN is $val"
if [ "$val" -eq 0 ]; then
  exit 3
else
  exit 0
fi
