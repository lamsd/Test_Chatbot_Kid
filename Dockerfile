
FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
WORKDIR /app
RUN apt update && apt install -y \
    python3-pip \
    python3-dev \
    git \
    curl \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "chatbot_voice.py"]
