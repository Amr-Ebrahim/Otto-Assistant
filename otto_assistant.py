import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyaudio
import numpy as np
import subprocess
import os
import wave
import time
import json
import re
import urllib.request
import winsound
from math import gcd
from scipy.signal import resample_poly
from openwakeword.model import Model

# =========================================================
# SETTINGS
# =========================================================

PROJECT_DIR = r"C:\otto-assistant"

MIC_DEVICE_INDEX = 1
MIC_NATIVE_RATE = 44100
SAMPLE_RATE = 16000
CHANNELS = 1

WAKE_THRESHOLD = 0.005
SILENCE_DURATION = 1.5
MAX_RECORD_SECONDS = 8
CONVERSATION_IDLE_TIMEOUT = 8

# =========================================================
# PATHS
# =========================================================

WAKE_MODEL = os.path.join(PROJECT_DIR, "models", "wake", "hey_otto.onnx")

WHISPER_EXECUTABLE = os.path.join(PROJECT_DIR, "models", "whisper", "Release", "whisper-cli.exe")
WHISPER_MODEL = os.path.join(
    PROJECT_DIR,
    "models",
    "whisper",
    "ggml-large-v3.bin"
)

LLAMA_SERVER_URL = "http://localhost:8080/v1/chat/completions"

PIPER_EXECUTABLE = os.path.join(PROJECT_DIR, "models", "tts", "piper", "piper.exe")
PIPER_MODEL_EN = os.path.join(PROJECT_DIR, "models", "tts", "en_US-amy-medium.onnx")
PIPER_MODEL_AR = os.path.join(PROJECT_DIR, "models", "tts", "ar_JO-kareem-medium.onnx")

AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
RECORDING_WAV = os.path.join(AUDIO_DIR, "otto_recording.wav")
RESPONSE_WAV = os.path.join(AUDIO_DIR, "otto_response.wav")

os.makedirs(AUDIO_DIR, exist_ok=True)

# =========================================================
# WAKE WORD MODEL
# =========================================================

oww_model = Model(wakeword_models=[WAKE_MODEL])

# =========================================================
# HELPERS
# =========================================================

def is_arabic(text):
    return any('\u0600' <= ch <= '\u06FF' for ch in text)


def resample_audio(audio_data, orig_rate, target_rate):
    g = gcd(orig_rate, target_rate)
    up = target_rate // g
    down = orig_rate // g
    resampled = resample_poly(audio_data, up, down)
    return resampled.astype(np.int16)


def speak(text):
    text = str(text).strip()
    print("\nTTS TEXT:", repr(text))

    if not text:
        return

    model_to_use = PIPER_MODEL_AR if is_arabic(text) else PIPER_MODEL_EN

    try:
        subprocess.run(
            [PIPER_EXECUTABLE, "--model", model_to_use, "--output_file", RESPONSE_WAV],
            input=text.encode("utf-8"),
            check=True
        )
        winsound.PlaySound(RESPONSE_WAV, winsound.SND_FILENAME)
    except Exception as e:
        print("❌ TTS error:", e)


# =========================================================
# WAKE WORD LISTENING
# =========================================================

def wait_for_wake_word():
    print("\n" + "=" * 50)
    print("Otto is listening for: Hey Otto")
    print("=" * 50)

    audio = pyaudio.PyAudio()
    native_chunk_size = int(1280 * MIC_NATIVE_RATE / SAMPLE_RATE)

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=MIC_NATIVE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=native_chunk_size
    )

    try:
        while True:
            audio_bytes = stream.read(native_chunk_size, exception_on_overflow=False)
            raw_data = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_data = resample_audio(raw_data, MIC_NATIVE_RATE, SAMPLE_RATE)

            prediction = oww_model.predict(audio_data)
            score = float(prediction.get("hey_otto", 0))

            if score >= WAKE_THRESHOLD:
                print(f"\nWake word detected! Score: {score:.2f}")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return True

    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        raise


# =========================================================
# RECORD USER SPEECH (with silence detection)
# =========================================================

def record_speech(max_seconds=MAX_RECORD_SECONDS):
    print("\n🎤 Listening...")

    audio = pyaudio.PyAudio()
    native_chunk_size = int(1600 * MIC_NATIVE_RATE / SAMPLE_RATE)

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=MIC_NATIVE_RATE,
        input=True,
        input_device_index=MIC_DEVICE_INDEX,
        frames_per_buffer=native_chunk_size
    )

    SPEECH_THRESHOLD = 500
    CHUNK_DURATION = 0.1

    frames = []
    speech_started = False
    silence_time = 0.0
    waiting_time = 0.0

    try:
        while True:
            chunk = stream.read(native_chunk_size, exception_on_overflow=False)
            raw_samples = np.frombuffer(chunk, dtype=np.int16)
            resampled = resample_audio(raw_samples, MIC_NATIVE_RATE, SAMPLE_RATE)
            rms = np.sqrt(np.mean(resampled.astype(np.float32) ** 2))

            frames.append(resampled.tobytes())

            if not speech_started:
                waiting_time += CHUNK_DURATION
                if rms >= SPEECH_THRESHOLD:
                    speech_started = True
                    silence_time = 0.0
                    print(f"🗣️ Speech detected (RMS: {rms:.0f})")
                elif waiting_time >= max_seconds:
                    stream.stop_stream()
                    stream.close()
                    audio.terminate()
                    return False
            else:
                if rms < SPEECH_THRESHOLD:
                    silence_time += CHUNK_DURATION
                    if silence_time >= SILENCE_DURATION:
                        break
                else:
                    silence_time = 0.0

        stream.stop_stream()
        stream.close()
        audio.terminate()

        if not frames:
            return False

        with wave.open(RECORDING_WAV, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))

        return True

    except Exception as e:
        print("❌ Recording error:", e)
        try:
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception:
            pass
        return False


# =========================================================
# WHISPER TRANSCRIPTION
# =========================================================

def transcribe():
    print("\n🧠 Whisper is processing...")

    try:
        result = subprocess.run(
            [WHISPER_EXECUTABLE, "-m", WHISPER_MODEL, "-f", RECORDING_WAV, "-nt", "-l", "auto"],
            capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode != 0:
            print("❌ Whisper error:", result.stderr)
            return ""

        text = result.stdout.strip()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        final_text = " ".join(lines).strip()

        print("\n📝 Transcription:", final_text)
        return final_text

    except Exception as e:
        print("❌ Whisper exception:", e)
        return ""


# =========================================================
# ASK LLM
# =========================================================

def ask_llm(user_text):
    print("\n🤖 Asking Qwen...")

    user_is_arabic = is_arabic(user_text)
    language_instruction = "Respond ONLY in Arabic." if user_is_arabic else "Respond ONLY in English. Do not use Arabic script."

    system_prompt = (
        "You are Otto, a friendly offline robot assistant. "
        f"{language_instruction} "
        "Keep answers short, clear, and helpful."
    )

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_text}\n\n({language_instruction})"}
        ],
        "temperature": 0.3,
        "max_tokens": 100
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            LLAMA_SERVER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result["choices"][0]["message"]["content"].strip()
        print("\n🤖 Otto:", answer)
        return answer

    except Exception as e:
        print("❌ LLM error:", e)
        return ""


# =========================================================
# MAIN LOOP
# =========================================================

def main():
    print("\n" + "=" * 60)
    print("              OTTO OFFLINE ASSISTANT (Windows)")
    print("=" * 60)

    while True:
        try:
            wait_for_wake_word()
            speak("Yes, how can I help?")

            while True:
                recorded = record_speech(max_seconds=CONVERSATION_IDLE_TIMEOUT)

                if not recorded:
                    print("\n💤 No speech — returning to wake-word mode.")
                    break

                user_text = transcribe()
                if not user_text:
                    print("No speech understood — returning to wake-word mode.")
                    break

                answer = ask_llm(user_text)
                if not answer:
                    speak("Sorry, I couldn't generate an answer.")
                    break

                speak(answer)
                print("\n💬 Conversation mode: waiting for next question...")

        except KeyboardInterrupt:
            print("\n\nOtto stopped.")
            break

        except Exception as e:
            print("\n❌ Unexpected error:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()