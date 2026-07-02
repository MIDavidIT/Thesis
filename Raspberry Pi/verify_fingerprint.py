import serial
import adafruit_fingerprint
import sys
import json

uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

def get_fingerprint():
    while True:
        i = finger.get_image()
        if i == adafruit_fingerprint.OK:
            break
        elif i == adafruit_fingerprint.NOFINGER:
            continue
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Hiba: Kép nem olvasható.", file=sys.stderr)
            return None

    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Hiba: Nem sikerült ujjelnyomat template-et készíteni.", file=sys.stderr)
        return None

    result = finger.finger_fast_search()
    if result == adafruit_fingerprint.OK:
        print(f"\n--- UJJLENYOMAT EREDMÉNY ---", file=sys.stderr)
        print(f"Státusz:   SIKERES ✅", file=sys.stderr)
        print(f"Szenzor ID:{finger.finger_id}", file=sys.stderr)
        print(f"Pontosság: {finger.confidence}", file=sys.stderr)
        print(f"----------------------------\n", file=sys.stderr)
        
        return {
            "status": "success",
            "match": True,
            "id": finger.finger_id,
            "confidence": finger.confidence
        }
    else:
        print(f"\n--- UJJLENYOMAT EREDMÉNY ---", file=sys.stderr)
        print(f"Státusz:   ELUTASÍTVA ❌", file=sys.stderr)
        print(f"Indok:     Nincs ilyen ujj a szenzor memóriájában", file=sys.stderr)
        print(f"----------------------------\n", file=sys.stderr)
        
        return {"status": "success", "match": False}

if __name__ == "__main__":
    try:
        match = get_fingerprint()
        if match:
            print(json.dumps(match))
        else:
            print(json.dumps({"status": "error", "message": "Nem sikerult az ujjlenyomatot beolvasni"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)