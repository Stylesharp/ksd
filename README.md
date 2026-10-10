# 🎙️ ElevenLabs AI Voice Synthesis Studio

A modern, full-featured [Streamlit](https://streamlit.io/) application that turns text and documents into studio-grade speech using the [ElevenLabs API](https://elevenlabs.io/).

---

## ✨ Features

- **🎨 Modern Glassmorphic UI:** Clean, responsive design with gradient styling, metadata badges, and smooth feedback.
- **🔊 Instant Voice Auditions:** Listen to voice sample previews directly before synthesizing speech.
- **🎛️ Fine-Tuned Voice Controls:** Custom sliders for Stability, Clarity/Similarity, Style Exaggeration, and Speaking Speed.
- **✍️ Multi-Mode Input:**
  - **Direct Editor:** Real-time character counter, word counter, and estimated audio playback duration.
  - **Document Uploader:** Drag-and-drop `.txt` or `.md` files.
  - **Quick Start Presets:** 1-click sample templates (Podcast Intro, Audiobook Story, Product Launch, Guided Meditation, Motivational Coach).
- **📚 Session History:** Automatically preserves previous takes and generations so you can compare voices and download any take.
- **⚡ .env & Secret Support:** Automatically detects `ELEVENLABS_API_KEY` from your environment or `.env` file.

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set up virtual environment (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure API Key via `.env`
Copy `.env.example` to `.env` and paste your ElevenLabs API Key:
```bash
cp .env.example .env
```
*(You can also simply paste your API key in the sidebar of the web app).*

### 5. Launch the Studio
```bash
python -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/)
- [ElevenLabs Python SDK v2](https://github.com/elevenlabs/elevenlabs-python)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📄 License
[MIT](LICENSE)
