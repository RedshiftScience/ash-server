
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
import playsound
from tempfile import NamedTemporaryFile
import edge_tts
from subtitles import SubtitleWindow
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

    # save the audio to a wav file
    rvc_np = np.frombuffer(rvc_audio_bytes, dtype=np.float32)
    # write
    sf.write("rvc.wav", rvc_np, 40000)
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


def tts(text,stack, timings=False, subtitle_window=None):
    # split into sentences using . ? , and !
    sentences = []
    current_sentence = ""
    for char in text:
        current_sentence += char
        if char in [".", "?", "!"]:
            sentences.append(current_sentence)
            current_sentence = ""

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
    if subtitle_window:
        subtitle_thread = threading.Thread(target=write_subtitle, args=(subtitle_window,sentences))
        subtitle_thread.start()

    # write to a output wav
    audio_np = np.frombuffer(audio_bytes_sum, dtype=np.int16)
    # save
    type_b = 1 if stack == "piper" else 2
    sf.write(f"output-{type_b}.wav", audio_np, 40000)

    return audio_bytes_sum

def play_audio(audio_bytes):
    print("playing audio")
    # play audio in thread
    with NamedTemporaryFile(suffix=".wav", delete=False) as f:
        # opena soundfile
        sf.write(f.name, audio_bytes, 40000)
        # play audio
        playsound.playsound(f.name, True)
        os.unlink(f.name)

def write_subtitle(subtitle_window, texts):
    time.sleep(0.3)
    for sentence in texts:
        subtitle_window.display_progressive_words(sentence, 0.3)
    time.sleep(0.5)
    # clear the subtitle window
    subtitle_window.text_label.config(text="")

def tts_loop(subtitleWindow, backend,timings=False):
    
  
    while True:
       
        input_text = input("tts: ")
        if input_text == "exit":
            break

        audio_bytes = tts(input_text,stack=backend,timings=timings, subtitle_window=subtitleWindow)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        # write to a wav
        # play audio in a thread
        audio_thread = threading.Thread(target=play_audio, args=(audio_np,))
        audio_thread.start()
          



def tts_wav(text, path, backend ,timings=False):
    print("timings:")
    start = time.perf_counter()
    audio_bytes = tts(text,stack=backend,timings=timings)
    with sf.SoundFile(path, 'w', samplerate=40000, channels=1, format='wav') as f:
        # convert to int16
        audio_bytes = np.frombuffer(audio_bytes, dtype=np.int16)
        f.write(audio_bytes)
    end = time.perf_counter()
    if timings:
        # in ms
        print(f"tts to wav: {(end-start)*1000:.2f} ms")        

def main(subtitleWindow,timings=False,):
    while True:
        backend = input("backend (piper or edge-tts): ")
        if backend != "piper" and backend != "edge-tts":
            print("invalid backend")
            continue
        command = input("play (tts) or save as (wav): ")

        if command == "tts":

            tts_loop(subtitleWindow,backend,timings=timings)
        elif command == "wav":
            text = input("text: ")
            path = input("output path: ")
            tts_wav(text, path, backend,timings=timings)
        elif command == "exit":
            break
        else:
            print("invalid command")
    sys.exit(0)

import  argparse    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', action='store_true')
    parser.add_argument('--subtitles', action='store_true')
    args = parser.parse_args()
    subtitle_window = None
    if args.time:
        print("timings enabled")
    if args.subtitles:
        print("subtitles enabled")
        subtitle_window = SubtitleWindow()
  
        
    # in a thead
    main_thread = threading.Thread(target=main, args=(subtitle_window,args.time))
    main_thread.start()
    # run the subtitle window
    if subtitle_window:
        subtitle_window.run()

    else:
        while True:
            time.sleep(1)

