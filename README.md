# 🤖 Otto Offline Assistant

An offline, privacy-focused voice assistant built for Windows. Otto listens for a custom wake word ("Hey Otto"), records your speech, transcribes it locally using Whisper, generates a response via a local LLM server (`llama.cpp`), and speaks back using Piper TTS—completely offline!

---

## 🏗️ System Architecture & Data Flow

Otto runs entirely locally on your machine, ensuring complete data privacy and zero cloud dependencies. 

```text
 ┌───────────────┐     Audio Stream     ┌───────────────────┐
 │  Microphone   │ ───────────────────► │  openWakeWord     │ (Detects "Hey Otto")
 └───────────────┘                      └───────────────────┘
                                                  │ (Wake Word Triggered)
                                                  ▼
 ┌───────────────┐      WAV Audio       ┌───────────────────┐
 │   Speaker     │ ◄─────────────────── │    Piper TTS      │ (Synthesizes Response)
 └───────────────┘                      └───────────────────┘
         ▲                                        ▲
         │ Text Response                          │ Text Response
 ┌───────────────┐     JSON (REST API)  ┌───────────────────┐
 │  llama.cpp    │ ◄─────────────────── │   whisper.cpp     │ (Transcribes Audio)
 │ (Local LLM)   │                      └───────────────────┘
 └───────────────┘
