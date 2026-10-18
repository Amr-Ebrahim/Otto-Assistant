# 🤖 Otto Offline Assistant

An advanced, fully offline, privacy-first voice assistant built for Windows. Otto handles custom wake-word detection, local speech transcription, local LLM generation (supporting English and Arabic), and neural text-to-speech synthesis without relying on any cloud APIs.

---

## 🏗️ System Architecture & Pipeline

The following diagram illustrates the complete local data flow and component pipeline when interacting with Otto:

```mermaid
graph TD
    A[Microphone Input] -->|Audio Stream| B(openWakeWord)
    B -->|Trigger: 'Hey Otto'| C(Speech Recording)
    C -->|WAV File| D(whisper.cpp STT)
    D -->|Transcribed Text| E(llama.cpp Local Server)
    E -->|JSON Response| F(Piper TTS)
    F -->|Synthesized Audio| G[Speaker Output]

    style A fill:#e1bee7,stroke:#333,stroke-width:2px
    style G fill:#c8e6c9,stroke:#333,stroke-width:2px
    style E fill:#bbdefb,stroke:#333,stroke-width:2px
