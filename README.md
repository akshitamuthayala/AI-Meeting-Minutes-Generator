# 🧠 AI Meeting Minutes Generator

A powerful, AI-driven web app that converts raw meeting transcripts — from text, files, or even audio — into **structured, professional-grade minutes**. Built with LLaMA3 via Groq, Streamlit, and Whisper.

---

## 🚀 Features

### 📝 Intelligent Meeting Summarization
- Extracts **Date & Time**, **Attendees**, **Key Topics**, **Action Items**, and **Decisions** from your meeting.
- Clean, bullet-pointed output optimized for sharing or documentation.

### 🎙️ Audio & Video Transcription (NEW)
- Upload `.mp3` or `.mp4` files — the app automatically transcribes using **Whisper (Groq)**.
- Handles both **audio** and **video** inputs.
- Temporary files are auto-deleted for privacy and performance.

### 📂 File Upload Support
- Supports `.pdf` and `.docx` transcripts.
- Extracts full text using PyPDF2 and python-docx.

### 💻 Paste Mode
- Paste any raw transcript directly into the app for quick summaries.

### 📤 Export Options
- Download your generated minutes as:
  - ✅ `.txt`
  - ✅ `.md`
  - ✅ `.pdf` (via ReportLab)
  - ✅ `.docx`

### 🌐 Clean, Responsive UI
- Dark-themed layout with a custom header, sidebar, and navbar.
- Smooth scroll & fade-in animations.
- Fully responsive on desktop and tablets.

---

## 🛠️ Tech Stack

| Tech            | Purpose                            |
|-----------------|------------------------------------|
| **Streamlit**   | Web interface                      |
| **Groq + LLaMA3** | Large language model for minutes |
| **Whisper API** | Audio/video transcription          |
| **ReportLab**   | Custom PDF generation              |
| **PyPDF2 / docx** | File parsing                     |
| **uuid / tempfile** | Secure audio handling         |

---

## 🛡️ Security & Privacy
- No data is stored or logged.
- Audio files are processed locally and removed after transcription.
- API keys are handled securely via environment variables.