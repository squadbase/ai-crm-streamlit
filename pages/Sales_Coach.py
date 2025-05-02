import os
import pathlib
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env')

openai_api_key = os.environ.get("OPENAI_API_KEY")
attio_api_key = os.environ.get("ATTIO_ACCESS_TOKEN")
ATTIO_API_BASE = "https://api.attio.com/v2"
KNOWLEDGE_DIR = pathlib.Path("knowledge")

st.logo('assets/squadbase.png', link='https://squadbase.dev', icon_image='assets/squadbase_icon.png')

@st.cache_resource(show_spinner=False)
def load_all_markdown() -> str:
    """Recursively read all *.md files under the knowledge directory and concatenate them."""
    md_files = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    if not md_files:
        return "# Knowledge base is empty!"

    contents = []
    for path in md_files:
        contents.append(f"<!-- {path.relative_to(KNOWLEDGE_DIR)} -->\n")
        contents.append(path.read_text(encoding="utf-8"))
        contents.append("\n\n")
    return "".join(contents)

SYSTEM_PROMPT = load_all_markdown()

@st.cache_data(ttl=300)   # 5-minute cache
def fetch_notes(page_size: int = 20) -> pd.DataFrame:
    url = f"{ATTIO_API_BASE}/notes"
    params = {"limit": page_size}
    all_rows = []

    while True:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {attio_api_key}",
                "Content-Type": "application/json"
            },
            params=params,
            timeout=30
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx responses
        payload = response.json()    # {"data":[…], "next_cursor": "...", "has_more": true}
        all_rows.extend(payload["data"])

        # --- Pagination ---
        if payload.get("has_more") and payload.get("next_cursor"):
            params["page[after]"] = payload["next_cursor"]
        else:
            break

    # --- Convert to DataFrame & keep relevant columns ---
    df = pd.json_normalize(all_rows)
    return df

@st.dialog("Knowledge", width='large')
def knowledge_dialog():
    st.markdown(SYSTEM_PROMPT)

@st.dialog("Data connections", width='large')
def data_connections_dialog():
    st.write("## Retrieve Notes from Attio")
    st.dataframe(st.session_state.notes_df)

with st.sidebar:
    st.write("""
# Sales Coach
Sales Coach can help you with your sales strategy and tactics.
    """)
    st.write("""
### knowledge/*.md
It reads the Markdown files located in the knowledge folder of the source code. Please describe your product in these files. By maintaining the Markdown files in this folder, the coach will evolve to suit you better.
""")
    if st.button("See knowledge"):
        knowledge_dialog()
    st.write("""
### Data connections
You can provide additional contextual information, such as data from your CRM or data stored in your data warehouse. In this demo, meeting notes from deals are imported via the [Attio](https://attio.com/) API.
""")
    if st.button("See data connections"):
        data_connections_dialog()

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "system" not in st.session_state:
    st.session_state.system = {"role": "system", "content": SYSTEM_PROMPT}
if "notes_df" not in st.session_state:
    st.session_state.notes_df = fetch_notes()

def messagify_notes_df(notes_df: pd.DataFrame) -> str:
    markdown_list = notes_df["content_markdown"].tolist()
    combined_md = "\n\n".join(
        f"## note {i+1}\n{md}"
        for i, md in enumerate(markdown_list)
    )
    return combined_md

def send_message(message: str):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    client = OpenAI(api_key=openai_api_key)
    user_message = {"role": "user", "content": message}
    st.session_state.messages.append(user_message)
    st.chat_message("user").write(message)

    response = client.chat.completions.create(
        messages=[
            st.session_state.system,
            {"role": "system", "content": "# Recent meeting logs\n\n" + messagify_notes_df(st.session_state.notes_df)}
        ] + st.session_state.messages,
        model="o3",
    )
    msg = response.choices[0].message
    assistant_message = {"role": "assistant", "content": msg.content}
    st.session_state.messages.append(assistant_message)
    st.chat_message("assistant").write(msg.content)
    st.rerun()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if len(st.session_state.messages) == 0:
    st.write("### Starting questions")
    if st.button("Which industry / company should we approach next?", use_container_width=True):
        send_message("Which industry / company should we approach next?")
    if st.button("What is the ideal proposal storyline to sell to Squadbase?", use_container_width=True):
        send_message("What is the ideal proposal storyline to sell to Squadbase?")
    if st.button("Based on meeting logs, what are the characteristics of a successful business meeting?", use_container_width=True):
        send_message("Based on meeting logs, what are the characteristics of a successful business meeting?")
if prompt := st.chat_input():
    send_message(prompt)
