import socketio
import base64
import soundfile
import io

# Initialize the Socket.IO client
sio = socketio.Client()

# Define the text prompt you want to synthesize
text_prompt = "Hello, this is a test. Https."

@sio.event
def connect():
    print("Connected to the Socket.IO server")

@sio.event
def disconnect():
    print("Disconnected from the Socket.IO server")

# Define an event handler to receive the synthesized audio data
@sio.on('audio_data')
def receive_audio_data(data):
    # Convert the base64-encoded data back to binary
    audio_binary = base64.b64decode(data)

    # Save the audio data to a WAV file
    with open("synthesized_audio.wav", "wb") as f:
        f.write(audio_binary)

# Connect to the Socket.IO server
sio.connect('https://melba-tts.zuzu.red')

# Send the text prompt for audio synthesis
sio.emit('synthesize_audio', text_prompt)

# Wait for the audio data to be received
sio.wait()

# Disconnect from the Socket.IO server
sio.disconnect()
