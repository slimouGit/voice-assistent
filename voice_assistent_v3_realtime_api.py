import time
import sounddevice as sd
import numpy as np
import json
from websocket import create_connection

from config import API_KEY

"""The voice_assistent_v3_realtime_api.py script is a voice assistant application that records audio input, sends it to the OpenAI Realtime API for processing, and plays back the AI-generated responses. It uses the sounddevice library for audio recording and playback, and WebSockets for real-time communication with the API.
Features:
Real-time Audio Recording: Captures audio input from the microphone in real-time.
WebSocket Communication: Sends recorded audio chunks to the OpenAI Realtime API and receives responses.
Audio Playback: Plays back the AI-generated audio responses.
Error Handling: Implements reconnection logic in case of connection errors."""

SAMPLERATE = 16000  # Required for Realtime API
CHUNK_SIZE = 1024  # Size of audio chunks
REALTIME_API_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"


def record_and_send_audio(ws):
    """Records audio and sends it in real-time to the Realtime API."""
    print("Starting recording... Speak now!")
    time.sleep(2)  # Add a delay to allow the microphone to initialize

    try:
        # Start the recording
        with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="int16") as stream:
            while ws.connected:
                chunk, _ = stream.read(CHUNK_SIZE)
                if not np.any(chunk):
                    print("Skipping empty audio chunk.")  # Skip empty data
                    continue

                try:
                    ws.send(chunk.tobytes(), opcode=0x2)
                    print("Audio chunk sent.")  # Debugging
                except Exception as e:
                    print(f"Error sending audio chunk: {e}")
                time.sleep(0.1)
    except Exception as e:
        print(f"Error during recording: {e}")


def receive_responses(ws):
    """Receives responses from the Realtime API."""
    print("Waiting for AI response...")
    try:
        while ws.connected:
            message = ws.recv()  # Wait for a message
            if not message:
                print("Received empty message.")
                continue

            print(f"Response from the API: {message}")  # Debugging
            response = json.loads(message)

            if "audio" in response:
                play_audio(response["audio"])
            elif "text" in response:
                print(f"AI response: {response['text']}")
    except Exception as e:
        print(f"Error receiving response: {e}")


def play_audio(audio_data):
    """Plays audio data."""
    print("Playing AI response...")
    sd.play(np.frombuffer(audio_data, dtype=np.int16), samplerate=SAMPLERATE)
    sd.wait()


def realtime_conversation():
    """Establishes a WebSocket connection to the Realtime API."""
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "OpenAI-Beta": "realtime=v1",
        "Content-Type": "application/json"
    }
    while True:
        try:
            print("Connecting to the Realtime API...")
            ws = create_connection(REALTIME_API_URL, header=headers, timeout=300)

            # Start parallel threads for recording and receiving responses
            from threading import Thread

            record_thread = Thread(target=record_and_send_audio, args=(ws,))
            receive_thread = Thread(target=receive_responses, args=(ws,))

            record_thread.start()
            receive_thread.start()

            record_thread.join()
            receive_thread.join()
        except KeyboardInterrupt:
            print("Program terminated.")
            break
        except Exception as e:
            print(f"Connection error: {e}. Retrying...")
            time.sleep(5)
        finally:
            try:
                ws.close()
            except Exception:
                pass


if __name__ == "__main__":
    print("Starting realtime conversation...")
    try:
        realtime_conversation()
    except Exception as e:
        print(f"Error: {e}")
