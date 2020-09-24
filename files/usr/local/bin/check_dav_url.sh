#!/bin/bash
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Check availability of configured caldav-server
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

max_tries="${1:-10}"
server=$(sed -ne '/dav_url/s![^/]*//\([^/]*\)/.*!\1!p' /etc/pi-e-ink-daily.json)

let i=0
while [ $i -lt $max_tries ]; do
  ping -c 1 -W 1 "$server" 2>&1 1>/dev/null && exit 0
  let i+=1
done

exit 1
