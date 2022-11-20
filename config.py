import os

DEVICE_UID = os.environ['DEVICE_UID']
SMS_X_RAPID_API_KEY = os.environ['RAPID_API_KEY']
SMS_X_RAPID_API_HOST = os.environ['RAPID_API_HOST']

SMS_CONTENT_TYPE = "application/x-www-form-urlencoded"
SMS_JSON = 1
SMS_P = "0rE3sBlF2qqdzXxkdvs6SRnAH2zdZLM5fpllnCQmBLRcuqpm7HQpzQGUh0kkZ7KD"

SMS_HEADERS = {
    "content-type":     SMS_CONTENT_TYPE,
	"X-RapidAPI-Key":   SMS_X_RAPID_API_KEY,
	"X-RapidAPI-Host":  SMS_X_RAPID_API_HOST
}


WEEKDAYS = { 0 : "monday",
             1 : "tuesday",
             2 : "wednesday",
             3 : "thursday",
             4 : "friday",
             5 : "saturday",
             6 : "sunday" }

PINS = {"Button"            : 4,
        "ControlLedGreen"   : 2, 
        "ControlLedRed"     : 3,
        "MedLedYellow"      : 26, 
        "MedLedBlue"        : 19, 
        "MedLedGreen"       : 13, 
        "MedLedRed"         : 6}

INTERVAL = 30