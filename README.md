RedshiftScience ASH-Server

Combined llama.cpp+piperTTS+MangioRVC in a single docker container

** RTX 3060 example with 13b llama2 **


https://github.com/RedshiftScience/ash-server/assets/61531193/713b7fd6-9215-468e-9b55-db4f89128339


** RTX 3090 example with 13b llama2 **



https://github.com/RedshiftScience/ash-server/assets/61531193/ff0222a3-9639-47b0-970a-0db3616b07e7

**Running**
The above test were ran with the text-tts-rvc-gen-streaming.py example
- ```cd examples/```
- ```pip install -r requirements.txt```
- ```python text-tts-rvc-gen-streaming.py```

There is cli options --time for printing timings and --subtitles to enable a subtitle window.

**Tested with**

- RTX 3060 12GB VRAM
  - 7b q4_0, 2048 ctx
- RTX 3090 24GB VRAM
  - 13b q6_K 4096 ctx


**TODO**

- documentation
- usage guide
- finish examples
