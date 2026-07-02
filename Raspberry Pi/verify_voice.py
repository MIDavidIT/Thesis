import sounddevice as sd
import numpy as np
import librosa
import json
import sys
import os

THRESHOLD = 550
DURATION = 3
SAMPLE_RATE = 44100

def extract_mfcc_live():
    print(f"Felvétel indul ({DURATION} másodperc)... Beszélj most!", file=sys.stderr)
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("Felvétel kész!", file=sys.stderr)
    
    recording_trimmed, _ = librosa.effects.trim(recording.flatten()) # kivágja a csendet
    mfccs = librosa.feature.mfcc(y=recording_trimmed, sr=SAMPLE_RATE, n_mfcc=13) # azért kell a flatten, mert egy 2D-s mátrixot akarok átadni, de azt nem fogja szeretni
    return np.mean(mfccs.T, axis=0)

def verify_voice(model_path):
    if not os.path.exists(model_path):
        print(f"Ez a modell nem található", file=sys.stderr)
        return {"status": "error", "message": "Modell nem talalhato"}
    try:
        user_model = np.load(model_path)
        live_recording_mfcc = extract_mfcc_live()
        distance = np.linalg.norm(user_model - live_recording_mfcc)
        is_match = distance < THRESHOLD
        
        match_text = "SIKERES ✅" if is_match else "ELUTASÍTVA ❌"
        print(f"\n--- HANGANANALÍZIS EREDMÉNY ---", file=sys.stderr)
        print(f"Státusz:   {match_text}", file=sys.stderr)
        print(f"Távolság:  {distance:.4f}", file=sys.stderr)
        print(f"Küszöb:    {THRESHOLD:.4f}", file=sys.stderr)
        print(f"-------------------------------\n", file=sys.stderr)
        
        return {
            "status": "success",
            "match": bool(is_match),
            "distance": float(distance)
        }
    except Exception as e:
        print(f"Hiba történt {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Hianyzo modell eleresi ut"}))
        sys.exit(1)
    
    result = verify_voice(sys.argv[1])
    print(json.dumps(result))