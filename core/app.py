import mysql.connector
import requests
import streamlit as st

import chat as backend

st.set_page_config(
    page_title=f"{backend.SCHOOL_NAME} | School Assistant",
    page_icon="🏫",
    layout="centered",
    initial_sidebar_state="expanded",
)

GREETING = "Hi! Have a nice day. How can I help you?"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, button, input, textarea {
    font-family: 'Lexend', sans-serif;
}
.stApp { background: #f4f6fa; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 760px; }

/* Header */
.hero {
    background: #173b65;
    border-radius: 16px;
    padding: 26px 28px;
    margin-bottom: 22px;
    border-bottom: 5px solid #f2b134;
}
.hero h1 {
    color: #ffffff;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    padding: 0;
    letter-spacing: -0.01em;
}
.hero p {
    color: #cfdcee;
    font-size: 0.95rem;
    margin: 0;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e1e7f0;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
[data-testid="stChatMessage"] p { line-height: 1.6; }

/* Suggestion buttons */
.stButton > button {
    width: 100%;
    background: #ffffff;
    color: #173b65;
    border: 1px solid #c9d5e6;
    border-radius: 10px;
    padding: 10px 12px;
    font-weight: 500;
    text-align: left;
}
.stButton > button:hover {
    border-color: #173b65;
    background: #edf2fa;
    color: #173b65;
}
.stButton > button:focus-visible {
    outline: 3px solid #f2b134;
}
.hint {
    color: #5b6b82;
    font-size: 0.9rem;
    margin: 4px 0 10px 2px;
}

/* Sidebar */
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e1e7f0; }
.side-note {
    background: #fff6e0;
    border-left: 4px solid #f2b134;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 0.85rem;
    color: #4a3b10;
}

/* ---- Polished look (overrides earlier rules) ---- */
.hero {
    display: flex;
    align-items: center;
    gap: 18px;
    background: linear-gradient(135deg, #173b65 0%, #25599a 100%);
    box-shadow: 0 10px 28px rgba(23, 59, 101, 0.20);
}
.hero-icon {
    width: 58px;
    height: 58px;
    flex-shrink: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
}
.hero-status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    color: #cfdcee;
    font-size: 0.82rem;
}
.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4ade80;
    display: inline-block;
}

/* Assistant bubbles on the left, user bubbles on the right */
[data-testid="stChatMessage"] {
    box-shadow: 0 2px 10px rgba(23, 59, 101, 0.06);
    margin-right: 12%;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    margin-right: 0;
    margin-left: 12%;
    background: #173b65;
    border-color: #173b65;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * {
    color: #ffffff;
}

/* Rounded chat input */
[data-testid="stChatInput"] {
    border-radius: 999px;
    box-shadow: 0 4px 18px rgba(23, 59, 101, 0.12);
}

/* Starter questions as pills */
.stButton > button {
    border-radius: 999px;
    text-align: center;
}

/* ---- Colourful school theme ---- */
.stApp {
    background-color: #eaf4ff;
    background-image: repeating-linear-gradient(
        to bottom, transparent 0, transparent 35px,
        rgba(91, 141, 239, 0.14) 35px, rgba(91, 141, 239, 0.14) 36px
    );
}
.hero {
    position: relative;
    overflow: hidden;
    border-bottom: none;
    padding-bottom: 32px;
    background: linear-gradient(120deg, #1d4f91 0%, #2f6fed 60%, #4ecdc4 130%);
}
.hero::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 8px;
    background: linear-gradient(90deg, #f2b134 0 25%, #ef6f6c 25% 50%, #4ecdc4 50% 75%, #8b6cf0 75% 100%);
}
.hero-doodles {
    margin-left: auto;
    font-size: 1.7rem;
    letter-spacing: 6px;
    opacity: 0.95;
}
@media (max-width: 600px) { .hero-doodles { display: none; } }

[data-testid="stChatMessage"] {
    background: #ffffff;
    border: none;
    border-left: 6px solid #f2b134;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(47, 111, 237, 0.10);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #2f6fed, #5b8def);
    border-left: none;
    border-right: 6px solid #4ecdc4;
}
[data-testid="stChatInput"] {
    background: #ffffff;
    border: 2px solid #5b8def;
    border-radius: 999px;
}
[data-testid="stSidebar"] { background: #fffaf0; border-right: 3px solid #f2b134; }

/* ---- Professional theme ---- */
.stApp { background: #f3f6fb; background-image: none; }
.hero {
    background: linear-gradient(120deg, #12325a 0%, #1f5aa6 100%);
    box-shadow: 0 6px 20px rgba(18, 50, 90, 0.18);
}
.hero::after { height: 4px; background: #f2b134; }
.hero-icon { background: rgba(255, 255, 255, 0.12); }
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e1e7f0;
    border-left: 4px solid #1f5aa6;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(18, 50, 90, 0.06);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1f5aa6;
    border: 1px solid #1f5aa6;
}
[data-testid="stChatInput"] {
    border: 1px solid #c5d3e8;
    box-shadow: 0 4px 14px rgba(18, 50, 90, 0.08);
}
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e1e7f0; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero">
    <div class="hero-icon">🏫</div>
    <div>
        <h1>{backend.SCHOOL_NAME}</h1>
        <p>Welcome to our AI School Assistant</p>
        <div class="hero-status"><span class="dot"></span>Online</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.session_state.history = []


if "messages" not in st.session_state:
    reset_chat()

with st.sidebar:
    st.subheader("School Assistant")
    if st.button("Clear conversation"):
        reset_chat()
        st.rerun()

    st.markdown("**Contact the office**")
    st.write(f"Phone: {backend.SCHOOL_PHONE}")
    st.write(f"Email: {backend.SCHOOL_EMAIL}")



for message in st.session_state.messages:
    avatar = "🏫" if message["role"] == "assistant" else "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Type your message...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🏫"):
        with st.spinner("Looking that up..."):
            try:
                answer = backend.agent_answer(question, st.session_state.history)

            except requests.exceptions.ConnectionError:
                answer = (
                    "The language model isn't reachable. "
                    "Start Ollama (`ollama serve`) and try again."
                )
            except mysql.connector.Error:
                answer = (
                    "I couldn't connect to the school database. "
                    "Check that MySQL is running and try again."
                )
            except Exception:
                answer = (
                    "Something went wrong while answering that. "
                    "Please rephrase the question and try again."
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
    st.session_state.history.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    )
    st.session_state.history = st.session_state.history[-12:]