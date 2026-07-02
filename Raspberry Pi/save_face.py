from picamera2 import Picamera2
from datetime import datetime
import os
import cv2
import time
import json
import sys

SAVE_DIR = "/home/matedavid12345/Desktop/szakdolgozat/photos"
os.makedirs(SAVE_DIR, exist_ok=True)

try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (1500, 1500)})
    picam2.configure(config)
    
    picam2.start()
    time.sleep(2)
    cv2.namedWindow("Arcfelismeres", cv2.WINDOW_NORMAL)
    
    start_time = time.time()
    while time.time() - start_time < 3:
        frame = picam2.capture_array()
        
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        cv2.imshow("Arcfelismeres", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
    path = os.path.join(SAVE_DIR, filename)
    
    picam2.capture_file(path)
    
    print(json.dumps({
        "status": "success",
        "path": path,
        "message": "Kep sikeresen elmentve"
    }))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": str(e),
        "path": None
    }))
    sys.exit(1)

finally:
    picam2.stop()
    cv2.destroyAllWindows()