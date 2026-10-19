# Installation Guide

This guide sets up Otto on **Windows 10/11** from scratch: Python, the wake-word model, Whisper, the local LLM server and the text-to-speech voices.

Model files are large, so they are **not stored in this repository** — you download them once, and after that Otto runs fully offline.

**Contents**

1. [Requirements](#1-requirements)
2. [Get the code](#2-get-the-code)
3. [Install Python dependencies](#3-install-python-dependencies)
4. [Wake word (openWakeWord)](#4-wake-word-openwakeword)
5. [Speech-to-text (whisper.cpp)](#5-speech-to-text-whispercpp)
6. [Local LLM (llama.cpp + Qwen2.5)](#6-local-llm-llamacpp--qwen25)
7. [Choose your microphone](#7-choose-your-microphone)
8. [Text-to-speech (Piper)](#8-text-to-speech-piper)
9. [Optional: Egyptian Arabic voice with VoiceTut-TTS](#9-optional-egyptian-arabic-voice-with-voicetut-tts)
10. [Run Otto](#10-run-otto)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Requirements

| | Minimum | Recommended |
| :-- | :-- | :-- |
| OS | Windows 10 / 11 (64-bit) | — |
| Python | 3.10 | 3.10 or 3.11 |
| RAM | 16 GB | 16 GB+ |
| GPU | not required | NVIDIA GPU with recent drivers |
| Disk | ~10 GB free | — |
| Audio | a microphone and speakers | — |

You also need [Git](https://git-scm.com/download/win).

> **Why Windows only?** Otto plays audio with Python's built-in `winsound` module and calls the Windows `.exe` builds of whisper.cpp and Piper.

## 2. Get the code

The script looks for its files in `C:\otto-assistant` (the `PROJECT_DIR` setting), so clone it there:

```powershell
git clone https://github.com/Amr-Ebrahim/Otto-Assistant.git C:\otto-assistant
cd C:\otto-assistant
```

Want a different folder? Change `PROJECT_DIR` at the top of `otto_assistant.py`.

Then create the model folders:

```powershell
mkdir models\wake, models\whisper, models\llm, models\tts, llama.cpp
```

## 3. Install Python dependencies

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

This installs `pyaudio`, `numpy`, `scipy` and `openwakeword`.

## 4. Wake word (openWakeWord)

**4.1 — Download openWakeWord's built-in feature models** (needed by every wake-word model):

```powershell
python -c "import openwakeword.utils as u; u.download_models()"
```

**4.2 — Add the "Hey Otto" model.** Otto uses a custom wake-word model named `hey_otto.onnx`. Download it from the [Releases page](https://github.com/Amr-Ebrahim/Otto-Assistant/releases) and save it as:

```text
C:\otto-assistant\models\wake\hey_otto.onnx
```

> **Want your own wake word?** Train one with openWakeWord's [training notebook](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing), export it as `.onnx`, and save it in `models\wake\`. If you give it a different name, update `WAKE_MODEL` and the `"hey_otto"` key in `wait_for_wake_word()` — openWakeWord names each score after the model file.

## 5. Speech-to-text (whisper.cpp)

**5.1 — Download the Windows binaries.** From the [whisper.cpp releases](https://github.com/ggml-org/whisper.cpp/releases), pick a release that includes Windows builds (for example **v1.7.6**; some newer releases only ship source code) and download:

| Your hardware | File |
| :-- | :-- |
| NVIDIA GPU | `whisper-cublas-12.4.0-bin-x64.zip` |
| CPU only | `whisper-bin-x64.zip` |

Extract it into `models\whisper\`. You should end up with:

```text
C:\otto-assistant\models\whisper\Release\whisper-cli.exe
```

**5.2 — Download the Whisper model.** Download [`ggml-large-v3.bin`](https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-large-v3.bin) (3.1 GB) from Hugging Face into `models\whisper\`:

```text
C:\otto-assistant\models\whisper\ggml-large-v3.bin
```

> **Slower PC?** `ggml-large-v3-turbo.bin` (1.6 GB) or `ggml-large-v3-turbo-q5_0.bin` (574 MB) from the same page are much faster. Save it and change `WHISPER_MODEL` in the script to the new filename.

**5.3 — Test it:**

```powershell
models\whisper\Release\whisper-cli.exe -m models\whisper\ggml-large-v3.bin -f path\to\any.wav -l auto
```

## 6. Local LLM (llama.cpp + Qwen2.5)

Otto talks to the LLM through `llama-server`, which exposes an OpenAI-compatible API at `http://localhost:8080`.

**6.1 — Download llama.cpp.** From the [llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases), download the Windows build that matches your hardware (file names include the build number):

| Your hardware | Files to download |
| :-- | :-- |
| NVIDIA GPU | `llama-<build>-bin-win-cuda-12.4-x64.zip` **and** `cudart-llama-bin-win-cuda-12.4-x64.zip` |
| AMD / Intel GPU | `llama-<build>-bin-win-vulkan-x64.zip` |
| CPU only | `llama-<build>-bin-win-cpu-x64.zip` |

Extract everything into `C:\otto-assistant\llama.cpp\` so that `llama-server.exe` is directly inside that folder. (For CUDA, extract both zips into the same folder.)

**6.2 — Download Qwen2.5-7B-Instruct.** Otto uses the **Q4_K_M** quantization (≈4.7 GB), a good balance of quality and speed.

Option A — let llama-server download it automatically (needs internet the first time only; the model is cached afterwards):

```powershell
llama.cpp\llama-server.exe -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -ngl 99
```

Option B — download the file yourself into `models\llm\`:

```powershell
pip install -U huggingface_hub
hf download Qwen/Qwen2.5-7B-Instruct-GGUF --include "qwen2.5-7b-instruct-q4_k_m*.gguf" --local-dir models\llm
```

(On older versions of `huggingface_hub`, use `huggingface-cli download` instead of `hf download`.)

If the download arrives in several parts (`...-00001-of-00002.gguf`), merge them into one file:

```powershell
llama.cpp\llama-gguf-split.exe --merge models\llm\qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf models\llm\qwen2.5-7b-instruct-q4_k_m.gguf
```

**6.3 — Start the server** (keep this terminal open while Otto runs):

```powershell
llama.cpp\llama-server.exe -m models\llm\qwen2.5-7b-instruct-q4_k_m.gguf --port 8080 -ngl 99 -c 4096
```

| Flag | Meaning |
| :-- | :-- |
| `-m` | path to the GGUF model |
| `--port 8080` | must match `LLAMA_SERVER_URL` in the script |
| `-ngl 99` | put all model layers on the GPU (use `0` on CPU-only machines, or a smaller number if you run out of VRAM) |
| `-c 4096` | context size in tokens |

**6.4 — Test the server** from a second terminal:

```powershell
curl.exe http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":20}"
```

You should get a JSON reply with Qwen's answer. You can also open `http://localhost:8080` in a browser to chat with the model directly.

> **Low on memory?** Use [Qwen2.5-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) instead — same steps, roughly half the size.

## 7. Choose your microphone

List your input devices and their sample rates:

```powershell
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name'], int(p.get_device_info_by_index(i)['defaultSampleRate'])) for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]"
```

Example output:

```text
1 Microphone (Realtek Audio) 44100
3 Headset Microphone (USB) 48000
```

Open `otto_assistant.py` and set:

```python
MIC_DEVICE_INDEX = 1       # the number in the first column
MIC_NATIVE_RATE = 44100    # the number in the last column
```

## 8. Text-to-speech (Piper)

**8.1 — Download Piper for Windows.** From Piper's [2023.11.14-2 release](https://github.com/rhasspy/piper/releases/tag/2023.11.14-2), download `piper_windows_amd64.zip` and extract it into `models\tts\`. You should get:

```text
C:\otto-assistant\models\tts\piper\piper.exe
```

**8.2 — Download the voices.** Each voice needs **both** the `.onnx` file and its `.onnx.json` config. Save all four files in `models\tts\`:

| Voice | Files |
| :-- | :-- |
| English — Amy | [`en_US-amy-medium.onnx`](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/amy/medium/en_US-amy-medium.onnx) + [`.onnx.json`](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json) |
| Arabic — Kareem | [`ar_JO-kareem-medium.onnx`](https://huggingface.co/rhasspy/piper-voices/blob/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx) + [`.onnx.json`](https://huggingface.co/rhasspy/piper-voices/blob/main/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json) |

**8.3 — Test it:**

```powershell
echo Hello, I am Otto. | models\tts\piper\piper.exe --model models\tts\en_US-amy-medium.onnx --output_file test.wav
start test.wav
```

> Piper's original repository is now archived and development continues at [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl). The Windows `piper.exe` from the release above still works with Otto as-is.

## 9. Optional: Egyptian Arabic voice with VoiceTut-TTS

The Kareem voice speaks Modern Standard Arabic with a Jordanian accent. For natural **Egyptian Arabic**, Otto can use [VoiceTut-TTS](https://huggingface.co/mohammedaly22/VoiceTut-TTS) — an Apache-2.0 model fine-tuned on about 380 hours of Egyptian podcast speech, with Arabic–English code-switching and several built-in voices. It needs an NVIDIA GPU (about 3 GB of VRAM in float16, per the model card).

**9.1 — Install** (inside the same `venv`; pick the PyTorch build that matches your CUDA version from [pytorch.org](https://pytorch.org/get-started/locally/)):

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install git+https://github.com/k2-fsa/OmniVoice.git
pip install voicetut-tts
```

**9.2 — Test it and pick a voice.** The model downloads from Hugging Face the first time, then runs offline from the cache:

```powershell
voicetut --list-speakers
voicetut --text "ازيك عامل ايه النهاردة؟" --speaker Mohamed --output test_egy.wav
start test_egy.wav
```

**9.3 — Use it in Otto.** In `otto_assistant.py`, load the model once near the top of the file:

```python
from voicetut_tts import VoiceTutTTS

EGY_TTS = VoiceTutTTS.from_pretrained("mohammedaly22/VoiceTut-TTS")
EGY_SPEAKER = "Mohamed"   # any name from `voicetut --list-speakers`
```

Then replace the `try:` block inside `speak()` so Arabic replies use VoiceTut and English replies keep using Piper:

```python
    try:
        if is_arabic(text):
            EGY_TTS.synthesize(text, speaker=EGY_SPEAKER, output=RESPONSE_WAV)
        else:
            subprocess.run(
                [PIPER_EXECUTABLE, "--model", PIPER_MODEL_EN, "--output_file", RESPONSE_WAV],
                input=text.encode("utf-8"),
                check=True
            )
        winsound.PlaySound(RESPONSE_WAV, winsound.SND_FILENAME)
    except Exception as e:
        print("❌ TTS error:", e)
```

## 10. Run Otto

Your folder should now look like this:

```text
C:\otto-assistant\
├── otto_assistant.py
├── llama.cpp\llama-server.exe  (+ DLLs)
└── models\
    ├── wake\hey_otto.onnx
    ├── whisper\Release\whisper-cli.exe
    ├── whisper\ggml-large-v3.bin
    ├── llm\qwen2.5-7b-instruct-q4_k_m.gguf
    └── tts\
        ├── piper\piper.exe
        ├── en_US-amy-medium.onnx + .onnx.json
        └── ar_JO-kareem-medium.onnx + .onnx.json
```

1. **Terminal 1** — start the LLM server (step 6.3) and wait until it says the server is listening.
2. **Terminal 2** — run Otto:

   ```powershell
   cd C:\otto-assistant
   venv\Scripts\activate
   python otto_assistant.py
   ```

3. Say **"Hey Otto"**. Otto answers *"Yes, how can I help?"* — ask your question in Arabic or English.
4. Keep asking follow-up questions. After 8 seconds of silence, Otto goes back to waiting for the wake word.
5. Press **Ctrl + C** to stop.

## 11. Troubleshooting

| Problem | Fix |
| :-- | :-- |
| `Invalid sample rate` or the mic doesn't open | Set `MIC_DEVICE_INDEX` and `MIC_NATIVE_RATE` to the values from [step 7](#7-choose-your-microphone). |
| Otto wakes up on its own | Raise `WAKE_THRESHOLD` (try `0.3`–`0.5`). |
| Otto never hears "Hey Otto" | Lower `WAKE_THRESHOLD`, move closer to the mic, and check the right device is selected. |
| Otto stops recording too early / never stops | `SPEECH_THRESHOLD = 500` inside `record_speech()` is the loudness level that counts as speech — raise it in a noisy room, lower it for a quiet mic. |
| `❌ LLM error: ... connection refused` | `llama-server` isn't running, or it's on a different port than `LLAMA_SERVER_URL`. |
| `❌ Whisper error` / file not found | Check that `whisper-cli.exe` is in `models\whisper\Release\` and the model filename matches `WHISPER_MODEL`. |
| `❌ TTS error` | Make sure each voice's `.onnx.json` file sits next to its `.onnx` file. |
| Answers are slow | Use the CUDA builds, `-ngl 99`, a turbo Whisper model, or Qwen2.5-3B. Whisper reloads its model for every question, so a smaller Whisper model helps most. |
| Arabic text looks garbled in the console | Use Windows Terminal, which displays Arabic correctly. The script already outputs UTF-8. |
