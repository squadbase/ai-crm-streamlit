import pathlib
import streamlit as st

KNOWLEDGE_DIR = pathlib.Path("knowledge")


@st.cache_resource(show_spinner=False)
def load_knowledge_md() -> str:
    """/knowledge 以下の *.md を再帰的に読み込んで連結して返す"""
    md_files = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    if not md_files:
        return "# Knowledge base is empty!"

    contents = []
    for path in md_files:
        contents.append(f"<!-- {path.relative_to(KNOWLEDGE_DIR)} --> \n")
        contents.append(path.read_text(encoding="utf-8"))
        contents.append("\n\n")
    return "".join(contents)


@st.dialog("Knowledge", width="large")
def knowledge_dialog():
    st.markdown(load_knowledge_md())


def knowledge_dialog_button():
    if st.button("Knowledge"):
        knowledge_dialog()
