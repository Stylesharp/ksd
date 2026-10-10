import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Load environment variables (.env) if present
load_dotenv()

st.set_page_config(
    page_title="ElevenLabs Studio | AI Voice Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero header */
    .hero-container {
        padding: 1.6rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
        border-radius: 18px;
        border: 1px solid rgba(168, 85, 247, 0.25);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
    }
    
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .hero-subtitle {
        color: #64748B;
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
    }

    /* Badge styles */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.3rem;
    }
    .badge-primary {
        background-color: rgba(99, 102, 241, 0.12);
        color: #4F46E5;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.12);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.12);
        color: #475569;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    /* Generation Result Card */
    .result-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.2rem;
        margin-top: 1rem;
    }

    /* Button hover enhancement */
    button[kind="primary"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "text_input_area" not in st.session_state:
    st.session_state.text_input_area = ""

# Sample Presets for Quick Testing
SAMPLE_PRESETS = {
    "Select a preset...": "",
    "🎙️ Podcast Intro": "Welcome back to the Future Sound Podcast! Today, we are exploring cutting-edge breakthroughs in generative artificial intelligence and voice synthesis.",
    "🚀 Tech Product Launch": "Introducing Nova OS: an intelligent, hyper-fast operating system designed to elevate every interaction and supercharge your everyday workflow.",
    "📖 Audiobook Storyteller": "The ancient lantern flickered against the damp stone walls. Outside, the rain drummed relentlessly, whispering forgotten tales into the night.",
    "🧘 Guided Meditation": "Take a deep breath in... and exhale slowly. Let your shoulders drop, release all tension, and gently bring your awareness into the present moment.",
    "⚡ Motivational Coach": "Greatness isn't born from comfort zones. Every obstacle in front of you is simply another stepping stone waiting to be conquered. Let's make it happen!"
}

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    
    # 1. API Key Setup (supports secrets.toml, .env, or manual input)
    default_key = ""
    try:
        if "ELEVENLABS_API_KEY" in st.secrets:
            default_key = st.secrets["ELEVENLABS_API_KEY"]
    except Exception:
        pass

    if not default_key:
        default_key = os.getenv("ELEVENLABS_API_KEY", "")

    api_key_input = st.text_input(
        "ElevenLabs API Key",
        value=default_key,
        type="password",
        placeholder="sk_...",
        help="Get your key at elevenlabs.io/app/settings/api-keys. You can also store it in .streamlit/secrets.toml or a .env file."
    )
    api_key = api_key_input.strip()

    st.markdown("---")

    # Client Initialization
    client = None
    voices_dict = {}
    voices_list = []
    
    if api_key:
        try:
            client = ElevenLabs(api_key=api_key)
            with st.spinner("Connecting to ElevenLabs..."):
                resp = client.voices.get_all()
                voices_list = resp.voices
                voices_dict = {v.name: v for v in voices_list}
            st.success("Connected to ElevenLabs", icon="🟢")
        except Exception as e:
            st.error(f"Authentication error: {e}")
            client = None
    else:
        st.info("💡 Enter your API key above or in `.env` to load voices.", icon="🔑")

    # 2. Voice & Model Selection
    st.markdown("#### 🗣️ Voice Selection")
    if voices_dict:
        voice_names = list(voices_dict.keys())
        selected_voice_name = st.selectbox("Choose Voice", options=voice_names)
        selected_voice = voices_dict[selected_voice_name]
        selected_voice_id = selected_voice.voice_id
        
        # Display Voice Metadata Card
        with st.container(border=True):
            st.caption("VOICE DETAILS")
            st.markdown(f"**{selected_voice.name}**")
            
            # Badges
            labels = selected_voice.labels or {}
            badges_html = ""
            if selected_voice.category:
                badges_html += f"<span class='badge badge-primary'>{selected_voice.category.title()}</span>"
            for k, val in labels.items():
                badges_html += f"<span class='badge badge-neutral'>{val.title()}</span>"
            if badges_html:
                st.markdown(badges_html, unsafe_allow_html=True)
            
            if selected_voice.description:
                st.caption(f"_{selected_voice.description}_")
                
            # Quick Preview Player if available
            if selected_voice.preview_url:
                st.markdown("🔊 **Sample Audio Preview:**")
                st.audio(selected_voice.preview_url, format="audio/mp3")
    else:
        selected_voice_name = None
        selected_voice_id = None
        st.caption("Voices will appear here once authenticated.")

    st.markdown("#### 🧠 Model Selection")
    model_id = st.selectbox(
        "ElevenLabs Model",
        options=[
            "eleven_multilingual_v2",
            "eleven_turbo_v2_5",
            "eleven_turbo_v2",
            "eleven_monolingual_v1"
        ],
        index=0,
        help="Multilingual v2 is best for natural emotion across 29 languages. Turbo v2.5 offers the lowest latency."
    )

    # 3. Fine-tuning Voice Settings
    with st.expander("🎛️ Advanced Voice Tuning", expanded=False):
        stability = st.slider(
            "Stability",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Higher values make voice more consistent; lower values make it more expressive and variable."
        )
        similarity = st.slider(
            "Clarity / Similarity Boost",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Enhances resemblance to original voice and improves audio clarity."
        )
        style = st.slider(
            "Style Exaggeration",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            help="Amplifies speaking style/attitude (recommended: 0.0 for natural dialogue)."
        )
        speed = st.slider(
            "Speaking Speed",
            min_value=0.7,
            max_value=1.5,
            value=1.0,
            step=0.05,
            help="Controls narration tempo. 1.0 is default speech speed."
        )
        speaker_boost = st.checkbox("Speaker Boost", value=True, help="Boosts similarity to the original speaker.")

    st.markdown("---")
    st.caption("Crafted with Streamlit & ElevenLabs SDK")


# --- Main Application Area ---

# Header Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎙️ AI Voice Synthesis Studio</div>
    <div class="hero-subtitle">Transform text and documents into lifelike, emotional, studio-grade speech with ElevenLabs.</div>
</div>
""", unsafe_allow_html=True)

# Main Grid: Left side for inputs, Right side for quick metrics & generation details
col_main, col_stats = st.columns([2.3, 1], gap="medium")

with col_main:
    # Input Tabs
    input_tab1, input_tab2, input_tab3 = st.tabs([
        "✍️ Write / Paste Text", 
        "📄 Upload Document", 
        "💡 Prompt Presets"
    ])
    
    text_to_speak = ""

    # Tab 1: Direct text input
    with input_tab1:
        text_entered = st.text_area(
            "Enter your script:",
            value=st.session_state.text_input_area,
            height=220,
            placeholder="Type, write, or paste the text you want converted to speech...",
            key="direct_text_box"
        )
        if text_entered:
            text_to_speak = text_entered

    # Tab 2: Document upload
    with input_tab2:
        st.markdown("##### Upload a text or markdown file")
        uploaded_doc = st.file_uploader(
            "Upload file (.txt, .md)", 
            type=["txt", "md"], 
            help="The text will be automatically extracted and prepared for speech synthesis."
        )
        if uploaded_doc is not None:
            try:
                extracted_content = uploaded_doc.read().decode("utf-8")
                st.success(f"Loaded '{uploaded_doc.name}' ({len(extracted_content)} characters)", icon="✅")
                text_to_speak = extracted_content
                st.text_area("File Preview", value=extracted_content, height=180, disabled=True)
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # Tab 3: Preset Library
    with input_tab3:
        st.markdown("##### Quick Start Presets")
        preset_choice = st.selectbox("Choose a sample script to try:", options=list(SAMPLE_PRESETS.keys()))
        if preset_choice and SAMPLE_PRESETS[preset_choice]:
            st.info(f"**Preview:**\n\n_{SAMPLE_PRESETS[preset_choice]}_")
            if st.button("Use This Preset", use_container_width=True):
                st.session_state.text_input_area = SAMPLE_PRESETS[preset_choice]
                st.rerun()

# Real-time text metrics
char_count = len(text_to_speak)
word_count = len(text_to_speak.split()) if text_to_speak.strip() else 0
# Average speaking rate ~150 words per minute (2.5 words/sec)
est_duration_sec = round(word_count / 2.5) if word_count > 0 else 0

with col_stats:
    with st.container(border=True):
        st.markdown("#### 📊 Script Metrics")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Characters", f"{char_count:,}")
            st.metric("Words", f"{word_count:,}")
        with m_col2:
            st.metric("Est. Time", f"~{est_duration_sec}s")
            st.metric("Voices", len(voices_list) if voices_list else "0")

        st.markdown("---")
        st.markdown("#### 🎯 Active Voice")
        if selected_voice_name:
            st.markdown(f"**Voice:** `{selected_voice_name}`")
            st.markdown(f"**Model:** `{model_id}`")
            st.markdown(f"**Speed:** `{speed}x`")
        else:
            st.caption("No voice selected")

st.markdown("")

# --- Generation Trigger Bar ---
action_col1, action_col2, action_col3 = st.columns([1, 2, 1])
with action_col2:
    generate_btn = st.button(
        "✨ Generate Studio Speech", 
        type="primary", 
        use_container_width=True,
        disabled=(client is None or not selected_voice_id)
    )

if generate_btn:
    if not text_to_speak.strip():
        st.warning("⚠️ Please provide some text in the editor or upload a document first.", icon="✏️")
    elif client is None:
        st.error("⚠️ Please configure a valid ElevenLabs API Key in the sidebar.", icon="🔒")
    else:
        with st.status("🎙️ Synthesizing voice...", expanded=True) as status_box:
            st.write("Initializing voice parameters and tuning...")
            time.sleep(0.2)
            st.write(f"Connecting to model `{model_id}` using voice **{selected_voice_name}**...")
            
            try:
                # Custom voice settings object
                custom_settings = VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity,
                    style=style,
                    speed=speed,
                    use_speaker_boost=speaker_boost
                )

                # Call the official ElevenLabs text_to_speech convert method
                audio_stream = client.text_to_speech.convert(
                    voice_id=selected_voice_id,
                    text=text_to_speak,
                    model_id=model_id,
                    voice_settings=custom_settings
                )
                
                audio_bytes = b"".join(audio_stream)
                
                status_box.update(label="Speech generated successfully!", state="complete", expanded=False)
                
                # Save into Session History
                generation_record = {
                    "id": f"gen_{int(time.time())}",
                    "timestamp": datetime.now().strftime("%I:%M %p - %b %d"),
                    "voice_name": selected_voice_name,
                    "model": model_id,
                    "text_snippet": (text_to_speak[:90] + "...") if len(text_to_speak) > 90 else text_to_speak,
                    "audio_bytes": audio_bytes,
                    "words": word_count
                }
                st.session_state.history.insert(0, generation_record)
                
            except Exception as e:
                status_box.update(label="Generation failed", state="error", expanded=True)
                st.error(f"Failed to generate speech: {e}")

# --- Output & Playback Section ---
if st.session_state.history:
    latest = st.session_state.history[0]
    
    st.markdown("### 🎧 Latest Generation")
    with st.container(border=True):
        res_col1, res_col2 = st.columns([2.5, 1], gap="medium")
        
        with res_col1:
            st.markdown(f"**Voice:** `{latest['voice_name']}` • **Model:** `{latest['model']}` • **Words:** `{latest['words']}`")
            st.caption(f"Script: \"{latest['text_snippet']}\"")
            st.audio(latest["audio_bytes"], format="audio/mp3")
            
        with res_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            custom_filename = f"tts_{latest['voice_name'].lower().replace(' ', '_')}_{int(time.time())}.mp3"
            st.download_button(
                label="⬇️ Download MP3",
                data=latest["audio_bytes"],
                file_name=custom_filename,
                mime="audio/mp3",
                use_container_width=True,
                type="secondary"
            )

# --- Generation History Drawer ---
if len(st.session_state.history) > 1:
    with st.expander(f"📚 Session History ({len(st.session_state.history)} generations)", expanded=False):
        top_h_col1, top_h_col2 = st.columns([3, 1])
        with top_h_col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()
                
        for idx, item in enumerate(st.session_state.history[1:], start=2):
            with st.container(border=True):
                hcol1, hcol2 = st.columns([3, 1])
                with hcol1:
                    st.markdown(f"**#{idx} | {item['voice_name']}** (`{item['model']}`) • <small style='color:gray;'>{item['timestamp']}</small>", unsafe_allow_html=True)
                    st.caption(f"\"{item['text_snippet']}\"")
                    st.audio(item["audio_bytes"], format="audio/mp3")
                with hcol2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️ Download",
                        data=item["audio_bytes"],
                        file_name=f"audio_{idx}.mp3",
                        mime="audio/mp3",
                        key=f"dl_history_{item['id']}",
                        use_container_width=True
                    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 1rem 0;'>"
    "ElevenLabs TTS Studio • Powered by ElevenLabs Voice AI & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
