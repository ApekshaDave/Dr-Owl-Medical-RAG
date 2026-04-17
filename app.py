import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import ollama
import os
import time
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime

# ── MODEL STRINGS ─────────────────────────────────────────────────────────────
# Ensure you have run `ollama pull llama3` and `ollama pull llava` in your terminal
OLLAMA_TEXT_MODEL = "llama3.2:1b"
OLLAMA_VISION_MODEL = "moondream"

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pulse — Medical AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. GLOBAL CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Sora:wght@600;700&display=swap');

:root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #1c2330;
    --border:    #30363d;
    --accent:    #3b82f6;
    --accent2:   #06b6d4;
    --green:     #10b981;
    --amber:     #f59e0b;
    --red:       #ef4444;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --radius:    14px;
    --radius-sm: 8px;
}
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}
.block-container { max-width: 780px !important; padding: 2rem 1.5rem 6rem !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }

.brand { display: flex; align-items: center; gap: 10px; padding: 4px 0 20px; }
.brand-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 19px;
}
.brand-name { font-family: 'Sora', sans-serif !important; font-size: 1.2rem !important; font-weight: 700 !important; color: var(--text) !important; letter-spacing: -0.02em; line-height: 1.2; }
.brand-tag  { font-size: 0.68rem !important; color: var(--accent2) !important; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 500 !important; }

.sidebar-label { font-size: 0.68rem !important; font-weight: 600 !important; color: var(--muted) !important; text-transform: uppercase; letter-spacing: 0.1em; margin: 18px 0 8px !important; }
.stat-pill { background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 9px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
.stat-pill-label { font-size: 0.76rem; color: var(--muted); }
.stat-pill-value { font-size: 0.82rem; font-weight: 600; color: var(--text); }

/* Buttons */
.stButton > button {
    background: transparent !important; border: 1px solid var(--border) !important; color: var(--muted) !important;
    border-radius: var(--radius-sm) !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important; padding: 8px 16px !important; width: 100% !important;
    transition: all 0.2s !important; font-weight: 500 !important;
}
.stButton > button:hover { border-color: var(--red) !important; color: var(--red) !important; background: rgba(239,68,68,0.07) !important; }

/* Page header */
.page-header { text-align: center; padding: 1.8rem 0 1.4rem; }
.page-header h1 { font-family: 'Sora', sans-serif; font-size: 1.85rem; font-weight: 700; color: var(--text); letter-spacing: -0.03em; margin: 0 0 6px; }
.page-header p  { font-size: 0.88rem; color: var(--muted); margin: 0; }
.header-dot {
    display: inline-block; width: 9px; height: 9px; background: var(--green);
    border-radius: 50%; margin-right: 8px; vertical-align: middle; animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.45;transform:scale(.75)} }

/* Welcome card */
.welcome-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px 32px; margin: 1.5rem 0; text-align: center; }
.welcome-card h3 { font-family: 'Sora', sans-serif; font-size: 1.05rem; font-weight: 600; color: var(--text); margin: 0 0 8px; }
.welcome-card p  { font-size: 0.84rem; color: var(--muted); margin: 0 0 20px; line-height: 1.65; }

/* Debug panel */
.debug-panel { background: #0a0a0a; border: 1px solid #333; border-left: 3px solid #f59e0b; border-radius: var(--radius-sm); padding: 12px 16px; margin: 8px 0; font-family: monospace; font-size: 0.75rem; color: #d4d4d4; }
.debug-ok    { color: #10b981; }
.debug-err   { color: #ef4444; }
.debug-warn  { color: #f59e0b; }

/* Chat messages */
@keyframes slide-up { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
[data-testid="stChatMessage"] { animation: slide-up 0.22s ease-out !important; background: transparent !important; border: none !important; box-shadow: none !important; padding: 4px 0 !important; }

/* Chat input */
[data-testid="stChatInput"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.14) !important; }

/* Expander */
.streamlit-expanderHeader  { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--muted) !important; font-size: 0.8rem !important; }
.streamlit-expanderContent { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: var(--surface2) !important; border: 1px dashed var(--border) !important; border-radius: var(--radius-sm) !important; }

/* Disclaimer */
.disclaimer { text-align: center; padding: 22px 16px; margin-top: 40px; border-top: 1px solid var(--border); font-size: 0.76rem; color: var(--muted); line-height: 1.75; }
.disclaimer strong { color: var(--amber); }

hr { border-color: var(--border) !important; margin: 14px 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ── 3. SESSION STATE ──────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "chip_prompt" not in st.session_state: st.session_state.chip_prompt = None
if "debug_log"   not in st.session_state: st.session_state.debug_log   = []
if "assets_ok"   not in st.session_state: st.session_state.assets_ok   = False


# ── 4. LOAD ASSETS ────────────────────────────────────────────────────────────
load_dotenv(override=True)

def add_debug(msg: str, level: str = "info"):
    ts  = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_log.append({"ts": ts, "msg": msg, "level": level})

@st.cache_resource(show_spinner="Loading models…")
def load_assets():
    errors = []

    # — FAISS index —
    try:
        index = faiss.read_index("faiss_index.bin")
    except Exception as e:
        errors.append(f"faiss_index.bin: {e}")
        index = None

    # — Chunks —
    try:
        chunks = np.load("chunks.npy", allow_pickle=True)
    except Exception as e:
        errors.append(f"chunks.npy: {e}")
        chunks = None

    # — Embedding model —
    try:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        errors.append(f"SentenceTransformer: {e}")
        embed_model = None

    # — Reranker —
    try:
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    except Exception as e:
        errors.append(f"CrossEncoder: {e}")
        reranker = None

    return index, chunks, embed_model, reranker, errors

index, chunks, embed_model, reranker, load_errors = load_assets()
assets_ok = not load_errors and all(
    x is not None for x in [index, chunks, embed_model, reranker]
)


# ── 5. HELPERS ────────────────────────────────────────────────────────────────
def run_generation(prompt: str, uploaded_file):
    """RAG retrieval + Ollama generation. Returns (response_text, valid_sources)."""
    # Retrieval
    query_emb = embed_model.encode(
        [prompt], normalize_embeddings=True
    ).astype("float32")
    _, indices = index.search(query_emb, 10)
    retrieved  = [chunks[i] for i in indices[0] if i != -1]

    pairs  = [[prompt, item["text"]] for item in retrieved]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(retrieved, scores), key=lambda x: x[1], reverse=True)
    valid  = [r for r in ranked if r[1] > -5.0]

    context_text = (
        "\n---\n".join([r[0]["text"] for r in valid[:3]]) if valid else "None."
    )

    system_instruction = (
        "You are Pulse, a professional and empathetic medical AI assistant. "
        "Answer clearly and concisely. Always recommend consulting a qualified "
        "healthcare professional for clinical decisions. "
        f"Use this medical knowledge context when relevant: {context_text}"
    )

    # Build messages list for Ollama
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]

    # Process image for Ollama Vision Model if attached
    if uploaded_file:
        model_to_use = OLLAMA_VISION_MODEL
        image_bytes = uploaded_file.getvalue()
        messages[1]["images"] = [image_bytes]  # Ollama accepts raw bytes directly
    else:
        model_to_use = OLLAMA_TEXT_MODEL

    add_debug(f"Calling Ollama ({model_to_use}) — context chunks: {len(valid)}")

    # Make the call to the local Ollama instance
    response = ollama.chat(
        model=model_to_use,
        messages=messages
    )

    response_text = response['message']['content']

    if not response_text:
        raise ValueError("Ollama returned no text content.")

    add_debug(f"Response received — {len(response_text)} chars", "ok")
    
    # Simple dict/class return to keep the render function compatible
    class MockResponse:
        pass
    resp_obj = MockResponse()
    resp_obj._extracted_text = response_text
    
    return resp_obj, valid


def render_response(response, valid_sources):
    text = response._extracted_text
    with st.chat_message("assistant"):
        st.markdown(text)
        if valid_sources:
            with st.expander("📄 View sources"):
                for i, (res, score) in enumerate(valid_sources[:3]):
                    st.markdown(
                        f"**Source {i+1}** &nbsp;·&nbsp; "
                        f"<span style='color:#8b949e;font-size:0.76rem;'>"
                        f"relevance {score:.2f}</span>",
                        unsafe_allow_html=True,
                    )
                    st.info(res["text"])
    st.session_state.messages.append({"role": "assistant", "content": text})


def handle_prompt(prompt: str, uploaded_file):
    """Full pipeline: display user msg → generate → handle errors."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    add_debug(f"User asked: {prompt[:80]}…" if len(prompt) > 80 else f"User asked: {prompt}")

    with st.spinner("Analyzing locally with Ollama..."):
        try:
            response, valid_sources = run_generation(prompt, uploaded_file)
            render_response(response, valid_sources)
        except Exception as e:
            error_str = str(e)
            add_debug(f"Exception: {error_str[:200]}", "err")
            st.error(f"**Error:** Could not connect to Ollama. Make sure Ollama is running on your machine and you have pulled the '{OLLAMA_TEXT_MODEL}' and '{OLLAMA_VISION_MODEL}' models. Details: {error_str}")


# ── 6. SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="brand">
            <div class="brand-icon">🩺</div>
            <div>
                <div class="brand-name">Pulse</div>
                <div class="brand-tag">Medical AI Assistant</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Asset status ──────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">System Status</div>', unsafe_allow_html=True)
    if assets_ok:
        st.markdown("""
            <div class="stat-pill">
                <span class="stat-pill-label">All systems</span>
                <span class="stat-pill-value" style="color:#10b981;">✔ Ready</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        for err in load_errors:
            st.markdown(f"""
                <div class="stat-pill">
                    <span class="stat-pill-label" style="color:#ef4444;">✘ {err[:40]}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="stat-pill">
            <span class="stat-pill-label">Provider</span>
            <span class="stat-pill-value">Local (Ollama)</span>
        </div>
        <div class="stat-pill">
            <span class="stat-pill-label">Messages</span>
            <span class="stat-pill-value">{len(st.session_state.messages)}</span>
        </div>
        <div class="stat-pill">
            <span class="stat-pill-label">Retrieval</span>
            <span class="stat-pill-value">RAG · Reranked</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Image upload ──────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Attach Image</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload X-ray or symptom photo",
        type=["jpg", "png", "jpeg"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.image(uploaded_file, caption="Attached", use_container_width=True)

    st.markdown("---")
    if st.button("🗑  Clear conversation"):
        st.session_state.messages = []
        st.session_state.debug_log = []
        st.rerun()

    # ── Debug log expander ────────────────────────────────────────────────
    if st.session_state.debug_log:
        with st.expander("🔍 Debug log", expanded=False):
            for entry in reversed(st.session_state.debug_log[-30:]):
                css = {"ok": "debug-ok", "err": "debug-err",
                       "warn": "debug-warn"}.get(entry["level"], "")
                st.markdown(
                    f'<div class="debug-panel"><span class="{css}">'
                    f'[{entry["ts"]}] {entry["msg"]}</span></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("""
        <div style="padding-top:20px;">
            <div style="font-size:0.7rem;color:#8b949e;line-height:1.65;">
                ⚠️ For educational use only.<br>
                Not a substitute for professional<br>medical advice.
            </div>
        </div>
    """, unsafe_allow_html=True)


# ── 7. MAIN AREA ──────────────────────────────────────────────────────────────
st.markdown("""
    <div class="page-header">
        <h1><span class="header-dot"></span>Pulse</h1>
        <p>Ask anything about symptoms, conditions, medications, or health topics.</p>
    </div>
""", unsafe_allow_html=True)

# ── Asset load failure — stop here with clear instructions ────────────────
if not assets_ok:
    st.error("⚠️ **Startup failed.** Check the sidebar for details.")
    for err in load_errors:
        st.markdown(f"- `{err}`")
    st.info(
        "**Common fixes:**\n"
        "1. Make sure `faiss_index.bin` and `chunks.npy` are in the same folder as `app.py`.\n"
        "2. Run `pip install ollama sentence-transformers faiss-cpu` if any package is missing."
    )
    st.stop()

# ── Welcome card ──────────────────────────────────────────────────────────
SUGGESTIONS = [
    "What causes chest pain?",
    "Explain my blood test results",
    "Signs of diabetes",
    "Common drug interactions",
    "When should I see a doctor?",
    "Normal blood pressure range",
]

if not st.session_state.messages:
    st.markdown("""
        <div class="welcome-card">
            <h3>How can I help you today?</h3>
            <p>I can explain symptoms, review lab values, discuss medications,<br>
                or analyse an uploaded X-ray or photo using local AI.</p>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, suggestion in enumerate(SUGGESTIONS):
        with cols[idx % 3]:
            if st.button(suggestion, key=f"chip_{idx}"):
                st.session_state.chip_prompt = suggestion
                st.rerun()

# ── Conversation history ──────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Handle new input ──────────────────────────────────────────────────────
# Handle chip click
if st.session_state.chip_prompt:
    pending = st.session_state.chip_prompt
    st.session_state.chip_prompt = None
    handle_prompt(pending, uploaded_file)

# Normal chat input
else:
    prompt = st.chat_input("Type your medical question…")
    if prompt:
        handle_prompt(prompt, uploaded_file)

# ── 8. DISCLAIMER ────────────────────────────────────────────────────────────
st.markdown("""
    <div class="disclaimer">
        <strong>⚠ Educational purposes only</strong><br>
        Pulse is a demonstration of RAG + multimodal AI and is <em>not</em> a clinical tool.<br>
        Always consult a qualified healthcare professional for medical decisions.
    </div>
""", unsafe_allow_html=True)