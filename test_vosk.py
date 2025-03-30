from vosk import Model, KaldiRecognizer
import sys
import wave

# Correct model path
model_path = r"D:\vosk-models\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"

# Load Vosk model
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Open the recorded WAV file
wav_file = "test.wav"  # Make sure this file exists in the working directory
wf = wave.open(wav_file, "rb")

# Check audio format
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
    print("Audio format not supported. Use 16kHz mono WAV.")
    sys.exit(1)

# Process audio
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if recognizer.AcceptWaveform(data):
        print(recognizer.Result())

# Print final result
print(recognizer.FinalResult())
