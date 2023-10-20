ARG UBUNTU_VERSION=20.04
# This needs to generally match the container host's environment.
ARG CUDA_VERSION=11.8.0
# Target the CUDA build image
ARG BASE_CUDA_DEV_CONTAINER=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
# Target the CUDA runtime image
# ARG BASE_CUDA_RUN_CONTAINER=nvidia/cuda:${CUDA_VERSION}-cudnn8-runtime-ubuntu${UBUNTU_VERSION}

FROM ${BASE_CUDA_DEV_CONTAINER} 
# Unless otherwise specified, we make a fat build.
ARG CUDA_DOCKER_ARCH=all

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common && \
    DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install build-essential git python3.9 python3.9-dev python3.9-distutils tmux curl wget python3.9-venv -y



# Set Python 3.9 as the default python
RUN ln -sf /usr/bin/python3.9 /usr/bin/python
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3

# install pip

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

RUN python3 get-pip.py

RUN python3 -m pip install --upgrade pip


WORKDIR /app


# =================================
# clone llama.cpp and build server
# =================================
RUN git clone https://github.com/RedshiftScience/llama.cpp ./LLM
WORKDIR /app/LLM

# last tested commit
RUN git checkout 6b3ae4da92485f979a0f45774fcf68597634db0b

# Set nvcc architecture
ENV CUDA_DOCKER_ARCH=${CUDA_DOCKER_ARCH}
# Enable cuBLAS
ENV LLAMA_CUBLAS=1

ENV LAMA_CUDA_DMMV_Y=2

ENV LLAMA_CUDA_DMMV_X=64

ENV CUDA_VISABLE_DEVICES=0

# ENV CUDA_ARCHITECTURES=OFF

ENV LLAMA_BUILD_SERVER=1

RUN echo $CUDA_VISABLE_DEVICES && ls

RUN make 


WORKDIR /app


# # =================================
# # clone piper and install pip requirements
# # =================================

WORKDIR /app

RUN git clone https://github.com/RedshiftScience/piper piper

WORKDIR /app/piper

RUN python3 -m venv .venv

# last tested commit
RUN git checkout c01ec88c6dd4c024d6796c13b91c35bd08f9e2b3

RUN . .venv/bin/activate && \
 pip3 install torch==2.0.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118 && \
 python3 -m pip install numpy==1.24.4 cython==0.29.35 espeak-phonemizer==1.3.1 librosa==0.10.0.post2 grpcio==1.54.2 grpcio-tools==1.54.2 pytorch-lightning==2.0.4 && \
 which python3

# COPY ./piper/src/python/piper_train/serverPIPER.py ./src/python/piper_train/serverPIPER.py
# COPY ./piper/src/python/ASH_grpc.proto ./src/python/ASH_grpc.proto
# COPY ./piper/src/python/ashera_piper.ckpt ./src/python/ashera_piper.ckpt
# COPY ./piper/src/python/rusty.ckpt ./src/python/rusty.ckpt


RUN . .venv/bin/activate && \
  cd src/python/piper_train/vits/monotonic_align && \
  mkdir -p monotonic_align && \
  cythonize -i core.pyx && \
  mv core*.so monotonic_align && \
  cd /app/piper
WORKDIR /app/piper


RUN . .venv/bin/activate && \
 cd src/python/piper_train && \
 python3 -m grpc_tools.protoc -I./ --python_out=../ --grpc_python_out=../ ./ASH_grpc.proto

WORKDIR /app

RUN git clone https://github.com/rhasspy/espeak-ng espeak-ng

WORKDIR /app/espeak-ng

# config make and install under /usr/lib/x86_64-linux-gnu

RUN apt install make autoconf automake libtool pkg-config -y
RUN ./autogen.sh && \
 ./configure --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu && \
 make -j && \
 make install



# # =================================
# # clone rvc and install pip requirements
# # =================================

WORKDIR /app

# RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI rvc
RUN git clone https://github.com/RedshiftScience/rvcM rvc

# last tested commit
RUN cd rvc  && git checkout  b0adfed02c6e655aa15869dc6614b873733e273b

WORKDIR /app/rvc




# make venv

RUN python3 -m venv venv

RUN  . venv/bin/activate && \
git clone https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder.git && \
cd Python-Wrapper-for-World-Vocoder && \
git submodule update --init && \
pip install -U pip  && \
pip install -r requirements.txt  && \
pip install .  


RUN . venv/bin/activate && \
 pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118 && \
 python3 -m pip install -r requirements.txt && \
 which python3


# COPY ./rvcM/serverRVC.py ./serverRVC.py
# COPY ./rvcM/config.py ./config.py
# COPY ./rvcM/ASH_grpc.proto ./ASH_grpc.proto
# COPY ./rvcM/hubert_base.pt ./hubert_base.pt
# COPY ./rvcM/weights ./weights
# COPY ./rvcM/pretrained_v2 ./pretrained_v2
# COPY ./rvcM/logs/ashera2/added_IVF817_Flat_nprobe_1_ashera2_v2.index ./logs/ashera2/added_IVF817_Flat_nprobe_1_ashera2_v2.index
RUN wget https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt -O hubert_base.pt

RUN . venv/bin/activate && \
 pip install grpcio-tools==1.54.2 grpcio==1.54.2 && \
 python3 -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./ASH_grpc.proto



WORKDIR /app


COPY ./launch.sh /app/launch.sh

RUN chmod +x /app/launch.sh


EXPOSE 44332
EXPOSE 50051
EXPOSE 50052

ENTRYPOINT [ "/app/launch.sh" ]
