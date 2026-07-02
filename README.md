# PiLock - Multimodal Biometric Smart Lock 🔒

[![Platform: Raspberry Pi 5](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-C51A4A?logo=raspberry-pi)](#)
[![Language: Python](https://img.shields.io/badge/Server-Python_3.11-3776AB?logo=python)](#)
[![Language: Kotlin](https://img.shields.io/badge/Client-Android_(Kotlin)-073042?logo=kotlin)](#)
[![Framework: Flask](https://img.shields.io/badge/Framework-Flask-000000?logo=flask)](#)

🌍 **[Read in English](#-english-version)** | 🇭🇺 **[Ugrás a Magyar Verzióra](#-magyar-verzió)**

---

## 🇬🇧 English Version

### 📖 Project Overview
This repository contains the source code for my BSc Thesis in Computer Science Engineering: **"Multimodal Smart Lock Control: Android-based system on Raspberry Pi platform"**. 

The PiLock system is an IoT-based smart lock that replaces traditional single-factor authentication with a robust, multi-layered biometric chain. The system is controlled via a native Android application and uses a Raspberry Pi 5 as the central server. The lock will only open if **all three** biometric factors (Fingerprint, Face, and Voice) are successfully verified.

### ✨ Features
* **Software Interlocking:** The 12V solenoid lock only opens after a 100% successful multi-factor authentication process.
* **Multimodal Biometrics:**
  * 👆 **Fingerprint:** Optical CMOS sensor (SEN0188) with local DSP template matching.
  * 👤 **Face Recognition:** 128-dimensional facial feature vector extraction and Euclidean distance measurement using OpenCV and `dlib` (`face_recognition`).
  * 🗣️ **Voice Analysis:** Mel-frequency cepstral coefficients (MFCC) extraction via the `librosa` library.
* **Android Client:** Native Kotlin app with OkHttp for asynchronous, encrypted HTTPS communication.
* **Fail-Secure Architecture:** The relay and 12V solenoid lock are wired in a "Normally Open" (NO) configuration, ensuring the door remains securely locked during a power outage.
* **Local Database:** Secure SQLite database with PBKDF2 password hashing.

### 🛠️ Hardware Requirements
* **Server:** Raspberry Pi 5 (8GB) with Active Cooler (SC1148)
* **Fingerprint Sensor:** DFRobot SEN0188 (UART interface)
* **Camera:** Raspberry Pi Camera Module v2 (mini-CSI interface)
* **Microphone:** USB Condenser Microphone
* **Lock Mechanism:** 12V Electromagnetic Solenoid Lock
* **Relay:** 5V One-Channel Relay Module (Galvanic isolation)
* **Client:** Android Smartphone (Huawei P20 Lite or newer)

### 💻 Code Structure
* `server.py`: The main Flask API gateway handling HTTP requests, SQLite database operations, and GPIO relay control.
* `save_*.py`: Scripts handling the registration phase (capturing and saving biometric templates).
* `verify_*.py`: Scripts handling the verification phase (matching live inputs against stored models).
* `lock_test.py`: A simple hardware test script to check relay and solenoid functionality.
* `delete_all_fingerprint.py`: Utility script to clear the SEN0188 sensor's internal memory.

### 🚀 How to Run (Server-side)
1. Install dependencies:
   ```bash
   pip install flask picamera2 face_recognition opencv-python librosa sounddevice adafruit-circuitpython-fingerprint RPi.GPIO

2. Generate SSL certificates for HTTPS (required for secure OkHttp communication):
   ```bash
   openssl req -x509 -newkey rsa:4096 -nodes -out certfile.crt -keyout keyfile.key -days 365

3. Start the Flask server:
   ```bash
   python3 server.py
