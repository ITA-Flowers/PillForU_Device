from time import sleep
import datetime as dt
import requests
import json
import RPi.GPIO as GPIO

import config as cfg

# API Calls
def get_dosages() -> list:
  dosages = []
    
  url = "http://192.168.0.10:8080/dosages"

  payload = json.dumps({
    "device_uid": cfg.DEVICE_UID
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  dosages = response.json()
    
  return dosages

def delete_dosage(id : str):    
  url = "http://192.168.0.10:8080/dosages"

  payload = json.dumps({
    "id": int(id)
  })
  headers = {
    'Content-Type': 'application/json'
  }

  print(f'Deleting dosage: {id}')
  response = requests.request("DELETE", url, headers=headers, data=payload)
  print(f'CODE: {response.status_code}\n')
  
def get_user_phone_numbers_by_uuid(uuid : str):
  url = "http://192.168.0.10:8080/users"

  payload = json.dumps({
    "uuid": uuid
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  if response.status_code == 200:
    phone_number = response.json()['phone_number']
  else:
    phone_number = None
  
  return phone_number

def get_user_login_by_uuid(uuid : str):
  url = "http://192.168.0.10:8080/users"

  payload = json.dumps({
    "uuid": uuid
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  if response.status_code == 200:
    login = response.json()['login']
  else:
    login = None
  
  return login

def send_sms(to : str, text : str):
  to = "+48" + to
  
  print(f'Sending SMS [{text}] to: {to}')
  
  to = to.replace('+', '%2B')
  text = text.replace(' ', '%20')
  
  url = "https://sms77io.p.rapidapi.com/sms"
  payload = f"to={to}&p={cfg.SMS_P}&text={text}&json={cfg.SMS_JSON}"
  request_method = 'POST'
  
  REQUEST = f'{request_method} / {url}?{payload}'
  
  response = requests.request(request_method, url, data=payload, headers=cfg.SMS_HEADERS)
  
  
# Data analysis
def until_date_expired(until_date : str, today : str) -> bool:
  # 2022-12-31
  yearU, monthU, dayU = until_date.split('-')
  yearT, monthT, dayT = today.split('-')
  
  if yearU < yearT:
    return True
  
  elif yearU > yearT:
    return False
  
  # the same year
  if monthU < monthT:
    return True
  
  elif monthU > monthT:
    return False
  
  # the same month
  if dayU < dayT:
    return True
    
  return False

def its_a_time(when_time : str, now : str) -> bool:
  hoursE, minutesE, secondsE = when_time.split(':')
  hoursN, minutesN, secondsN = now.split(':')
    
  if int(hoursE) < int(hoursN):
    return True
  
  elif int(hoursE) == int(hoursN):
    if int(minutesE) <= int(minutesN):
      return True
  
  return False

def its_a_good_day(when_day : str, weekday : str) -> bool:
  return when_day == weekday


# GPIO
def led_on(led_pin : int):
  GPIO.output(led_pin, GPIO.HIGH)
  
def led_off(led_pin : int):
  GPIO.output(led_pin, GPIO.LOW)

def led_blink(led_pin : int, count : int):
  for _ in range(count):
    led_on(led_pin)
    sleep(0.5)
    
    led_off(led_pin)
    sleep(0.5)

def button_callback(channel):
  if len(dosages_signal) > 0:
    dosage = dosages_signal.pop(0)
    med_name, pills_count = dosage['med_name'], dosage['pills_count']
    
    print(f'\t{med_name} : {pills_count}')

    if med_name == 'Polopiryna':
      led_blink(cfg.PINS['MedLedYellow'], pills_count)
    elif med_name == 'Witaminki':
      led_blink(cfg.PINS['MedLedBlue'], pills_count)
    elif med_name == 'Strepsilsik':
      led_blink(cfg.PINS['MedLedGreen'], pills_count)
    elif med_name == 'Apap':
      led_blink(cfg.PINS['MedLedRed'], pills_count)

    caretaker_phone_number = get_user_phone_numbers_by_uuid(dosage['caretaker_uuid'])
    pupil_login = get_user_login_by_uuid(dosage['pupil_uuid'])
    
    text = f"Your pupil '{pupil_login}' has already took '{pills_count}' pills of '{med_name}'."
    
    send_sms(caretaker_phone_number, text)
    
    delete_dosage(dosage['id'])
    
    if len(dosages_signal) == 0:
      led_off(cfg.PINS['ControlLedRed'])
      led_on(cfg.PINS['ControlLedGreen'])

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(cfg.PINS['Button'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(cfg.PINS['ControlLedGreen'], GPIO.OUT)
    GPIO.setup(cfg.PINS['ControlLedRed'], GPIO.OUT)
    GPIO.setup(cfg.PINS['MedLedYellow'], GPIO.OUT)
    GPIO.setup(cfg.PINS['MedLedBlue'], GPIO.OUT)
    GPIO.setup(cfg.PINS['MedLedGreen'], GPIO.OUT)
    GPIO.setup(cfg.PINS['MedLedRed'], GPIO.OUT)
    
    GPIO.output(cfg.PINS['ControlLedGreen'], GPIO.HIGH)
    GPIO.output(cfg.PINS['ControlLedRed'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedYellow'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedBlue'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedGreen'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedRed'], GPIO.LOW)

    GPIO.add_event_detect(cfg.PINS['Button'], GPIO.RISING, callback=button_callback)

    GPIO.setwarnings(True)

def gpio_clean_up():
    GPIO.output(cfg.PINS['ControlLedGreen'], GPIO.LOW)
    GPIO.output(cfg.PINS['ControlLedRed'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedYellow'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedBlue'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedGreen'], GPIO.LOW)
    GPIO.output(cfg.PINS['MedLedRed'], GPIO.LOW)
       
    GPIO.cleanup()


# Main Loop
def loop():
  global dosages_signal
  dosages_signal = []
  
  while True:
    dosages_signal = []
    dosages = get_dosages()

    if len(dosages) > 0:
      today, now = dt.datetime.today().strftime('%Y-%m-%d|%H:%M:%S').split('|')
      weekday = cfg.WEEKDAYS[dt.datetime.today().weekday()]

      for dosage in dosages:
        until_date = dosage['until_date']
        when_time = dosage['when_time']
        when_day = dosage['when_day']

        if until_date_expired(until_date, today):
           delete_dosage(dosage["id"])

        else:
          if its_a_good_day(when_day, weekday):
            if its_a_time(when_time, now):
              dosages_signal.append(dosage)

      if len(dosages_signal) > 0:
        led_off(cfg.PINS['ControlLedGreen'])
        led_on(cfg.PINS['ControlLedRed'])
        
        for dosage in dosages_signal:
          pupil_phone_number = get_user_phone_numbers_by_uuid(dosage['pupil_uuid'])

          if pupil_phone_number is not None:
            med_name, pills_count = dosage['med_name'], dosage['pills_count']
            text = f"Time to take '{pills_count}' pills of '{med_name}'."
            send_sms(pupil_phone_number, text)
                   
    sleep(cfg.INTERVAL)


if __name__ == '__main__':
  try:
    print('-- Power on --')
    print('-- GPIO init --')
    gpio_init()
    
    print('-- Starting work --\n' + 20 * '--' + '\n')
    loop()
    
  except KeyboardInterrupt:
    print('\n-- Manual turn off --')
    
  except Exception as why:
    print(20 * '--')
    print('-- Error --')
    raise why
  
  finally:
    print(20 * '--')  
    gpio_clean_up()
    print('-- Power off --')
