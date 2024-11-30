import websocket

try:
    ws = websocket.create_connection("wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01")
    print("Connection succeeded!")
    ws.close()
except Exception as e:
    print(f"Connection failed: {e}")
