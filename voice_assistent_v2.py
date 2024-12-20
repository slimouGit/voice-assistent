import requests
import sounddevice as sd
import numpy as np
import wave
import pyttsx3

from config import API_KEY, REALTIME_API_URL

"""The voice_assistent_v2.py script is a voice assistant application that records audio input, transcribes it using the OpenAI API, and responds with synthesized speech. It uses the sounddevice library for audio recording and playback, and pyttsx3 for text-to-speech conversion.
Features:
Audio Recording: Captures audio input from the microphone.
Audio Transcription: Sends recorded audio to the OpenAI API for transcription.
Text-to-Speech: Converts text responses from the OpenAI API to speech and plays it back to the user.
OpenAI Integration: Uses the OpenAI API for both transcription and generating responses."""

SAMPLERATE = 16000  # Required for the Realtime API
DURATION = 5        # Recording time in seconds

# Initialize conversation history
conversation_history = []

def record_audio():
    """Records audio via the microphone."""
    print("Recording... Speak now!")
    audio_data = sd.rec(int(SAMPLERATE * DURATION), samplerate=SAMPLERATE, channels=1, dtype="int16")
    sd.wait()  # Wait until the recording is finished
    print("Recording finished.")
    return np.array(audio_data, dtype=np.int16)

def save_audio_to_wav(audio_data, filename="input.wav"):
    """Saves audio data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLERATE)
        wf.writeframes(audio_data.tobytes())

def transcribe_audio(audio_file_path):
    """Sends a WAV file for transcription to the OpenAI API."""
    with open(audio_file_path, "rb") as audio_file:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
        }
        files = {
            "file": audio_file,
            "model": (None, "whisper-1")  # The model for speech recognition
        }
        print("Sending audio to OpenAI API...")
        response = requests.post(f"{REALTIME_API_URL}", headers=headers, files=files)
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

def synthesize_speech(prompt):
    """Generates a spoken response from the OpenAI API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Add the new user prompt to the conversation history
    conversation_history.append({"role": "user", "content": prompt})

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a friendly assistant who engages in casual conversation."}
        ] + conversation_history  # Include the conversation history
    }
    print("Generating response...")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        text_response = response_data["choices"][0]["message"]["content"]
        # Add the model's response to the conversation history
        conversation_history.append({"role": "assistant", "content": text_response})
        return text_response
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def save_text_to_speech(text, filename="response.wav"):
    """Saves the text as a spoken response in a WAV file."""
    engine = pyttsx3.init()
    """initializes available voices"""
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

def play_audio(file_path):
    """Plays a WAV file."""
    with wave.open(file_path, "rb") as wf:
        data = wf.readframes(wf.getnframes())
        sd.play(np.frombuffer(data, dtype=np.int16), samplerate=wf.getframerate())
        sd.wait()

def main():
    while True:
        audio_data = record_audio()
        save_audio_to_wav(audio_data, "input.wav")
        user_text = transcribe_audio("input.wav")

        if user_text:
            print(f"You said: {user_text}")
            if user_text.lower() in ["stop", "beenden", "ende"]:
                print("Program terminated.")
                break

            text_response = synthesize_speech(user_text)
            if text_response:
                response_audio_file = save_text_to_speech(text_response)
                print("Playing response...")
                play_audio(response_audio_file)
        else:
            print("No valid input recognized. Please try again.")

if __name__ == "__main__":
    main()