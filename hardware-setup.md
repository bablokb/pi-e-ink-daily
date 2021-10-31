Hardware Setup
==============

E-inks are ideal for battery-based projects, otherwise there is no
justification for the extra cost and missing functionality of these displays
(except the fact that they are reflective, you can keep them running
at night without beeing disturbed).

Battery-based projects usually run at specified intervals or by manual
request. The Pi boots, updates the display and shuts down again. Since the
Pi is not equipped with circuity for this task, you need some more
or less simple external components for it (depending on your needs).

You can find a simple circuit/pcb for the necessary battery-management
[here](https://github.com/bablokb/pcb-pi-batman):

![](min-pcb-3d.png)

The circuit uses a flip-flop to manage the current-supply from the battery
to the Pi. A prerequisite is a DC-DC converter with an enable pin. The
button (or an external device) turns on the Pi by pulling the enable pin high.
The Pi itself turns of the current after shutdown by pulling the enable
pin low again.

Adafruit has other nice solutions for this, e.g. an enable timer button
(works the same way, but powers on every two hours or shorter), or a
pushbutton power-switch.


Hardware
--------

The minimal list of required hardware is short:

  - a Raspberry Pi Zero-W
  - an Inky-wHAT or Inky-Impression from Pimoroni

Since the e-ink displays only expose GPIO4 (besides I2C and SPI), I
soldered long pins to the Pi Zero-W to have pins on both sides, so
every pin not used by the display is available from the back.

Optional components:

  - a LiPo battery
  - a DC-DC converter (e.g. a PowerBoost 500C from Adafruit)
  - battery-management pcb (see above)
  - 3D-printed [stand](https://www.tinkercad.com/things/f5TTT5WoGkW)
  - or a 3D-printed [frame](https://www.tinkercad.com/things/1BvKeof9mrh)

Average power-requirement is 115mA (measured for the wHat), so the
update-cycle draws 2mAh from the battery. A normal 1200mAh LiPo should
therefore last at least a year with a daily update.

If you use an Inky-Impression, have a look into the sub-directory
[Inky-Impression-Frame](Inky-Impression-Frame/Readme.md).
The directory contains the STL-files for a complete slim frame
for the Impression together with some images of my actual setup.


