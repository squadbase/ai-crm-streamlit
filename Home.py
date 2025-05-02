import streamlit as st

st.set_page_config(
    page_title="Squadbase x Streamlit Demo",
    page_icon="assets/squadbase_icon.png",
)

st.logo('assets/squadbase.png', link='https://squadbase.dev', icon_image='assets/squadbase_icon.png')

st.write("# Welcome to Squadbase x Streamlit Demo! 🚀")

st.markdown(
    """
    This is a demo application of Squadbase x Streamlit to showcase how AI apps can empower you.
    
    **👈 Select a demo from the sidebar** to see some examples
    of what AI apps can do!

    ### Want to learn more?
    - Check out [our website](https://squadbase.dev)
    - Jump into our [documentation](https://squadbase.dev/docs)
"""
)