import streamlit as st
import os

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔬",
    page_title="Mira",
)
violet = "rgb(169, 131, 247)"
red = "rgb(169, 131, 247)"


def construct_pages():
    stt = st.Page(page='src/speech_model.py',
                               title='STT', icon=':material/arrow_forward_ios:')

    pages = st.navigation(
        {
            "LOCAI": [stt],
        }
    )
    pages.run()


def launch_application():
    construct_pages()


launch_application()
