import librosa
import numpy as np
import sounddevice as sd
import os
from scipy.io.wavfile import write
import sys
import json

DURATION = 3
SAMPLE_RATE = 44100
SAVE_DIR = "/home/matedavid12345/Desktop/szakdolgozat/voice_models"
os.makedirs(SAVE_DIR, exist_ok=True)

def extract_mfcc(file_path):
    y, sr = librosa.load(file_path)
    y, _ = librosa.effects.trim(y)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfccs.T, axis=0)

def register_voice(username):
    filename = f"{username}_voice.wav"
    path = os.path.join(SAVE_DIR, filename)
    model_path = os.path.join(SAVE_DIR, f"{username}_model.npy")

    try:
        print(f"Felvétel indul ({DURATION} másodperc)... Beszélj most!", file=sys.stderr)
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        print("Felvétel kész, mentés...", file=sys.stderr)
        
        write(path, SAMPLE_RATE, recording)
        
        recording_mfcc = extract_mfcc(path)
        np.save(model_path, recording_mfcc)
        
        print(f"Modell elmentve: {model_path}", file=sys.stderr)
        return {
            "status": "success",
            "path": model_path, 
            "message": "Hangminta rogzitve"
        }

    except Exception as e:
        print(f"Hiba történt {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Hianyzo felhasznalonev"}))
        sys.exit(1)
        
    result = register_voice(sys.argv[1])
    print(json.dumps(result))