import pyttsx3
import requests
import speech_recognition

from config import API_KEY, API_URL

"""The voice_assistant_v1.py script is a simple voice assistant application that uses speech recognition and text-to-speech capabilities to interact with the user. It captures audio input, processes it using the OpenAI API, and responds with synthesized speech.
Features:
Speech Recognition: Captures audio input from the microphone and converts it to text using Google Speech Recognition.
Text-to-Speech: Converts text responses from the OpenAI API to speech and plays it back to the user.
OpenAI Integration: Sends user input to the OpenAI API and retrieves a response for a casual conversation."""

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech and play it."""
    engine.say(text)
    engine.runAndWait()

def get_audio():
    """Capture audio from the microphone and recognize it using Google Speech Recognition."""
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Recording... Speak now!")
        try:
            # Listen for audio input
            audio = recognizer.listen(source)
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio, language="en-EN")
            print(f"You said: {text}")
            return text
        except speech_recognition.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None

def get_openai_response(prompt):
    """Send a prompt to the OpenAI API and return the response."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a friendly assistant who engages in casual conversation."},
            {"role": "user", "content": prompt}
        ],
    }
    # Send a POST request to the OpenAI API
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def main():
    """Main function to run the voice assistant."""
    while True:
        # Get audio input from the user
        user_input = get_audio()
        if user_input:
            # Check for termination commands
            if user_input.lower() in ["stop", "beenden", "ende"]:
                print("Program terminated.")
                break

            # Get response from OpenAI API
            response = get_openai_response(user_input)
            if response:
                print(f"AI says: {response}")
                # Convert the response text to speech
                speak(response)

if __name__ == "__main__":
    main()