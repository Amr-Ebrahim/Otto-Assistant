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


🚀 Features
Custom Wake Word Detection: Powered locally by openWakeWord.

Offline Speech-to-Text: Fast, lightweight local transcription via whisper.cpp.

Local Language Model Server: Communicates with a local server instance using llama.cpp supporting both English and Arabic conversational inference.

Natural Offline Text-to-Speech: Synthesizes voice output using Piper TTS.

Bilingual Capabilities: Automatically detects language input and routes responses accordingly.

🛠️ Project Structure
Plaintext
otto-assistant/
│
├── audio/               # Runtime generated audio clips (ignored by git)
├── models/              # Local models & binaries directory (see download links below)
├── .gitignore           # Git ignore rules for virtual environments and binaries
├── requirements.txt     # Python package dependencies
├── otto_assistant.py    # Main control script and event loop
└── README.md            # Project documentation
📥 Setup, Installation & Dependencies
Because large model binaries and executables exceed GitHub's file storage limits, you will need to set up the runtime dependencies and models locally:

1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/Otto-Assistant.git](https://github.com/YOUR_USERNAME/Otto-Assistant.git)
cd Otto-Assistant
2. Install Python Dependencies
Make sure you have Python installed, then install the required Python packages:

Bash
pip install -r requirements.txt
3. Download Required Binaries & Models
To run this project, download and place the necessary components inside a local models/ directory:

Speech-to-Text (whisper.cpp):

Download the compiled CLI executable (whisper-cli.exe) and model weights (e.g., ggml-large-v3.bin) from the whisper.cpp releases page.

Text-to-Speech (Piper):

Download the Windows binary and voice models (en_US-amy-medium.onnx and ar_JO-kareem-medium.onnx) from the Piper TTS repository.

Local LLM Server (llama.cpp):

Download and run a local server binary from llama.cpp releases to serve your preferred open-source model (such as Qwen2.5 or Llama) on port 8080.

▶️ Running the Assistant
Ensure your local llama.cpp server is active and running on http://localhost:8080.

Run the main script from your terminal:

Bash
python otto_assistant.py
Say "Hey Otto" into your microphone to begin interacting!

📄 License
This project is open-source and available under the MIT License.


---

Once you paste this in and commit it, your GitHub repo will look exceptional—complete with a clear visual text diagram of your hardware/software pipeline and helpful external links for anyone looking to understand or run your work!
