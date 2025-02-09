#!/bin/bash

IMAGE_NAME="chatbot-voice"

echo "🚀 Bắt đầu build Docker image: $IMAGE_NAME..."

docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Build thất bại! Kiểm tra lỗi và thử lại."
    exit 1
fi

echo "✅ Build thành công!"

echo "🔧 Kiểm tra quyền truy cập microphone..."
if [ ! -d "/dev/snd" ]; then
    echo "❌ Không tìm thấy thiết bị âm thanh! Hãy kiểm tra lại microphone."
    exit 1
fi

echo "🎤 Microphone hoạt động tốt!"

echo "🚀 Chạy chatbot trong Docker container..."
docker run -it --rm --device /dev/snd --name chatbot-container $IMAGE_NAME
