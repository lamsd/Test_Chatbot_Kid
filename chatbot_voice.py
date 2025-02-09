import sounddevice as sd
import numpy as np
import wave
import torch
from transformers import MarianMTModel, MarianTokenizer
import language_tool_python
from vosk import Model, KaldiRecognizer
import json
import os
from coqui_tts.tts import TTS


MODEL_VOSK = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
DURATION = 5  
ACTIVATION_KEYWORDS = ["hey chatbot"]  


model_name = "Helsinki-NLP/opus-mt-vi-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)


grammar_tool = language_tool_python.LanguageTool("en-US")


if not os.path.exists(MODEL_VOSK):
    raise ValueError("Vui lòng tải mô hình Vosk vào thư mục `vosk-model`!")
vosk_model = Model(MODEL_VOSK)


tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")


def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE):
    print("🎤 Đang ghi âm... Nói vào mic!")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    print("✅ Hoàn tất ghi âm!")
    return recording


def speech_to_text(audio_data, sample_rate=SAMPLE_RATE):
    recognizer = KaldiRecognizer(vosk_model, sample_rate)
    
    
    audio_bytes = audio_data.tobytes()
    if recognizer.AcceptWaveform(audio_bytes):
        result = recognizer.Result()
        text = json.loads(result)["text"]
        return text
    return ""


def contains_activation_keyword(text):
    return any(keyword in text.lower() for keyword in ACTIVATION_KEYWORDS)


def translate_vi_en(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text


def correct_grammar(text):
    matches = grammar_tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text


def text_to_speech(text, output_file="output.wav"):
    tts.tts_to_file(text=text, file_path=output_file)
    print(f"🔊 Đã tạo file âm thanh: {output_file}")
    return output_file


def chatbot():
    print("🎙️ Chatbot dạy tiếng Anh (Hãy nói từ khóa để bắt đầu)")

    while True:
        print("\n🟢 Hãy nói từ khóa kích hoạt...")
        audio_data = record_audio(duration=3)  
        user_text = speech_to_text(audio_data)

        if not user_text:
            print("⚠️ Không nhận diện được giọng nói, thử lại!")
            continue

        print(f"📢 Bạn nói: {user_text}")

        
        if not contains_activation_keyword(user_text):
            print("❌ Không có từ khóa kích hoạt, bỏ qua.")
            continue

        print("✅ Đã nhận từ khóa! Hãy nói câu tiếng Việt để dịch...")

        
        audio_data = record_audio()
        user_text = speech_to_text(audio_data)

        if not user_text:
            print("⚠️ Không nhận diện được giọng nói, thử lại!")
            continue

        print(f"📢 Bạn nói: {user_text}")

        
        translated_text = translate_vi_en(user_text)
        corrected_text = correct_grammar(translated_text)

        print(f"📝 Bản dịch: {translated_text}")
        print(f"✅ Câu đúng: {corrected_text}")

        
        audio_file = text_to_speech(corrected_text)
        os.system(f"aplay {audio_file}")


if __name__ == "__main__":
    chatbot()
