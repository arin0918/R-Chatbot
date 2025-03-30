import requests
import pyaudio
import numpy as np
import wave
from vosk import Model, KaldiRecognizer
from gtts import gTTS
import json
import os

# Paths to Vosk models
vosk_models = {
    "hi": Model("D:/vosk-models/vosk-model-hi-0.22-small/vosk-model-small-hi-0.22"),
    "en": Model("D:/vosk-models/vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15")
}

# Rasa API Endpoint
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

# PyAudio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 4000  # Buffer size

# Function to record audio using PyAudio
def record_audio(duration=5, lang="hi"):
    print(f"🎤 Recording ({lang.upper()} Mode)... Speak now!")
    
    wav_file = "temp.wav"
    audio = pyaudio.PyAudio()
    
    # Open stream for recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the recorded audio
    with wave.open(wav_file, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return wav_file

# Function to recognize speech using Vosk
def recognize_speech(lang="hi"):
    wav_file = record_audio(lang=lang)

    # Load the correct Vosk model
    model = vosk_models.get(lang, vosk_models["en"])  # Default to English
    rec = KaldiRecognizer(model, RATE)

    with wave.open(wav_file, "rb") as wf:
        while True:
            data = wf.readframes(CHUNK)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "")

    return ""

# Function to send message to Rasa chatbot
def send_to_rasa(user_message, lang="hi"):
    if not user_message.strip():
        print("⚠ No speech detected. Please try again!")
        return

    payload = {"sender": "user", "message": user_message}
    try:
        response = requests.post(RASA_SERVER_URL, json=payload, timeout=5)
        if response.status_code == 200:
            messages = response.json()
            for msg in messages:
                bot_reply = msg.get("text", "")
                print(f"🤖 Bot ({lang.upper()}):", bot_reply)

                # Convert text to speech
                tts = gTTS(bot_reply, lang=lang)
                tts.save("response.mp3")
                
                # Play response using PyAudio
                play_audio("response.mp3")
                os.remove("response.mp3")  # Clean up
        else:
            print("❌ Error: Unable to reach Rasa chatbot.")
    except requests.exceptions.RequestException as e:
        print(f"⚠ Network Error: {e}")

# Function to play audio using PyAudio
def play_audio(file_path):
    audio = pyaudio.PyAudio()

    with wave.open(file_path, "rb") as wf:
        stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()), 
                            channels=wf.getnchannels(), 
                            rate=wf.getframerate(), 
                            output=True)
        
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        audio.terminate()

# Main loop
if __name__ == "__main__":
    while True:
        user_lang = input("🌍 Select language (hi/en): ").strip().lower()
        if user_lang not in vosk_models:
            print("⚠ Language not supported! Defaulting to English.")
            user_lang = "en"

        user_message = recognize_speech(user_lang)
        if user_message.lower() == "exit":
            print("👋 Exiting... Goodbye!")
            break

        send_to_rasa(user_message, user_lang)
