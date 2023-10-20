RedshiftScience ASH-Server

Combined llama.cpp+piperTTS+MangioRVC in a single docker container

**RTX 3060 example with 13b llama2**


https://github.com/RedshiftScience/ash-server/assets/61531193/713b7fd6-9215-468e-9b55-db4f89128339


**RTX 3090 example with 13b llama2**



https://github.com/RedshiftScience/ash-server/assets/61531193/ff0222a3-9639-47b0-970a-0db3616b07e7

**Running**

The above test were ran with the text-tts-rvc-gen-streaming.py example

First you need enough ram on a GPU, suggest minnimum 12GB to have a somewhat real time experience.

Then using docker pull to pull the ash-server

- ```docker pull redshiftscience/ash-server:latest```

Then run using a model from Huggingface and checkpoints of your choice at any url for piper and RVC (These are the ones in the example I am using).
You also need nvidia container toolkit installed for docker if you want to use your nvidida gpu.

- ```docker run -it --name ash-server -p 44332:44332 -p 50051:50051  -p 50052:50052  ash-server:latest "llama-2-13b.Q4_0.gguf" "TheBloke/Llama-2-13B-GGUF" "https://files.redshiftscience.com/api/public/dl/lMWjjCRp/rvcM/melba-toast.pth" "https://files.redshiftscience.com/api/public/dl/lMWjjCRp/piper/ashera.ckpt" "-c 1000 -v -t 1 --no-mmap -ngl 34 -mg 0 --host 0.0.0.0 --port 44332 --embedding"```

- ```cd examples/```
- ```pip install -r requirements.txt```
- ```python text-tts-rvc-gen-streaming.py```

There is cli options --time for printing timings and --subtitles to enable a subtitle window.

**Tested with**

- RTX 3060 12GB VRAM (Local)
  - 7b q4_0, 2048 ctx
- RTX 3090 24GB VRAM (Runpod)
  - 13b q6_K 4096 ctx


**TODO**

- documentation
- usage guide
