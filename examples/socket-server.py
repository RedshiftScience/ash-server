import socketio
import io
import soundfile
import base64
from flask import Flask, render_template, request, send_file
import os


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
import numpy as np
import sys
from tempfile import NamedTemporaryFile
import edge_tts
import asyncio
import soundfile
import resampy
# import pyaudio
def piper(text,timings=False):
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
        start = time.perf_counter()
        piper_request = ASH_grpc_pb2.ServerPIPERRequest(**piper_data)
        piper_response = piper_stub.SynthesizePiper(piper_request)
        end = time.perf_counter()
        if timings:
            # in ms
            print(f"piper: {(end-start)*1000:.2f} ms")
        piper_audio_bytes = piper_response.audio_bytes
        # save the audio to a wav file
        piper_np = np.frombuffer(piper_audio_bytes, dtype=np.float32) # remember to convert from float16 if using half
        # convert to float32
        # piper_np = piper_np.astype(np.float32)
        # write
        sf.write("piper.wav", piper_np, 22050)
        return piper_np.tobytes()



def rvc(bytes,timings=False):
    grpc_opt_cfg = [
        ('grpc.max_send_message_length', ash_cfgs.grpc_opt_max_send_message_length_cfg),
        ('grpc.max_receive_message_length', ash_cfgs.grpc_opt_max_receive_message_length_cfg)
    ]

    channel = grpc.insecure_channel(f"{ash_cfgs.rvc_ip_cfg}:{ash_cfgs.rvc_port_cfg}", grpc_opt_cfg)
    rvc_stub = ASH_grpc_pb2_grpc.ServerRVCServiceStub(channel)
    rvc_data = {
        "audio_bytes": bytes,
        "f0_up_key": ash_cfgs.rvc_f0_up_key_cfg,
        "f0_file": ash_cfgs.rvc_f0_file_cfg,
        "f0_method": ash_cfgs.rvc_f0_method_cfg,
        "file_index": ash_cfgs.rvc_file_index_cfg,
        "file_index2": ash_cfgs.rvc_file_index2_cfg,
        "filter_radius": ash_cfgs.rvc_filter_radius_cfg,
        "index_rate": ash_cfgs.rvc_index_rate_cfg,
        "protect": ash_cfgs.rvc_protect_cfg, 
        "resample_sr": ash_cfgs.rvc_resample_sr_cfg,
        "rms_mix_rate": ash_cfgs.rvc_rms_mix_rate_cfg,
        "version": ash_cfgs.rvc_version_cfg,
        "tgt_sr": ash_cfgs.rvc_tgt_sr_cfg
    }

    start = time.perf_counter()
    rvc_request = ASH_grpc_pb2.ServerRVCRequest(**rvc_data)
    rvc_response = rvc_stub.ProcessAudio(rvc_request)
    end = time.perf_counter()
    if timings:
        # in ms
        print(f"rvc: {(end-start)*1000:.2f} ms")
  
    rvc_audio_bytes = rvc_response.audio_bytes

    return rvc_audio_bytes



async def edge(text,timings=False):
    VOICE = "en-US-AriaNeural"
    start = time.perf_counter()
    communicate = edge_tts.Communicate(text, VOICE)
    stream = communicate.stream()

    bytes_arr = b''
    async for chunk in stream:
        if chunk["type"] == "audio":
       
            bytes_arr += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            pass
    if timings:
        end = time.perf_counter()
        print(f"edge: {(end-start)*1000:.2f} ms")

    # convert from wav bytes to int16 and resample to 40000 hz
    
    f_name = "temp.wav"
    with open(f_name, "wb") as f:
        f.write(bytes_arr)


    
    sound = soundfile.read(f_name, dtype='float32')[0]
    # convert to int16
    # audio_np = np.frombuffer(sound, dtype=np.int16)

    # resample to 40000 hz
    audio_np = resampy.resample(sound, 24000, 22050)
    # convert to int16
    # audio_np = (audio_np * 32767).astype(np.int16)
    return audio_np.tobytes()


# lock = threading.Lock()

def tts(text,stack, timings=False, subtitle_window=None):
    # with lock:
    # split into sentences using . ? , and !
    sentences = []
    current_sentence = ""
    for char in text:
        current_sentence += char
        if char in [".", "?", "!"]:
            sentences.append(current_sentence)
            current_sentence = ""

    # check if there are no punctuation in the input text
    if len(sentences) == 0:
        sentences.append(text)

    if stack not in ["piper","edge-tts"]:
        raise ValueError(f"Invalid tts backend: {stack}")
        
    # remove any single characters
    sentences = [sentence for sentence in sentences if len(sentence) > 1]

    # if the original text didnt have ant punctuation, just tts the whole thing
    if len(sentences) == 0:
        sentences = [text]

    # raise an error if the text is too long
    for sentence in sentences:
        assert len(sentence) < ash_cfgs.max_tts_char_cfg, f"Text is too long. Max characters is {ash_cfgs.max_tts_char_cfg}. This is to prevent the tts from using too much video memory."


    audio_bytes_sum = b""
    # tts each sentence
    start_tts = time.perf_counter()
    first = True
    for sentence in sentences:
        audio_bytes = b""
        if stack == "piper":
            audio_bytes = piper(sentence,timings=timings)
        elif stack == "edge-tts":
            audio_bytes = asyncio.run(edge(sentence,timings=timings))
        else:
            raise ValueError(f"Invalid tts backend: {stack}")
        audio_bytes = rvc(audio_bytes,timings=timings)

        first_tts_time = time.perf_counter()
        if first:
            print(f"first tts chunk: {(first_tts_time-start_tts)*1000:.2f} ms")
            first = False
        audio_bytes_sum += audio_bytes
    if timings:
        print(f"tts: {(time.perf_counter()-start_tts)*1000:.2f} ms")


    # write to a output wav
    audio_np = np.frombuffer(audio_bytes_sum, dtype=np.int16)


    return audio_np

import eventlet
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

sio = socketio.Server(cors_allowed_origins='*')  # Set the CORS allowed origins here
app = socketio.WSGIApp(sio, app)


@sio.event
def connect(sid, environ):
    print(f"Connected: {sid}")

@sio.event
def synthesize_audio(sid, text):
    # Call your TTS function with the provided text here (replace this with your code)
    # Sanitize text, limit to alphanumeric and punctuation
    text = ''.join([c for c in text if c.isalnum() or c in [' ', '.', '?', '!']])

    # For example:
    print(f"tts: {text}")
    tts_output = tts(text, "piper")

    # Create an in-memory file for the WAV data
    memory_file = io.BytesIO()
    soundfile.write(memory_file, tts_output, 40000, format="WAV")
    memory_file.seek(0)

    # Convert the WAV data to a base64-encoded string
    wav_data_base64 = base64.b64encode(memory_file.read()).decode('utf-8')

    # Emit the synthesized audio data via WebSocket
    sio.emit('audio_data', wav_data_base64, room=sid)

@sio.event
def disconnect(sid):
    print(f"Disconnected: {sid}")

if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5327)), app)

