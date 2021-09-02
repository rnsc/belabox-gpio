#!/usr/bin/python3

from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import time
import signal
import urllib.request
import urllib.parse
from pathlib import Path
import json

btn_pin = 15

delay = 0.5
rapid_fire_delay = 3.0
bounce = 500
last_press_time = time.time() + rapid_fire_delay


def exit_handler(sig, frame):
  #lcd = CharLCD('PCF8574', 0x27)
  #lcd.clear()
  GPIO.cleanup()
  print('\r')

def belacoder_toggle():
  print('belacoder toggle')
  req = urllib.request.Request('http://localhost/status')
  try:
    with urllib.request.urlopen(req) as response:
      status = response.read().decode('utf-8')
      print("Is encoder started? ", status)
  except urllib.error.URLError as e:
    print(e.reason)

  if status == 'false':
    print("Starting encoder")
    file_handle = open(str(Path.home())+'/belaUI/config.json')
    belaUI_config = json.load(file_handle)
    form_data = urllib.parse.urlencode(belaUI_config).encode()
    req = urllib.request.Request('http://localhost/start', form_data)
    try:
      with urllib.request.urlopen(req) as response:
        start_result = response.read().decode('utf-8')
      print(start_result)
    except urllib.error.URLError as e:
      print(e.reason)

  if status == 'true':
    print("Stopping encoder")
    form_data = urllib.parse.urlencode({}).encode()
    req = urllib.request.Request('http://localhost/stop', form_data)
    try:
      with urllib.request.urlopen(req) as response:
        stop_result = response.read().decode('utf-8')
      print(stop_result)
    except urllib.error.URLError as e:
      print(e.reason)

def pressed(channel):
  global btn_pin
  global last_press_time
  counter = 0
  while True:
    time.sleep(delay)
    #print("GPIO input: ", GPIO.input(btn_pin))
    #print("counter: ", counter)
    #print("last_press_time: ", last_press_time)
    now = time.time()
    #print("time: ", now)
    #print("time diff: ", now-last_press_time)
    if ( now - last_press_time ) > rapid_fire_delay or ( now - last_press_time < 0 ):
      if GPIO.input(btn_pin) == 1:
        counter += 1
        if counter >= 6:
          last_press_time = time.time()
          print('long press')
          belacoder_toggle()
          break
      elif GPIO.input(btn_pin) == 0:
        last_press_time = time.time()
        #lcd_print("Short press")
        print('short press')
        break
    else:
      print('prevent rapid clics')
      return
    if counter >= 10:
      #lcd_print("Error on press")
      print('error on clic detection')
      break

def lcd_print(msg):
  lcd = CharLCD('PCF8574', 0x27)
  lcd.clear()
  lcd.backlight_enabled=False
  time.sleep(0.2)
  lcd.backlight_enabled=True
  lcd.write_string(msg)
  time.sleep(0.5)


def main():
  global btn_pin
  try:
    with open('/etc/belaboxgpio/belaboxgpio.json') as file_handle:
      config = json.load(file_handle)
      btn_pin = config['button_gpio_pin']
  except:
    print('Config file not present, default settings applied.')

  # Setting up GPIO
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  # Add event callback for button
  GPIO.add_event_detect(btn_pin, GPIO.RISING, callback=pressed, bouncetime=bounce)

  # Wait for SIGINT to exit
  signal.signal(signal.SIGINT, exit_handler)
  signal.pause()
