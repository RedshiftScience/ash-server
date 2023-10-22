**Investigation into speed of TTS**

Short Sentences (1 Chunk):

| TTS | First Chunk (ms) | Total (ms) |Audio |
| --- | ----- | ----- | --- |
| piper | 149.07 | 149.07 | | 
| edge-tts | 306.58 | 306.58 | |
| piper + rvc | 731.24 | 731.26 | [output-1-short.wav](output-1-short.wav) |
| edge-tts + rvc | 836.44 | 836.44 | [output-1-short.wav](output-2-short.wav) |
| edge-tts + Applio | 2007.32 |2007.32 | [output-1-short.wav](output-3-short.wav)|

Long Sentences (5 Chunks):

| TTS | First Chunk (ms) | Total (ms) |Audio |
| --- | ----- | ----- | ---- |
| piper | 168.62 | 804.76 |  |
| edge-tts | 824.91 | 3550.4 |  |
| piper + rvc | 1011.96 | 5603.78 | [output-1-short.wav](output-1-long.wav) |
| edge-tts + rvc | 1769.56 | 8609.78 | [output-1-short.wav](output-2-long.wav) |
| edge-tts + Applio | 2379.64 | 12392.70 |  [output-1-short.wav](output-3-long.wav) |


A "Chunk" means a return of audio from the endpoint, longer sentences are split by punctuation before they are sent to each TTS.

Tested sentences:

| Type | Sentence|
| ---- | ------- |
| Short | ```This is a short sentence``` |
| Long | ```Once upon a time in the whimsical land of toasts, there resided a courageous little toaster named Toasty. He was a master of his craft, known throughout the land for his ability to turn ordinary bread into the most delectable, golden-brown toasts. Toasty's cozy cottage was nestled amidst fields of wheat, where the aroma of freshly baked bread wafted through the air. One bright morning, as the sun painted the sky in shades of orange and pink, Toasty decided it was time to create his masterpiece, the legendary Mega-Toast. With great enthusiasm, he selected the finest loaf of bread he could find, and with precision, he popped it into his gleaming toaster slots.``` |

Screenshots:[output-3-long.webm](https://github.com/RedshiftScience/ash-server/assets/61531193/2d39f779-9934-441b-ab19-e719fe82ab47)


- piper + rvc

- edge-tts + rvc

- edge-tts + Applio
