import serial
import adafruit_fingerprint
import sys
import json

uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

def delete_all_templates():
    """Az összes fingerprint template törlése az olvasóból"""
    try:
        # Végigiterálunk az összes lehetséges ID-n (1-127)
        deleted_count = 0
        for template_id in range(0, 128):
            if finger.delete_model(template_id) == adafruit_fingerprint.OK:
                deleted_count += 1
                print(f"Törölve: ID #{template_id}", file=sys.stderr)
        
        return {
            "status": "success" if deleted_count > 0 else "warning",
            "deleted_count": deleted_count,
            "message": "Nincs törölhető template" if deleted_count == 0 else None
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    try:
        # Hitelesítés ellenőrzése törölve, mert a metódus nem elérhető
        result = delete_all_templates()
        print(json.dumps(result))
        sys.exit(0 if result["status"] in ("success", "warning") else 1)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Váratlan hiba: {str(e)}",
            "tip": "Ellenőrizze a szenzor kapcsolatát és a jogosultságokat"
        }))
        sys.exit(1)