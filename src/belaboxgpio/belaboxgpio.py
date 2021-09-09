#!/usr/bin/python3

from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import websocket

import time
import signal
import json
import threading

# GPIO vars
btn_pin = 15

delay = 0.5
rapid_fire_delay = 3.0
bounce = 500
last_press_time = time.time() + rapid_fire_delay

# BelaUI vars
stream_status = False

url = 'ws://localhost'
auth_obj = { "auth": {}}
status_obj = { "status" }
stop_obj = { "stop": 0 }

belaUI_config = {}

# WebSocket client handlers

def messageHandler(ws, message):
  global stream_status
  global belaUI_config
  json_msg = json.loads(message)
  #print(json_msg)
  for msg_type in json_msg:
    if msg_type == "status":
      stream_status = json_msg.get('status').get('is_streaming')
    if msg_type == "config":
        belaUI_config = json_msg.get('config')

def openHandler(ws):
  print('ws open')
  ws.send(json.dumps(auth_obj))

def errorHandler(ws, error):
  print('ws error')
  print(error)

def closeHandler(ws, close_status_code, close_msg):
  print('ws close')
  time.sleep(5)
  websocket_connect()

# WebSocket client init
websocket.enableTrace(False)
ws = websocket.WebSocketApp(url,
                            on_open=openHandler,
                            on_message=messageHandler,
                            on_error=errorHandler,
                            on_close=closeHandler
                            )

# Put the WebSocket in a Thread and reconnect on close
def websocket_connect():
  wst = threading.Thread(target=ws.run_forever)
  wst.daemon = True
  wst.start()

# GPIO functions

def exit_handler(sig, frame):
  #lcd = CharLCD('PCF8574', 0x27)
  #lcd.clear()
  print('SIGINT received')
  GPIO.cleanup()
  print('\r')

def belacoder_toggle(ws, stream_status):
  print('belacoder toggle')

  if stream_status == False:
    print("Starting encoder")
    start_obj = { "start": belaUI_config }
    ws.send(json.dumps(start_obj))

  if stream_status == True:
    print("Stopping encoder")
    ws.send(json.dumps(stop_obj))

def status_update():
  ws.send(json.dumps(auth_obj))

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
          belacoder_toggle(ws, stream_status)
          break
      elif GPIO.input(btn_pin) == 0:
        last_press_time = time.time()
        #lcd_print("Short press")
        print('short press')
        status_update()
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

  # Start WebSocket client
  websocket_connect()

  # Wait for SIGINT to exit
  signal.signal(signal.SIGINT, exit_handler)
  signal.pause()

if __name__ == "__main__":
  main()
