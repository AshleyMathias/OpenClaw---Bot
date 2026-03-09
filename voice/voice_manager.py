import requests

from voice.config import API_URL, SESSION_ID
from voice.speaker import Speaker
from voice.speech_listener import listen


class VoiceManager:
    def __init__(self):
        self._speaker = Speaker()

    def run(self):
        """Continuous loop: listen -> chat -> speak full answer -> repeat."""
        print("[VoiceManager] Voice assistant running. Just speak!")
        while True:
            try:
                user_text = listen()
                if not user_text:
                    continue

                print(f"[VoiceManager] You: {user_text}")
                print("[VoiceManager] Processing request...")

                response = self._send_message(user_text)
                if response:
                    print(f"[VoiceManager] OpenClaw: {response}")
                    print("[VoiceManager] Speaking response...")
                    self._speaker.speak(response)
                    print("[VoiceManager] Done speaking.")

            except KeyboardInterrupt:
                print("\n[VoiceManager] Shutting down.")
                break
            except Exception as e:
                print(f"[VoiceManager] Unexpected error: {e}")

    def _send_message(self, text):
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                params={"message": text, "session_id": SESSION_ID},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.RequestException as e:
            print(f"[VoiceManager] API error: {e}")
            return ""


def run_voice_assistant():
    """Public entry point — creates a VoiceManager and starts the loop."""
    manager = VoiceManager()
    manager.run()
