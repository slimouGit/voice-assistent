import json
from websocket import create_connection
from config import API_KEY

REALTIME_API_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

def test_server_communication():
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "OpenAI-Beta": "realtime=v1",
        "Content-Type": "application/json"
    }
    try:
        print("Connecting to the Realtime API...")
        ws = create_connection(REALTIME_API_URL, header=headers, timeout=300)
        print("Connection established.")

        # Send a test message
        test_message = json.dumps({"type": "test", "message": "Hello, server!"})
        ws.send(test_message)
        print("Test message sent.")

        # Receive a response
        response = ws.recv()
        print(f"Response from the server: {response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            ws.close()
        except Exception:
            pass

if __name__ == "__main__":
    test_server_communication()