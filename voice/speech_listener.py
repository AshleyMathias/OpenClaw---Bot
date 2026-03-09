import numpy as np
import sounddevice as sd
import whisper

from voice.config import LISTEN_DURATION, SAMPLERATE

model = whisper.load_model("base")


def listen(duration=LISTEN_DURATION, samplerate=SAMPLERATE):
    """Record from microphone and transcribe with Whisper.

    Returns the transcribed text, or an empty string on failure.
    """
    try:
        print("[Listener] Listening...")
        recording = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        audio = recording.flatten()
        result = model.transcribe(audio, fp16=False)
        return result["text"].strip()

    except sd.PortAudioError as e:
        print(f"[Listener] Microphone error: {e}")
        return ""
    except Exception as e:
        print(f"[Listener] Error: {e}")
        return ""


def has_speech(audio, threshold=0.01):
    """Check whether an audio array contains speech-level energy."""
    return float(np.sqrt(np.mean(audio ** 2))) > threshold
