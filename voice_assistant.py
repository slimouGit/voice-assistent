import pyttsx3
import requests
import speech_recognition

from config import API_KEY, API_URL

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_audio():
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Ich höre zu...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language="de-DE")
            print(f"Du hast gesagt: {text}")
            return text
        except speech_recognition.UnknownValueError:
            print("Entschuldigung, ich habe das nicht verstanden.")
            return None

def get_openai_response(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        print(f"Fehler: {response.status_code}, {response.text}")
        return None

def main():
    while True:
        user_input = get_audio()
        if user_input:
            if user_input.lower() in ["stop", "beenden", "ende"]:
                print("Programm beendet.")
                break

            response = get_openai_response(user_input)
            if response:
                print(f"KI sagt: {response}")
                speak(response)

if __name__ == "__main__":
    main()
