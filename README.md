<h1 align="center">Otto — Offline Voice Assistant</h1>
<p align="center">
  A privacy-first voice assistant for Windows that listens, thinks and speaks in <b>Arabic and English</b> —<br />
  wake word, speech recognition, LLM and text-to-speech all running on your own machine.
</p>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python\&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/platform-Windows-0B1020" alt="Platform: Windows" />
  <img src="https://img.shields.io/badge/runs-100%25%20offline-22D3EE" alt="Runs 100% offline" />
  <img src="https://img.shields.io/badge/languages-Arabic%20%7C%20English-A78BFA" alt="Languages: Arabic and English" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" />
</p>
<p align="center">
  ☁️ No GPU? Try <a href="https://github.com/Amr-Ebrahim/Otto-Cloud"><b>Otto Cloud</b></a>, the free cloud edition that runs on any laptop and speaks Egyptian Arabic.
</p>
<p align="center">
  <img src="otto-pipeline.svg" width="100%" alt="Otto pipeline: microphone, openWakeWord wake word, whisper.cpp speech-to-text, llama.cpp local LLM, Piper text-to-speech." />
</p>
---
Why Otto?
Most voice assistants send your voice to a server. Otto doesn't. Every step — hearing the wake word, turning speech into text, generating an answer and speaking it back — runs locally, so it works without internet and nothing you say leaves your computer.
Custom wake word — say "Hey Otto" to start a conversation (openWakeWord).
Bilingual speech recognition — Whisper large-v3 auto-detects Arabic or English (whisper.cpp).
Local LLM — Qwen2.5-7B-Instruct served by llama.cpp through an OpenAI-compatible API.
Replies in your language — if you speak Arabic, Otto answers in Arabic; if you speak English, it answers in English.
Natural voices — Piper neural TTS with separate English and Arabic voices.
Conversation mode — after answering, Otto keeps listening for follow-up questions until you stay quiet for 8 seconds.
Zero telemetry — no accounts, no API keys, no cloud calls.
How it works
```mermaid
flowchart LR
    MIC(\[🎙️ Microphone]) --> WAKE\[openWakeWord<br/><i>“Hey Otto”</i>]
    WAKE --> REC\[Record speech<br/><i>silence detection</i>]
    REC --> STT\[whisper.cpp<br/><i>large-v3 · auto language</i>]
    STT --> LLM\[llama.cpp server<br/><i>Qwen2.5-7B-Instruct</i>]
    LLM --> TTS\[Piper TTS<br/><i>EN or AR voice</i>]
    TTS --> SPK(\[🔊 Speaker])
    SPK -. follow-up question .-> REC
```
Otto listens to the microphone continuously and scores each 80 ms audio frame with a custom "Hey Otto" wake-word model.
Once triggered, it greets you and records until you stop talking (1.5 s of silence).
whisper.cpp transcribes the recording and detects the language automatically.
The text is sent to a local llama.cpp server, with an instruction to answer in the same language.
Piper speaks the answer with an Arabic or English voice, depending on the script of the reply.
The full design — components, timing, language routing and data flow — is in ARCHITECTURE.md.
Tech stack
Stage	Tool	Model used	Runs on
Wake word	openWakeWord	custom `hey\_otto.onnx`	CPU
Speech-to-text	whisper.cpp	`ggml-large-v3.bin`	CPU or NVIDIA GPU
Language model	llama.cpp (`llama-server`)	Qwen2.5-7B-Instruct (GGUF)	CPU or GPU
Text-to-speech	Piper	`en\_US-amy-medium`, `ar\_JO-kareem-medium`	CPU
Audio I/O	PyAudio, SciPy, `winsound`	—	—
Quick start
> Full step-by-step setup, including downloading every model and running the LLM server, is in \*\*\[INSTALLATION.md](INSTALLATION.md)\*\*.
```powershell
# 1. Get the code (the script expects this exact folder)
git clone https://github.com/Amr-Ebrahim/Otto-Assistant.git C:\\otto-assistant
cd C:\\otto-assistant

# 2. Install Python dependencies
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt

# 3. Download the models into C:\\otto-assistant\\models (see INSTALLATION.md)

# 4. Start the local LLM server (in a separate terminal)
llama.cpp\\llama-server.exe -m models\\llm\\qwen2.5-7b-instruct-q4\_k\_m.gguf --port 8080 -ngl 99

# 5. Run Otto
python otto\_assistant.py
```
Then say "Hey Otto" and ask your question.
Configuration
All settings live at the top of `otto\_assistant.py`:
Setting	Default	What it does
`PROJECT\_DIR`	`C:\\otto-assistant`	Root folder for `models/` and `audio/`
`MIC\_DEVICE\_INDEX`	`1`	Which microphone to use (how to find yours)
`MIC\_NATIVE\_RATE`	`44100`	Your microphone's sample rate; audio is resampled to 16 kHz
`WAKE\_THRESHOLD`	`0.005`	Wake-word score needed to trigger
`SILENCE\_DURATION`	`1.5`	Seconds of silence that end a question
`CONVERSATION\_IDLE\_TIMEOUT`	`8`	Seconds Otto waits for a follow-up before going back to sleep
`LLAMA\_SERVER\_URL`	`http://localhost:8080/v1/chat/completions`	Local LLM endpoint
Project structure
```text
otto-assistant/
├── otto\_assistant.py      # Main loop: wake word → record → transcribe → LLM → speak
├── requirements.txt       # Python dependencies
├── INSTALLATION.md        # Full setup guide (models, LLM server, microphone)
├── ARCHITECTURE.md        # System design and data flow
├── otto-pipeline.svg      # Pipeline diagram
├── models/                # Model files — downloaded locally, not in git
│   ├── wake/              #   hey\_otto.onnx
│   ├── whisper/           #   whisper-cli.exe (in Release/) + ggml-large-v3.bin
│   ├── llm/               #   Qwen2.5-7B-Instruct GGUF
│   └── tts/               #   piper/piper.exe + voice .onnx files
├── llama.cpp/             # llama-server binaries — not in git
└── audio/                 # Temporary recordings and replies — not in git
```
Hardware
Otto runs on CPU, but a GPU makes it much faster. Rough model sizes on disk:
Model	Size	Lighter alternative
Whisper large-v3	3.1 GB	`ggml-large-v3-turbo` (1.6 GB) or `ggml-large-v3-turbo-q5\_0` (574 MB)
Qwen2.5-7B-Instruct Q4_K_M	4.7 GB	Qwen2.5-3B-Instruct GGUF
Piper voices	~60 MB each	—
With an NVIDIA GPU, use the CUDA builds of whisper.cpp and llama.cpp. On a CPU-only machine, the lighter alternatives above keep response times reasonable.
Egyptian Arabic voice (optional)
The script in this repository uses Piper's `ar\_JO-kareem-medium` voice for Arabic. For a more natural Egyptian Arabic voice, I run VoiceTut-TTS locally on the GPU instead — an open-source model fine-tuned on Egyptian Arabic speech that also handles Arabic–English code-switching. Setup and the code change are in INSTALLATION.md.
Cloud edition
Don't have a strong PC or a GPU? Otto Cloud is the same assistant rebuilt on free cloud APIs (Groq Whisper, gpt-oss-120b and Gemini TTS). It runs on any Windows laptop, speaks natural Egyptian Arabic, and costs $0 on the free tiers.
Acknowledgements
Otto is built on these open-source projects:
openWakeWord ·
whisper.cpp ·
llama.cpp ·
Piper ·
Qwen2.5 ·
VoiceTut-TTS
License
Released under the MIT License. Each model and tool above keeps its own license.
