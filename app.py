import streamlit as st
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
import PyPDF2
import docx
from io import BytesIO
from docx import Document
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from moviepy.editor import VideoFileClip
import tempfile
import uuid


st.set_page_config(page_title="AI Meeting Minutes Generator", layout="centered")

def apply_custom_css():
    st.markdown("""
        <style>
            html {
                scroll-behavior: smooth;
            }
            .stApp {
                background-color: #1C1C1E;
                color: #FFFFFF;
            }
            .navbar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 60px;
                background: linear-gradient(to right, #7b2cbf, #9d4edd);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .navbar .brand {
                color: transparent;
                font-size: 0px;
            }
            .navbar a {
                display: none;
            }
            .main-content {
                padding-top: 80px;
            }
            .gradient-header-box {
                background-color: #7b2cbf;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }
            .gradient-header-box h1 {
                color: white;
                font-size: 2.5em;
                font-weight: bold;
                margin: 0;
            }
            .back-to-top {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #7b2cbf;
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                z-index: 9999;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }
            .section-spacer {
                margin-top: 100px;
            }
            a[href^="#"] {
                color: #d3b6f5;
                text-decoration: none;
                font-weight: bold;
            }
            a[href^="#"]:hover {
                color: #f0d9ff;
                text-decoration: underline;
            }
            .info-section {
                background-color: #2A2A2E;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
            }
            .info-section h3 {
                color: #d3b6f5;
                font-size: 1.8em;
                margin-bottom: 10px;
            }
            .info-section p {
                font-size: 1.1em;
                line-height: 1.6;
            }
        </style>
        <a href="#ai-home" class="back-to-top">↑ Top</a>
    """, unsafe_allow_html=True)

apply_custom_css()

st.markdown("""
    <div class="navbar">
        <div class="brand">🧠</div>
        <div></div>
    </div>
    <div class="main-content">
""", unsafe_allow_html=True)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please check your .env file.")
    st.stop()

def initialize_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama3-8b-8192",
        temperature=0.3
    )

def create_chain(llm):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that writes professional meeting minutes."),
        ("human",
         "Here is the meeting transcript:\n\n{transcript}\n\n"
         "Generate professional meeting minutes with the following clearly formatted markdown sections.\n\n"
         "🗓️ Date & Time\n👥 Attendee List\n💬 Key Topics Discussed\n📝 Summary\n✅ Action Items\n📅 Deadlines and Decisions\n📌 Next Steps\n\n"
         "- Use `-` for bullet points.\n"
         "- Format action items like `Name: Task`.\n"
         "- Each section must start on a new line.\n"
         "_This summary is for reference purposes only._")
    ])
    return {"transcript": RunnablePassthrough()} | prompt | llm | StrOutputParser()

def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(uploaded_file):
    try:
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception:
        return ""

def generate_pdf_with_reportlab(text):
    from markdown2 import markdown
    import html

    buffer = BytesIO()
    font_dir = r"C:\\Users\\akshi\\OneDrive\\Desktop\\AI meeting minutes generator\\fonts\\ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(font_dir, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(font_dir, "DejaVuSans-Bold.ttf")))

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Custom', fontName='DejaVuSans', fontSize=11, leading=16))
    styles.add(ParagraphStyle(name='Heading', fontName='DejaVuSans-Bold', fontSize=18, leading=24, spaceAfter=14, spaceBefore=14))

    headings = ["Date & Time", "Attendee List", "Key Topics Discussed", "Summary", "Action Items", "Deadlines and Decisions", "Next Steps"]

    def remove_emojis(t):
        return re.sub(r"[\U00010000-\U0010ffff]", "", t)

    text = remove_emojis(text)
    elements = []
    for line in text.split("\n"):
        if not line.strip():
            elements.append(Spacer(1, 12))
        elif any(h in line for h in headings):
            clean_heading = re.sub(r'[^\w\s&]', '', line)
            elements.append(Paragraph(html.escape(clean_heading), styles["Heading"]))
        else:
            html_line = markdown(line).strip().replace("<p>", "").replace("</p>", "")
            elements.append(Paragraph(html_line, styles["Custom"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def transcribe_audio_with_whisper(audio_file):
    import requests

    whisper_url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": (audio_file.name, audio_file.read(), "application/octet-stream"),
        "model": (None, "whisper-large-v3")
    }

    response = requests.post(whisper_url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        st.error(f"Failed to transcribe audio. Status code: {response.status_code}")
        return ""


def convert_video_to_audio(video_path, audio_path="temp_audio.mp3"):
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path)
    return audio_path

def main():
    st.markdown("""
    <div class="gradient-header-box" id="ai-home">
        <h1>AI Meeting Minutes Generator</h1>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Settings & Info")
        st.markdown("📌 Paste a transcript or upload a file to begin.")
        st.markdown("🔒 Your data is processed locally and securely.")
        st.markdown("---")
        st.markdown("🔗 Quick Links")
        st.markdown('<a href="#ai-about">📖 About</a>', unsafe_allow_html=True)
        st.markdown('<a href="#ai-contact">📬 Contact</a>', unsafe_allow_html=True)

    with st.expander("📄 Step 1: Provide Meeting Transcript"):
        input_method = st.radio("Choose input method", ["Paste Transcript", "Upload File", "Upload Audio"])
        transcript = ""

        if input_method == "Paste Transcript":
            transcript = st.text_area("Paste your meeting transcript below", height=300)
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
            if uploaded_file:
                file_type = uploaded_file.name.split(".")[-1].lower()
                if file_type == "pdf":
                    transcript = extract_text_from_pdf(uploaded_file)
                elif file_type == "docx":
                    transcript = extract_text_from_docx(uploaded_file)
        elif input_method == "Upload Audio":
            uploaded_file = st.file_uploader("Upload an audio or video file (MP3 or MP4)", type=["mp3", "mp4"])
            if uploaded_file:
                unique_id = str(uuid.uuid4())
                temp_dir = tempfile.gettempdir()
                progress = st.progress(0, text="Starting processing...")

                if uploaded_file.type == "video/mp4":
                    video_path = os.path.join(temp_dir, f"video_{unique_id}.mp4")
                    audio_path = os.path.join(temp_dir, f"audio_{unique_id}.mp3")
                    try:
                        progress.progress(10, text="Saving uploaded video...")
                        with open(video_path, "wb") as f:
                            f.write(uploaded_file.read())

                        progress.progress(30, text="Converting video to audio...")
                        convert_video_to_audio(video_path, audio_path)

                        progress.progress(60, text="Transcribing audio with Whisper...")
                        with open(audio_path, "rb") as audio_file:
                            transcript = transcribe_audio_with_whisper(audio_file)

                        progress.progress(100, text="✅ Finished processing!")
                    finally:
                        for path in [video_path, audio_path]:
                            try:
                                if os.path.exists(path):
                                    os.remove(path)
                            except Exception as e:
                                st.warning(f"Could not delete temp file: {path}")
                elif uploaded_file.type == "audio/mp3":
                    audio_path = os.path.join(temp_dir, f"audio_{unique_id}.mp3")
                    try:
                        progress.progress(10, text="Saving uploaded audio...")
                        with open(audio_path, "wb") as f:
                            f.write(uploaded_file.read())

                        progress.progress(50, text="Transcribing audio with Whisper...")
                        with open(audio_path, "rb") as audio_file:
                            transcript = transcribe_audio_with_whisper(audio_file)

                        progress.progress(100, text="✅ Finished processing!")
                    finally:
                        try:
                            if os.path.exists(audio_path):
                                os.remove(audio_path)
                        except Exception as e:
                            st.warning(f"Could not delete temp file: {audio_path}")



    if st.button("🚀 Generate Meeting Minutes"):
        if not transcript.strip():
            st.warning("Please provide or upload a transcript.")
            return

        with st.spinner("Generating professional minutes..."):
            llm = initialize_llm()
            chain = create_chain(llm)
            result = chain.invoke(transcript)

        st.success("✅ Meeting minutes generated!")
        st.subheader("📗 Generated Meeting Minutes")
        st.markdown(result)

        st.subheader("📥 Export Options")
        st.download_button("💾 Download as .txt", result, "meeting_minutes.txt", "text/plain")
        st.download_button("💾 Download as .md", result, "meeting_minutes.md", "text/markdown")
        st.download_button("💾 Download as .pdf", generate_pdf_with_reportlab(result), "meeting_minutes.pdf", "application/pdf")
        st.download_button("💾 Download as .docx", generate_docx(result), "meeting_minutes.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.markdown("""<div class="section-spacer"></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-section" id="ai-about">
        <h3>📖 About</h3>
        <p>
            This AI Meeting Minutes Generator transforms raw meeting transcripts into structured, professional minutes. 
            It identifies attendees, key topics, summaries, action items, and decisions – saving time and increasing productivity.
        </p>
    </div>

    <div class="info-section" id="ai-contact">
        <h3>📬 Contact</h3>
        <p>
            Questions or feedback? Reach out at 
            <a href="mailto:ai@minutes.com" style="color:#d3b6f5;">ai@minutes.com</a> 
            and we’ll be happy to help!
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
