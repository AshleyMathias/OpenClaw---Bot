import pyttsx3
from voice.config import VOICE_NAME, VOICE_RATE, VOICE_VOLUME


class Speaker:
    def __init__(self):
        self._test_audio()

    def _test_audio(self):
        """Startup test — you should hear 'OpenClaw ready' when this runs."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", VOICE_RATE)
            engine.setProperty("volume", VOICE_VOLUME)
            voices = engine.getProperty("voices")
            for v in voices:
                if VOICE_NAME.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    print(f"[Speaker] Using voice: {v.name}")
                    break
            engine.say("OpenClaw ready")
            engine.runAndWait()
            engine.stop()
            print("[Speaker] Audio test complete — did you hear 'OpenClaw ready'?")
        except Exception as e:
            print(f"[Speaker] Audio test FAILED: {e}")

    def speak(self, text):
        """Create a fresh engine each call to avoid pyttsx3 state issues."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", VOICE_RATE)
            engine.setProperty("volume", VOICE_VOLUME)
            for v in engine.getProperty("voices"):
                if VOICE_NAME.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[Speaker] Error during speech: {e}")


_default_speaker = None


def speak(text):
    """Module-level convenience function (backward compatible)."""
    global _default_speaker
    if _default_speaker is None:
        _default_speaker = Speaker()
    _default_speaker.speak(text)
