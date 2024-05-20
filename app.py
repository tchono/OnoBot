import streamlit as st
from groq import Groq

import logging
import json
import base64


client = Groq(api_key=st.secrets["GROQ_API_KEY"])

logging.basicConfig(level=logging.INFO)

title = "OnoBot"
OnoBot_img = "imgs/OnoBot.png"
a_avatar_img = "imgs/assistant.png"
u_avatar_img = "imgs/user.png"
model_engine = "llama3-70b-8192"

st.set_page_config(
    page_title = f"{title} - An Intelligent Streamlit Assistant",
    page_icon = OnoBot_img,
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items = {
        "Get help": "https://github.com/ここ",
        "Report a bug": "https://github.com/AdieLaine/ここ",
        "About": f"""
            ## {title}
            
            **GitHub**: https://github.com/ここ/
            
            チャットアプリです。追記予定。
        """
    }
)

st.title("Ono Bot")

@st.cache_data(show_spinner=False)
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@st.cache_data(show_spinner=False)
def load_initial_values():
    path = "data/initial_values.json"
    return load_json(path)

@st.cache_data(show_spinner=False)
def get_avatar_image(role):
    if role == "assistant":
        return a_avatar_img
    elif role == "user":
        return u_avatar_img
    else:
        return None

@st.cache_data(show_spinner=False)
def generate(messages, stream=False):

    completion = client.chat.completions.create(
        model=model_engine,
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=stream,
        stop=None,
    )

    result = ""

    if stream == True:
        for chunk in completion:
            result += chunk.choices[0].delta.content or ""
    else:
        result = completion.choices[0].message.content or ""

    return result

def main():
    if "history" not in st.session_state:
        st.session_state.history = []
        st.session_state.system_prompt = []

    if not st.session_state.history:
        initial_values = load_initial_values()
        initial_bot_message = initial_values.get("initial_bot_message", "")
        prompt_text = initial_values.get("prompt_text", "")
        st.session_state.system_prompt = [
            {"role": "system", "content": prompt_text}
            ]
        st.session_state.history = [
            {"role": "assistant", "content": initial_bot_message}
            ]

    st.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow:
                0 0 5px #003300,
                0 0 10px #006600,
                0 0 15px #009900,
                0 0 20px #00CC00,
                0 0 25px #00FF00,
                0 0 30px #33FF33,
                0 0 35px #66FF66;
            position: relative;
            z-index: -1;
            border-radius: 30px;  /* Rounded corners */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Function to convert image to base64
    def img_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Load and display sidebar image with glowing effect
    img_path = OnoBot_img
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Sidebar for Mode Selection
    mode = st.sidebar.radio("Select Mode:", options=["会話モード", "討論モード"], index=0)
    use_langchain = st.sidebar.checkbox("最新のモデルを適用 ", value=False)
    st.sidebar.markdown("---")

    show_basic_info = st.sidebar.toggle("Basic Interactions", value=True)
    if show_basic_info:
        st.sidebar.markdown("""
        ### Basic Interactions
        - **挨拶**: 「こんにちは」や「はじめまして」などの挨拶をすると、小野晋也さん風の挨拶を返します。
        - **経歴に関する質問**: 小野晋也さんの経歴について尋ねた場合、簡潔に答えます。
        """)

    show_advanced_info = st.sidebar.toggle("Show Advanced Interactions", value=False)

    if show_advanced_info:
        st.sidebar.markdown("""
        ### Advanced Interactions
        - **議論・討論**: 小野晋也さんの考えを踏まえて、ユーザが提示した問題について深く議論します。
        - **アドバイス**: ユーザがリーダーシップや起業家精神についてアドバイスを求めた場合、示唆に富んだアドバイスを提供します。
        """)
    st.sidebar.markdown("---")

    for message in st.session_state.history[-20:]:
        role = message["role"]
        with st.chat_message(role, avatar=get_avatar_image(role)):
            st.markdown(message["content"])

    chat_input = st.chat_input("メッセージを送信する:")
    if chat_input:
        st.session_state.history.append({"role": "user", "content": chat_input})
        with st.chat_message("user", avatar=get_avatar_image("user")):
            st.markdown(chat_input)

        with st.chat_message("assistant", avatar=get_avatar_image("assistant")):
            result = generate(st.session_state.system_prompt + st.session_state.history[-20:])
            st.markdown(result)
            st.session_state.history.append({"role": "assistant", "content": result})

if __name__ == "__main__":
    main()