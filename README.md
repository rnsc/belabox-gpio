# Belabox GPIO

## Purpose

This repository aims at providing a simple Python package that can be used to control the belabox software.
<https://github.com/BELABOX/>

### Disclaimer

This is an independant project from BELABOX and they're not responsible for any support regarding this piece of software.
I also will do limited support, this software requires that you're knowledgeable enough to install a button or an I2C LCD screen on your GPIO.

## Features

v0.1.1:

* Supports a button connected on your Jetson nano GPIO.
* The button can be used to start and stop your encoder via a long press.
  * The button itself just sends a command to toggle the current status that you'd find in belaUI.

Unreleased:

* Display information regarding the Jetson nano and belabox on an I2C 16x2 LCD screen.
* Cycle through information with single short presses on the button.

## Installation

```shell
sudo apt install -y python3-setuptools python3-pip
sudo pip3 install https://github.com/rnsc/belabox-gpio/releases/download/v0.1.0/belaboxgpio-0.1.0-py3-none-any.whl
```

The package has requirements that'll get installed automatically.
They are listed in `src/requirements.txt`.

## Configuration file

The `belaboxgpio` command expects a JSON configuration file (`/etc/belaboxgpio/belaboxgpio.json`), if this file is not available, the program will revert to default settings.
The default button PIN on the GPIO will be PIN 15.

## Install it as a SystemD service

```shell
sudo cp belaboxgpio.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo mkdir /etc/belaboxgpio
sudo cp belaboxgpio.json /etc/belaboxgpio
```

Once you've updated the configuration file (`/etc/belaboxgpio/belaboxgpio.json`) with your desired PIN number for you button, you can start the service:

```shell
sudo systemctl start belaboxgpio
```
