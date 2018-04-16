# Requirements #
This software requires the following packages be installed on your RPi:
* ratpoison
* ImageMagick
* python-raspberry-gpio
* python2-pyserial
* python2-numpy
* python2-pyglet
* xorg-server
* xorg-apps
* xorg-xset

These are the names of pacman Arch Linux packages but should closely correspond to the package names on other distributions.

# Setup #
1. Use the following for your `.xinitrc` to autostart ratpoison:

```bash
#!/bin/sh
xset s off -dpms
exec /usr/bin/ratpoison
```

2. Use the following for your `.ratpoisonrc` to autostart the rpi-display unit:

```bash
exec bash -c 'exec /home/jstarr/rpi-display/run.py'
```

you may have to change the above path depending on where you install this software.

3. Configure your shell run command to auto-start X:

```bash
if [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
  exec startx
fi
```

4. Enable communication over the serial GPIO pins by following [this guide](http://logicalgenetics.com/serial-on-raspberry-pi-arch-linux/).

# Links #

## Setup ##
* [Arch Linux Raspberry Pi Setup Guide](https://github.com/phortx/Raspberry-Pi-Setup-Guide)
* [Arch Linux Arm: Raspberry Pi](https://archlinuxarm.org/platforms/armv6/raspberry-pi)

## Login ##
* [Automatic Login to Virtual Console](https://wiki.archlinux.org/index.php/getty#Automatic_login_to_virtual_console)
* [Autostart X at Login](https://wiki.archlinux.org/index.php/Xinit#Autostart_X_at_login)

## Xorg ##
* [Modifying DPSM using xset](https://wiki.archlinux.org/index.php/Display_Power_Management_Signaling#Modifying_DPMS_and_screensaver_settings_using_xset)
* [xbacklight](https://wiki.archlinux.org/index.php/backlight#xbacklight)

## Ratpoison ##
* [Ratpoison Colon Commands](https://www.nongnu.org/ratpoison/doc/Other-Commands.html)
* [Ratpoison Arch Wiki](https://wiki.archlinux.org/index.php/Ratpoison)

## Serial ##
* [RPi3 UART Configuration](https://www.raspberrypi.org/documentation/configuration/uart.md)
* [Serial on RPi Arch Linux](http://logicalgenetics.com/serial-on-raspberry-pi-arch-linux/)
