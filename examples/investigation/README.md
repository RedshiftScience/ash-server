**Investigation into speed of TTS**

piper + rvc:

https://github.com/RedshiftScience/ash-server/assets/61531193/14dc4a24-d2f8-4bfc-9a31-23cec799898c


edge-tts + rvc:

https://github.com/RedshiftScience/ash-server/assets/61531193/15be524b-62fc-4dc8-b94f-b1efcd4a8572



Short Sentences (1 Chunk):

| TTS | First Chunk (ms) | Total (ms) |Audio |
| --- | ----- | ----- | --- |
| piper | 149.07 | 149.07 | [piper.wav](piper.wav) | 
| edge-tts | 306.58 | 306.58 | [edge-tts.wav](edge-tts.wav)  |
| piper + rvc | 731.24 | 731.26 | [output-1-short.wav](output-1-short.wav) |
| edge-tts + rvc | 836.44 | 836.44 | [output-2-short.wav](output-2-short.wav) |
| edge-tts + Applio | 2007.32 |2007.32 | [output-3-short.wav](output-3-short.wav) |

Long Sentences (5 Chunks):

| TTS | First Chunk (ms) | Total (ms) |Audio |
| --- | ----- | ----- | ---- |
| piper | 168.62 | 804.76 |  |
| edge-tts | 824.91 | 3550.4 |  |
| piper + rvc | 1011.96 | 5603.78 | [output-1-long.wav](output-1-long.wav) |
| edge-tts + rvc | 1769.56 | 8609.78 | [output-2-long.wav](output-2-long.wav) |
| edge-tts + Applio | 2379.64 | 12392.70 |  [output-3-long.wav](output-3-long.wav) |


A "Chunk" means a return of audio from the endpoint, longer sentences are split by punctuation before they are sent to each TTS.

Aria edge-tts vs trains vits piper:



https://github.com/RedshiftScience/ash-server/assets/61531193/ddc0a6be-0565-4464-80a1-e53af33fce95


https://github.com/RedshiftScience/ash-server/assets/61531193/3453cfd8-0b4a-4eec-8e2f-112f534ec0c2


https://github.com/RedshiftScience/ash-server/assets/61531193/13fbae4e-a8d0-4d8e-ac83-5da5e9601b58


https://github.com/RedshiftScience/ash-server/assets/61531193/736e916b-9c39-4961-9f34-3356a4ad4c55


Tested sentences:

| Type | Sentence|
| ---- | ------- |
| Short | ```This is a short sentence.``` |
| Long | ```Once upon a time in the whimsical land of toasts, there resided a courageous little toaster named Toasty. He was a master of his craft, known throughout the land for his ability to turn ordinary bread into the most delectable, golden-brown toasts. Toasty's cozy cottage was nestled amidst fields of wheat, where the aroma of freshly baked bread wafted through the air. One bright morning, as the sun painted the sky in shades of orange and pink, Toasty decided it was time to create his masterpiece, the legendary Mega-Toast. With great enthusiasm, he selected the finest loaf of bread he could find, and with precision, he popped it into his gleaming toaster slots.``` |

Screenshots:


- piper + rvc

  
![output-1-long](https://github.com/RedshiftScience/ash-server/assets/61531193/4335ac69-d219-4fda-b127-0614184c560b)

- edge-tts + rvc

![output-2-long](https://github.com/RedshiftScience/ash-server/assets/61531193/fc44d16b-54d8-4bf6-9c42-6611a82288c8)

- edge-tts + Applio

![output-3-long](https://github.com/RedshiftScience/ash-server/assets/61531193/7b80f06a-46b6-4a5f-83bc-c10d78295aaa)
