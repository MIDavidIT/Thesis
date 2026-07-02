import serial
import adafruit_fingerprint
import time
import sys
import json

uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

def enroll_fingerprint():
    for attempt in range(1, 128):
        if finger.load_model(attempt) != adafruit_fingerprint.OK:
            template_id = attempt
            break
    else:
        print(json.dumps({"error": "Nincs elerheto ID"}))
        sys.exit(1)

    while finger.get_image() != adafruit_fingerprint.OK:
        pass

    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print(json.dumps({"error": "1. kep konvertalasa sikertelen"}))
        sys.exit(1)

    time.sleep(2)

    while finger.get_image() != adafruit_fingerprint.OK:
        pass

    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        print(json.dumps({"error": "2. kep konvertalasa sikertelen"}))
        sys.exit(1)

    if finger.create_model() != adafruit_fingerprint.OK:
        print(json.dumps({"error": "Sablon letrehozasa sikertelen"}))
        sys.exit(1)

    if finger.store_model(template_id) != adafruit_fingerprint.OK:
        print(json.dumps({"error": "Mentes sikertelen"}))
        sys.exit(1)

    print(json.dumps({"status": "success", "id": template_id}))

if __name__ == "__main__":
    try:
        enroll_fingerprint()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    