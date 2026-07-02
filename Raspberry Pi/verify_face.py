from picamera2 import Picamera2
import face_recognition
import cv2
import sys
import json
import argparse
import time
import os

parser = argparse.ArgumentParser(description='Arcfelismerő rendszer')
parser.add_argument("registered_image_path", help="Regisztrált arckép elérési útja")
args = parser.parse_args()

LIVE_IMAGE_PATH = "/tmp/live_face.jpg"

try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (1500, 1500)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    
    start_time = time.time()
    while time.time() - start_time < 3:
        frame = picam2.capture_array()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    final_frame = picam2.capture_array()
    if final_frame is not None:
        final_frame_bgr = cv2.cvtColor(final_frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(LIVE_IMAGE_PATH, final_frame_bgr)
    else:
        raise Exception("Nem sikerult kepet kesziteni")

    if not os.path.exists(args.registered_image_path):
        raise FileNotFoundError(f"A regisztralt kep nem talalhato: {args.registered_image_path}")

    reg_img = face_recognition.load_image_file(args.registered_image_path)
    live_img = face_recognition.load_image_file(LIVE_IMAGE_PATH)
    
    reg_enc = face_recognition.face_encodings(reg_img)
    live_enc = face_recognition.face_encodings(live_img)

    if not reg_enc:
        print(json.dumps({"status": "error", "message": "Nem talalhato arc a regisztralt kepen"}))
        sys.exit(1)
    if not live_enc:
        print(json.dumps({"status": "error", "message": "Nem talalhato arc az elo kepen"}))
        sys.exit(1)

    result = face_recognition.compare_faces([reg_enc[0]], live_enc[0])[0]
    distance = float(face_recognition.face_distance([reg_enc[0]], live_enc[0])[0])
    is_match = bool(result)

    match_text = "SIKERES ✅" if is_match else "ELUTASÍTVA ❌"
    print(f"\n--- ARCFELISMERÉS EREDMÉNY ---", file=sys.stderr)
    print(f"Státusz:   {match_text}", file=sys.stderr)
    print(f"Távolság:  {distance:.4f}", file=sys.stderr)
    print(f"Küszöb:    0.6000", file=sys.stderr)
    print(f"------------------------------\n", file=sys.stderr)

    print(json.dumps({
        "status": "success",
        "match": is_match,
        "confidence": distance
    }))

except Exception as e:
    print(json.dumps({
        "status":"error",
        "message":str(e)
    }))
    sys.exit(1)

finally:
    if 'picam2' in locals():
        picam2.stop()
    cv2.destroyAllWindows()
    if os.path.exists(LIVE_IMAGE_PATH):
        os.remove(LIVE_IMAGE_PATH)