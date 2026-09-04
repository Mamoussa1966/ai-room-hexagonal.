import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic
from deep_translator import GoogleTranslator
import random

st.set_page_config(page_title="غرفة المحادثة الخماسية الكبرى", page_icon="🌟", layout="wide")

st.title("🌟 الغرفة الخماسية الكبرى (Gemini, ChatGPT, Claude, Grok, Kimi)")
st.subheader("نقاش جماعي متكامل يضم 5 من أقوى نماذج الذكاء الاصطناعي")

with st.sidebar:
    st.header("🔑 إعداد مفاتيح الـ API الخمسة")
    gemini_key = st.text_input("مفتاح Gemini API:", type="password")
    openai_key = st.text_input("مفتاح ChatGPT API:", type="password")
    claude_key = st.text_input("مفتاح Claude API:", type="password")
    grok_key = st.text_input("مفتاح Grok (xAI) API:", type="password")
    kimi_key = st.text_input("مفتاح Kimi (Moonshot) API:", type="password")
    
    st.markdown("---")
    st.header("🎛️ لوحة التحكم في المتحدثين")
    talk_mode = st.radio(
        "اختر نمط الإجابة والردود:",
        ("الجميع بالترتيب المتتابع", "متحدث واحد محدد فقط", "اختيار متحدث عشوائي")
    )
    
    selected_speaker = None
    if talk_mode == "متحدث واحد محدد فقط":
        selected_speaker = st.selectbox(
            "اختر المتحدث الحالي:",
            ("Gemini", "ChatGPT", "Claude", "Grok", "Kimi")
        )
        
    st.markdown("---")
    def reset_chat():
        st.session_state.chat_history = []
        st.toast("🧹 تم مسح المحادثة بالكامل!")

    st.button("🧹 مسح المحادثة وإعادة التعيين", on_click=reset_chat, use_container_width=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def build_context(bot_name):
    ctx = f"You are {bot_name}, participating in a 5-way group chat with User, Gemini, ChatGPT, Claude, Grok, and Kimi.\n"
    ctx += "Respond in Arabic, and provide a clear English translation below your response.\n\n"
    for msg in st.session_state.chat_history:
        ctx += f"[{msg['sender']}]: {msg['content_ar']} (Translation: {msg['content_en']})\n"
    ctx += f"Now, respond as {bot_name}:"
    return ctx

def get_gemini_resp(prompt, key):
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
    except Exception as e:
        return f"⚠️ خطأ في اتصال Gemini: {str(e)}"

def get_openai_resp(prompt, key, model="gpt-4o-mini"):
    try:
        client = OpenAI(api_key=key)
        return client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    except Exception as e:
        return f"⚠️ خطأ في اتصال ChatGPT: {str(e)}"

def get_claude_resp(prompt, key):
    try:
        client = anthropic.Anthropic(api_key=key)
        return client.messages.create(model="claude-3-haiku-20240307", max_tokens=1000, messages=[{"role": "user", "content": prompt}]).content[0].text
    except Exception as e:
        return f"⚠️ خطأ في اتصال Claude: {str(e)}"

def get_grok_resp(prompt, key):
    try:
        client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
        return client.chat.completions.create(model="grok-beta", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    except Exception as e:
        return f"⚠️ خطأ في اتصال Grok: {str(e)}"

def get_kimi_resp(prompt, key):
    try:
        client = OpenAI(api_key=key, base_url="https://api.moonshot.cn/v1")
        return client.chat.completions.create(model="moonshot-v1-8k", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    except Exception as e:
        return f"⚠️ خطأ في اتصال Kimi: {str(e)}"

st.write("### 🖥️ شاشة المحادثة النشطة (مترجمة ثنائياً):")
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['sender']}:**")
        st.markdown(f"**بالعربية:** {msg['content_ar']}")
        st.markdown(f"*English:* {msg['content_en']}")
        st.markdown("---")

if user_input := st.chat_input("اكتب رسالتك بالعربية هنا لتظهر للجميع..."):
    try:
        user_en = GoogleTranslator(source='auto', target='en').translate(user_input)
    except:
        user_en = user_input
        
    st.session_state.chat_history.append({
        "role": "user",
        "sender": "أنت (المستخدم)",
        "content_ar": user_input,
        "content_en": user_en
    })
    st.rerun()

if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "user":
    speakers = []
    all_spks = ["Gemini", "ChatGPT", "Claude", "Grok", "Kimi"]
    
    if talk_mode == "الجميع بالترتيب المتتابع":
        speakers = all_spks
    elif talk_mode == "متحدث واحد محدد فقط":
        speakers = [selected_speaker]
    elif talk_mode == "اختيار متحدث عشوائي":
        speakers = [random.choice(all_spks)]

    for spk in speakers:
        with st.spinner(f"[{spk}] يقرأ الشاشة ويكتب رده..."):
            reply = ""
            if spk == "Gemini":
                reply = get_gemini_resp(build_context("Gemini"), gemini_key) if gemini_key else "Gemini Key missing."
            elif spk == "ChatGPT":
                reply = get_openai_resp(build_context("ChatGPT"), openai_key) if openai_key else "ChatGPT Key missing."
            elif spk == "Claude":
                reply = get_claude_resp(build_context("Claude"), claude_key) if claude_key else "Claude Key missing."
            elif spk == "Grok":
                reply = get_grok_resp(build_context("Grok"), grok_key) if grok_key else "Grok Key missing."
            elif spk == "Kimi":
                reply = get_kimi_resp(build_context("Kimi"), kimi_key) if kimi_key else "Kimi Key missing."
            
            try:
                reply_en = GoogleTranslator(source='auto', target='en').translate(reply)
            except:
                reply_en = reply
                
            st.session_state.chat_history.append({
                "role": "assistant",
                "sender": spk,
                "content_ar": reply,
                "content_en": reply_en
            })
    st.rerun()
