import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env')

openai_api_key = os.environ.get("OPENAI_API_KEY")

run_id = str(uuid.uuid4())

threads = []

with st.sidebar:
    st.write("Streamlit + OpenAI")

st.title("CRM RAG Chat")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(
        api_key=openai_api_key,
    )
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        messages=st.session_state.messages,
        model="o4-mini",
    )
    msg = response.choices[0].message
    assistant_message = {"role": "assistant", "content": msg.content}
    st.session_state.messages.append(assistant_message)
    st.chat_message("assistant").write(msg.content)