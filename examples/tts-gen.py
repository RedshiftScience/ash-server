
import ash_cfgs
import grpc
import ASH_grpc_pb2
import ASH_grpc_pb2_grpc
# Create a queue to hold incoming requests
import threading
lock = threading.Lock()
import time
import soundfile as sf
import os
import pyaudio
def piper(text):


    # remove "*" from text
    text = text.replace("*", "")
    with lock:
        grpc_opt_cfg = [
            ('grpc.max_send_message_length', ash_cfgs.grpc_opt_max_send_message_length_cfg),
            ('grpc.max_receive_message_length', ash_cfgs.grpc_opt_max_receive_message_length_cfg)
        ]
        channel = grpc.insecure_channel(f"{ash_cfgs.piper_ip_cfg}:{ash_cfgs.piper_port_cfg}",grpc_opt_cfg)
        piper_stub = ASH_grpc_pb2_grpc.ServerPIPERServiceStub(channel)

        piper_data ={
            "text": text,
            "model": ash_cfgs.piper_model_cfg,
            "noise_scale": ash_cfgs.piper_noise_scale_cfg,
            "length_scale": ash_cfgs.piper_length_scale_cfg,
            "noise_scale_w": ash_cfgs.piper_noise_scale_w_cfg,
            "speaker_id": ash_cfgs.piper_speaker_id_cfg,
            "auto_rvc": False
        }    
    
        piper_request = ASH_grpc_pb2.ServerPIPERRequest(**piper_data)
        piper_response = piper_stub.SynthesizePiper(piper_request)
        piper_audio_bytes = piper_response.audio_bytes
        return piper_audio_bytes


def tts_loop():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=22050,
                    output=True)
    while True:
        input_text = input("tts: ")
        if input_text == "exit":
            break

        audio_bytes = piper(input_text)
        # play audio
        stream.write(audio_bytes)

    stream.stop_stream()
    stream.close()
    p.terminate()

def tts_wav(text, path):
    audio_bytes = piper(text)
    with sf.SoundFile(path, 'w', samplerate=22050, channels=1, format='wav') as f:
        f.write(audio_bytes)

def main():
    while True:
        command = input("tts or wav: ")
        if command == "tts":
            tts_loop()
        elif command == "wav":
            text = input("text: ")
            path = input("output path: ")
            tts_wav(text, path)
        elif command == "exit":
            break
        else:
            print("invalid command")
        
if __name__ == "__main__":
    main()

