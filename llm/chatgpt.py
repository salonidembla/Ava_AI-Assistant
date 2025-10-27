# llm/chatgpt.py
import os
import json
import google.generativeai as genai

# -----------------------------
# Load Gemini API key
# -----------------------------
def load_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and os.path.exists("config/config.json"):
        with open("config/config.json", "r", encoding="utf-8") as f:
            api_key = json.load(f).get("GEMINI_API")
    if not api_key:
        raise ValueError("❌ Gemini API key missing. Please add it in config/config.json or as an environment variable.")
    return api_key

# -----------------------------
# Initialize Gemini Chat Model
# -----------------------------
api_key = load_api_key()
genai.configure(api_key=api_key)

# Create persistent chat session
model = genai.GenerativeModel("models/gemini-2.5-flash")
chat_session = model.start_chat(history=[])

# -----------------------------
# Chat function with memory
# -----------------------------
def ChatGpt(prompt: str) -> str:
    """
    Conversational Gemini model.
    Remembers prior messages in this session for contextual replies.
    """
    try:
        response = chat_session.send_message(prompt)
        if hasattr(response, "text"):
            return response.text.strip()
        else:
            return "⚠️ Gemini returned no response text."
    except Exception as e:
        return f"⚠️ Gemini error: {e}"

# -----------------------------
# Optional: reset memory if needed
# -----------------------------
def clear_conversation():
    """Clears chat memory."""
    global chat_session
    chat_session = model.start_chat(history=[])
    return "✅ Conversation memory cleared."
