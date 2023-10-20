#!/bin/bash
MODEL_NAME=${1:-"llama-2-13b-chat.ggmlv3.q6_K.bin"}
MODEL_REPO=${2:-"TheBloke/Llama-2-13B-chat-GGML"}
RVC_MODEL=${3:-"ashera.pth"}
PIPER_MODEL=${4:-"ashera.ckpt"} 
LLAMACPP_ARGS=${5:-"-c 4096 -v -t 1 --no-mmap -ngl 99 -mg 0 --host 0.0.0.0 --port 44332 --embedding"}


echo "starting servers..."

# Start serverPIPER
echo "starting serverPIPER..."
source /app/piper/.venv/bin/activate
cd /app/piper/src/python

python -m piper_train.serverPIPER --model $PIPER_MODEL &
echo "serverPIPER started"
# deactivate

# Start serverRVC
echo "starting serverRVC..."
source /app/rvc/venv/bin/activate
which python3
cd /app/rvc/
# export CUDA_VISIBLE_DEVICES=1
python3 serverRVC.py --model_name $RVC_MODEL &
echo "serverRVC started"
# deactivate


if [ ! -f "/app/LLM/models/$MODEL_NAME" ]; then
    echo "model file $MODEL_NAME not found, downloading..."
    wget -O "/app/LLM/models/$MODEL_NAME" "https://huggingface.co/$MODEL_REPO/resolve/main/$MODEL_NAME" -P /app/LLM/models/
fi

/app/LLM/server -m "/app/LLM/models/$MODEL_NAME" $LLAMACPP_ARGS


