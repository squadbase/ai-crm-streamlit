import streamlit as st
from utils.knowledge import knowledge_dialog_button, load_knowledge_md
from utils.openai import openai_client
from typing import Optional, Literal
from pydantic import BaseModel
from openai.types.chat import (
    ChatCompletionMessageParam,
)
from time import sleep


# Session States


class ResearchReportManager:
    def __init__(self):
        self.key = "research_report"
        if self.key not in st.session_state:
            st.session_state[self.key] = None

    def get(self) -> Optional[str]:
        return st.session_state[self.key]

    def set(self, value: Optional[str]):
        st.session_state[self.key] = value


class Message(BaseModel):
    role: Literal["user", "system"]
    content: str


class MessagesManager:
    def __init__(self) -> None:
        self.key = "messages"
        if self.key not in st.session_state:
            st.session_state[self.key] = []

    def get(self) -> list[Message]:
        return st.session_state[self.key]

    def get_chat_completion_params(self) -> list[ChatCompletionMessageParam]:
        chat_completion_messages: list[Message] = st.session_state[self.key]
        return [
            {"role": "user", "content": m.content}
            if m.role == "user"
            else {"role": "system", "content": m.content}
            for m in chat_completion_messages
        ]

    def add_user_message(self, message: str):
        st.session_state[self.key].append(Message(role="user", content=message))

    def add_response(self, message: str):
        st.session_state[self.key].append(Message(role="system", content=message))


research_report_manager = ResearchReportManager()
messages_manager = MessagesManager()


# Functions


def get_initial_prompt(company_name: str) -> str:
    return f"""\
You are a sales team assistant.
We have an initial sales meeting scheduled with {company_name}, and I need your help in preparing for it.
Please conduct the necessary research for the initial sales meeting, using the product information as a reference.

### Research Overview
Target Company: {company_name}

- Are they using Streamlit for building internal applications?
- How are they building their internal applications? Please investigate in detail, especially if they are using Streamlit or Next.js.
- What initiatives are they taking regarding data utilization and AI implementation within their company?

### Reference Information: About Our Product
{load_knowledge_md()}
"""


def send_message(prompt: str) -> Optional[str]:
    messages_manager.add_user_message(prompt)

    messages = messages_manager.get_chat_completion_params()
    messages.append({"role": "user", "content": prompt})

    response_content = (
        openai_client.chat.completions.create(
            model="gpt-4o-mini-search-preview", messages=messages, web_search_options={}
        )
        .choices[0]
        .message.content
    )

    if response_content:
        messages_manager.add_response(response_content)

    return response_content


def summarize_messages_to_markdown() -> Optional[str]:
    messages = messages_manager.get_chat_completion_params()

    prompt = """
Please summarize the conversation history and create a final research report.
"""

    messages.append({"role": "user", "content": prompt})

    summary = (
        openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        .choices[0]
        .message.content
    )

    if not summary:
        return None

    return f"""
{summary}

<details>
<summary>Details</summary>

```json
{message.model_dump_json(indent=2)}
```
</details>
"""


def save_to_crm():
    sleep(3)
    pass


# UI

st.title("Data Enrichment")

knowledge_dialog_button()

with st.form("company_form"):
    company_name = st.text_input("Company Name")
    if st.form_submit_button("Submit"):
        research_report_manager.set(send_message(get_initial_prompt(company_name)))

messages = messages_manager.get()

if len(messages) >= 2:
    if followup_prompt := st.chat_input(
        "Do you need more detailed research or follow-up?"
    ):
        send_message(followup_prompt)

for message in messages:
    st.chat_message(message.role).markdown(message.content)

if st.button("Summarize", disabled=len(messages) == 0):
    summarized_md = summarize_messages_to_markdown()

    @st.dialog("Research Report", width="large")
    def final_result_dialog():
        if st.button("Save"):
            save_to_crm()
            st.toast("Saved Successfully")

        st.markdown(summarized_md)

    final_result_dialog()
