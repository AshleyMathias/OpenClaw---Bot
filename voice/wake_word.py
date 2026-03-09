import numpy as np
import sounddevice as sd
from rapidfuzz import fuzz

from voice.speech_listener import model, has_speech
from voice.config import WAKE_WORD, WAKE_LISTEN_DURATION, SAMPLERATE


def _matches_wake_word(text):
    """Fuzzy-match transcribed text against the wake phrase."""
    text_lower = text.lower().strip()
    if WAKE_WORD in text_lower:
        return True
    score = fuzz.partial_ratio(text_lower, WAKE_WORD)
    if score > 75:
        return True
    return False


def wait_for_wake_word():
    """Block until the wake phrase is detected on the microphone.

    Records short audio clips, checks for speech energy, and only runs
    Whisper transcription when someone is actually speaking.  Returns
    True once the wake word is recognised.
    """
    print("[WakeWord] Listening for wake word... Say 'Hey OpenClaw'")
    while True:
        try:
            audio = sd.rec(
                int(WAKE_LISTEN_DURATION * SAMPLERATE),
                samplerate=SAMPLERATE,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            energy = float(np.sqrt(np.mean(audio ** 2)))

            if not has_speech(audio):
                continue

            print(f"[WakeWord] Speech detected (energy={energy:.4f}), transcribing...")
            audio_flat = audio.flatten()
            result = model.transcribe(audio_flat, fp16=False)
            transcript = result["text"].strip()
            print(f"[WakeWord] Heard: \"{transcript}\"")

            if transcript and _matches_wake_word(transcript):
                return True

        except sd.PortAudioError as e:
            print(f"[WakeWord] Microphone error: {e}")
            sd.sleep(1000)
        except Exception as e:
            print(f"[WakeWord] Error: {e}")
            sd.sleep(1000)
