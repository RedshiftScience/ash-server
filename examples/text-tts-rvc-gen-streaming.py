
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

from subtitles import SubtitleWindow
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
        return piper_audio_bytes


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


def tts(text,timings=False, subtitle_window=None):
    # split into sentences using . ? , and !
    sentences = []
    current_sentence = ""
    for char in text:
        current_sentence += char
        if char in [".", "?", "!"]:
            sentences.append(current_sentence)
            current_sentence = ""

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
    for sentence in sentences:
        audio_bytes = piper(sentence,timings=timings)
        audio_bytes = rvc(audio_bytes,timings=timings)
        audio_bytes_sum += audio_bytes

    if subtitle_window:
        subtitle_thread = threading.Thread(target=write_subtitle, args=(subtitle_window,sentences))
        subtitle_thread.start()
    return audio_bytes_sum

def play_audio(audio_bytes):
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

def tts_loop(subtitleWindow,timings=False):
    
  
    while True:
        input_text = input("tts: ")
        if input_text == "exit":
            break

        audio_bytes = tts(input_text,timings=timings, subtitle_window=subtitleWindow)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        # write to a wav
        # play audio in a thread
        audio_thread = threading.Thread(target=play_audio, args=(audio_np,))
        audio_thread.start()
          



def tts_wav(text, path, timings=False):
    print("timings:")
    start = time.perf_counter()
    audio_bytes = tts(text,timings=timings)
    with sf.SoundFile(path, 'w', samplerate=40000, channels=1, format='wav') as f:
        # convert to int16
        audio_bytes = np.frombuffer(audio_bytes, dtype=np.int16)
        f.write(audio_bytes)
    end = time.perf_counter()
    if timings:
        # in ms
        print(f"tts to wav: {(end-start)*1000:.2f} ms")        




import requests
import ash_cfgs
import aiohttp
import json
import asyncio
import time
# TODO add error handling
def embed(text):

    url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"
    # post to API_SERVER /embedding
    with requests.post(f"{url}/embedding", json={"content": text}) as response:
        print(response)
        if response.status_code != 200:
            return None
        return response.json()["embedding"]

# TODO add error handling
def tokenize(text):

    url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"
    # post to API_SERVER /embedding
    try:
        with requests.post(f"{url}/tokenize", json={"content": text}, timeout=30.0) as response:
            if response.status_code != 200:
                return None
            return response.json()["tokens"]
    except Exception as e:
        print(e)
        return None
    


# generator_lock = asyncio.Lock()

async def token_generator(prompt):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                stops = ash_cfgs.llama_cpp_stop_cfg.splitlines()
                data = {
                    'prompt': prompt,
                    'temperature': ash_cfgs.llama_cpp_temp_cfg,
                    'top_p': ash_cfgs.llama_cpp_top_p_cfg,
                    'top_k': ash_cfgs.llama_cpp_top_k_cfg,
                    'n_predict': ash_cfgs.llama_cpp_n_predict_cfg,
                    'stream':  True,
                    'stop': stops,
                    'repetition_penalty': ash_cfgs.llama_cpp_repetition_penalty_cfg,
                    'mirostat_mode': ash_cfgs.llama_cpp_mirostat_mode_cfg,
                    'mirostat_tau': ash_cfgs.llama_cpp_mirostat_tau_cfg,
                    'mirostat_eta': ash_cfgs.llama_cpp_mirostat_eta_cfg
                }
                # print(data)
                
        
                url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"
                async with session.post(f'{url}/completion', json=data) as response:
                    if response.status != 200:
                        yield None
                    
                    data_accumulator = b''  # Accumulate binary data
                    async for chunk in response.content.iter_any():
                        data_accumulator += chunk  # Append the chunk to the accumulator

                        # Check if the accumulated data contains a complete UTF-8 string
                        while b'\n' in data_accumulator:
                            # check for skip signal
                            
                            line, data_accumulator = data_accumulator.split(b'\n', 1)

                            line = line.decode('utf-8')
                            
                            if line.startswith('data: '):
                                response = json.loads(line[6:])
                                token = response['content']
                                yield token
                                if response['stop']:
                                    print("Completed")
                                    return 
        # wait if url is not available
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print("waiting for llm to be available")
            await asyncio.sleep(1)

        except requests.exceptions.ConnectionError:
            print("waiting for llm to be available")
            await asyncio.sleep(1)
        
                        
# TODO add error handling
async def accumulate_tokens(token_stream):
    sentence = ""
    async for token in token_stream:
        sentence += token
        if '!' in token or '?' in token or '.' in token:
            yield sentence.strip()
            sentence = ""

# TODO add error handling
async def get_sentence(gen_prompt):
   
    async for sentence in accumulate_tokens(token_generator(gen_prompt)):

        yield sentence



async def main(subtitleWindow,timings=False):
    history = []
    while True:
        in_text = input("User: ")
        in_text = f"User: {in_text}"
        history.append(in_text)
        start = time.perf_counter()

        if in_text == "exit":
            break

        # gfet response generator
        response_generator = get_sentence("\n".join(history))
        # loop through responses and tts them
        async for response in response_generator:
            end = time.perf_counter()
            if True:
                # in ms
                print(f"llm: {(end-start)*1000:.2f} ms")
            start = time.perf_counter()
            print(f"{response}")
            history.append(response)
            audio_bytes = tts(response,timings=timings, subtitle_window=subtitleWindow)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            # write to a wav
            # play audio in a thread
            play_audio(audio_np)
            
        
    sys.exit(0)

def run_main(subtitleWindow,timings=False):
    asyncio.run(main(subtitleWindow,timings=timings))

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
    main_thread = threading.Thread(target=run_main, args=(subtitle_window,args.time))
    main_thread.start()
    # run the subtitle window
    if subtitle_window:
        subtitle_window.run()

    else:
        while True:
            time.sleep(1)

