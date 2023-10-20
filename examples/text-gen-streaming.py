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
    


generator_lock = asyncio.Lock()

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
                print(data)
                
        
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
    async with generator_lock:
       
        async for sentence in accumulate_tokens(token_generator(gen_prompt)):

            yield sentence

async def main_async():
    # loop user input, print streamed output until stop signal

    while True:
        gen_prompt = input("prompt: ")
        if gen_prompt == "exit":
            break
        async for sentence in get_sentence(gen_prompt):
            print(sentence)

def main():
    # loop user input, print streamed output until stop signal

    asyncio.run(main_async())

if __name__ == "__main__":
    main()