WAKE_WORD = "hi"

VOICE_RATE = 150
VOICE_VOLUME = 1.0
VOICE_NAME = "David"

LISTEN_DURATION = 5
WAKE_LISTEN_DURATION = 3
SAMPLERATE = 16000

API_URL = "http://127.0.0.1:8000"
SESSION_ID = "voice_user"

# RMS amplitude threshold for detecting user speech during TTS playback.
# Raise this if TTS echo triggers false interrupts; lower if hard to interrupt.
INTERRUPT_THRESHOLD = 0.05
INTERRUPT_CONSECUTIVE_FRAMES = 3
