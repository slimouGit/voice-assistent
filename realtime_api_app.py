import time
import sounddevice as sd
import numpy as np
import json
from websocket import create_connection

from config import API_KEY

SAMPLERATE = 16000  # Erforderlich für Realtime API
CHUNK_SIZE = 1024  # Größe der Audio-Chunks
REALTIME_API_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01";



def record_and_send_audio(ws):
    """Nimmt Audio auf und sendet es in Echtzeit an die Realtime API."""
    print("Starte Aufnahme... Sprich jetzt!")
    time.sleep(2)  # Füge eine Verzögerung ein, damit das Mikrofon initialisiert wird

    try:
        # Starte die Aufnahme
        with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="int16") as stream:
            while ws.connected:
                chunk, _ = stream.read(CHUNK_SIZE)
                if not np.any(chunk):
                    print("Überspringe leeres Audio-Chunks.")  # Überspringe leere Daten
                    continue

                # Sende nur, wenn gültige Daten vorhanden sind
                ws.send(chunk.tobytes(), opcode=0x2)
                print("Audio-Chunk gesendet.")  # Debugging
    except Exception as e:
        print(f"Fehler während der Aufnahme: {e}")


def receive_responses(ws):
    """Empfängt Antworten von der Realtime API."""
    print("Warten auf KI-Antwort...")
    try:
        while ws.connected:
            message = ws.recv()  # Warte auf eine Nachricht
            if not message:
                print("Leere Nachricht erhalten.")
                continue

            print(f"Antwort von der API: {message}")  # Debugging
            response = json.loads(message)

            if "audio" in response:
                play_audio(response["audio"])
            elif "text" in response:
                print(f"KI-Antwort: {response['text']}")
    except Exception as e:
        print(f"Fehler beim Empfang der Antwort: {e}")


def play_audio(audio_data):
    """Spielt Audio-Daten ab."""
    print("Spiele KI-Antwort ab...")
    sd.play(np.frombuffer(audio_data, dtype=np.int16), samplerate=SAMPLERATE)
    sd.wait()


def realtime_conversation():
    """Stellt eine WebSocket-Verbindung zur Realtime API her."""
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "OpenAI-Beta": "realtime=v1"
    }
    while True:
        try:
            print("Verbinde mit der Realtime API...")
            ws = create_connection(REALTIME_API_URL, header=headers, timeout=300)

            # Starte parallele Threads für Aufnahme und Antworten
            from threading import Thread

            record_thread = Thread(target=record_and_send_audio, args=(ws,))
            receive_thread = Thread(target=receive_responses, args=(ws,))

            record_thread.start()
            receive_thread.start()

            record_thread.join()
            receive_thread.join()
        except KeyboardInterrupt:
            print("Programm beendet.")
            break
        except Exception as e:
            print(f"Verbindungsfehler: {e}. Erneut versuchen...")
            time.sleep(5)
        finally:
            try:
                ws.close()
            except Exception:
                pass


if __name__ == "__main__":
    print("Starte Realtime-Konversation...")
    try:
        realtime_conversation()
    except Exception as e:
        print(f"Fehler: {e}")
