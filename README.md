# 🤖 Otto Offline Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An advanced, fully offline, privacy-first voice assistant built for Windows. Otto handles custom wake-word detection, local speech transcription, local LLM generation (supporting English and Arabic), and neural text-to-speech synthesis without relying on any cloud APIs.

</div>

---

## 🏗️ System Architecture

The following diagram illustrates the complete local data flow and component pipeline when interacting with Otto:

```mermaid
graph TD
    A[Microphone Input] -->|Audio Stream| B(openWakeWord)
    B -->|Trigger: 'Hey Otto'| C(Speech Recording & Silence Detection)
    C -->|WAV File| D(whisper.cpp STT)
    D -->|Transcribed Text| E(llama.cpp Local Server)
    E -->|JSON Response| F(Piper TTS)
    F -->|Synthesized Audio| G[Speaker Output]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#9f9,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px

    ✨ Key Features
Local Wake-Word Engine: Uses openWakeWord for ultra-low-latency custom wake-word triggering ("Hey Otto").

Offline Speech-to-Text: Integrates high-performance whisper.cpp for fast local transcription.

Local LLM Backend: Connects to a local server instance via llama.cpp supporting intelligent bilingual (English/Arabic) inference.

Neural Text-to-Speech: Generates natural voice responses offline utilizing Piper TTS.

Absolute Privacy: Zero telemetry, zero external cloud requests—your voice stays entirely on your hardware.

📂 Project Structure
Plaintext
otto-assistant/
│
├── audio/               # Runtime audio buffer storage (ignored by git)
├── models/              # Local model weights & binaries (see setup instructions)
├── .gitignore           # Excludes virtual environments, caches, and large weights
├── requirements.txt     # Python dependencies list
├── otto_assistant.py    # Main control script & event loop
└── README.md            # Documentation

🚀 Setup & Installation Guide
Because large model binaries and weights exceed GitHub storage thresholds, follow these steps to configure your local runtime environment:

1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/Otto-Assistant.git](https://github.com/YOUR_USERNAME/Otto-Assistant.git)
cd Otto-Assistant
2. Set Up Python Environment
Install the necessary package dependencies:

Bash
pip install -r requirements.txt
3. Download Required Binaries & Models
Create a local models/ folder and populate it with the required open-source engines:

whisper.cpp: Download the CLI executable (whisper-cli.exe) and your preferred model weights (e.g., ggml-large-v3.bin).

Piper TTS: Download the Windows binary and voice files (en_US-amy-medium.onnx and ar_JO-kareem-medium.onnx).

llama.cpp: Set up a local server instance serving your preferred open-source model (like Qwen2.5) on port 8080.

🎮 Usage
Ensure your local llama.cpp server is active at http://localhost:8080.

Run the main control script:

Bash
python otto_assistant.py
Speak "Hey Otto" to your microphone and begin your conversation!

📄 License
Distributed under the MIT License. Feel free to fork, modify, and build upon it!


---

Once you commit this version, GitHub will automatically compile the architecture section into a clean, modern vector flowchart graphic instead of plain text, and the badges at the top will give it an official open-source look! Let me know how it looks on your page.
