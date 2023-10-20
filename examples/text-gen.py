import requests
import ash_cfgs
import json
import time
import threading
# TODO add error handling
def embed(text):

    url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"
    # post to API_SERVER /embedding
    with requests.post(f"{url}/embedding", json={"content": text}) as response:
        if response.status_code != 200:
            return None
        return response.json()["embedding"]

# TODO add error handling
def tokenize(text):

    url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"
    # post to API_SERVER /tokenize
    try:
        with requests.post(f"{url}/tokenize", json={"content": text}, timeout=60.0) as response:
            if response.status_code != 200:
                return None
            return response.json()["tokens"]
    except Exception as e:
        print(e)
        return None
    

generator_lock = threading.Lock()

def generate(prompt):
    while True:
        try:
            with requests.Session() as s:
                stops = ash_cfgs.llama_cpp_stop_cfg.splitlines()
                data = {
                    'prompt': prompt,
                    'temperature': ash_cfgs.llama_cpp_temp_cfg,
                    'top_p': ash_cfgs.llama_cpp_top_p_cfg,
                    'top_k': ash_cfgs.llama_cpp_top_k_cfg,
                    'n_predict': ash_cfgs.llama_cpp_n_predict_cfg,
                    'stream': False,
                    'stop': stops,
                    'repetition_penalty': ash_cfgs.llama_cpp_repetition_penalty_cfg,
                    'mirostat_mode': ash_cfgs.llama_cpp_mirostat_mode_cfg,
                    'mirostat_tau': ash_cfgs.llama_cpp_mirostat_tau_cfg,
                    'mirostat_eta': ash_cfgs.llama_cpp_mirostat_eta_cfg
                }
                print(data)
                
        
                url = f"http://{ash_cfgs.llm_ip_cfg}:{ash_cfgs.llm_port_cfg}"

                response = s.post(f'{url}/completion', json=data)

                return response.json()["content"]
            
        # wait if url is not available
        except requests.exceptions.ConnectionError as e:
            print(e)
            time.sleep(1)
        
                        

def main():
    # loop user input, print streamed output until stop signal

    while True:
        gen_prompt = input("prompt: ")
        if gen_prompt == "exit":
            break
        
        response = generate(gen_prompt)
        print(response)

if __name__ == "__main__":
    main()