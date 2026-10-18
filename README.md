# 🤖 Otto Offline Assistant

An offline, privacy-focused voice assistant built for Windows. Otto listens for a custom wake word ("Hey Otto"), records your speech, transcribes it locally using Whisper, generates a response via a local LLM server (`llama.cpp`), and speaks back using Piper TTS—completely offline!

## 🚀 Features
- Custom wake word detection using `openWakeWord`.
- Offline speech-to-text with `whisper.cpp`.
- Local LLM generation supporting English and Arabic.
- Offline text-to-speech using `Piper TTS`.

## 🛠️ Setup & Installation
1. Clone the repo:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/otto-assistant.git](https://github.com/YOUR_USERNAME/otto-assistant.git)
   cd otto-assistant