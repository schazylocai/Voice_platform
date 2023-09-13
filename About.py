import streamlit as st
import os

from src.English_Language import write_english_About
from src.Arabic_Language import write_Arabic_About
from src.Change_Text_Style import change_text_style_arabic, change_text_style_english

from dotenv import load_dotenv
from src.stripe_functions_english import check_customers_eng, subscribe_to_service_eng, cancel_service_eng, \
    forgot_password_eng
from src.stripe_functions_arabic import check_customers_ara, subscribe_to_service_ara, cancel_service_ara, \
    forgot_password_ara

load_dotenv()  # read local .env file

st.set_page_config(layout="wide", initial_sidebar_state='expanded', page_icon="🔬", page_title='GPT Document Analyzer')
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

################### Define LLM Model ###################
llm_model = 'gpt-3.5-turbo'  # gpt-4 or gpt-3.5-turbo

################### Set session states ###################
st.session_state.setdefault("mylanguage", 'العربية')
st.session_state.setdefault("user_status", 'False')

if 'mylanguage' not in st.session_state:
    st.session_state.mylanguage = 'العربية'

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

if 'ChatOpenAI' not in st.session_state:
    st.session_state.ChatOpenAI = llm_model

# status = False
valid_email = False
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def change_language_to_Arabic():
    st.divider()
    change_text_style_arabic('☘️︎ بإستطاعتك الآن التفاعل مع أي ملف أو أي موقع على الإنترنت أو أي شريط ڤيديو من موقع يوتيوب.', 'subhead_new_item', violet)
    st.write('')
    col1, col2, col3 = st.columns(3)
    with col3:
        st.image('gpt_logos/GPTdoc.png')
    with col2:
        st.image('gpt_logos/GPTweb.png')
    with col1:
        st.image('gpt_logos/GPTyoutube.png')
    st.divider()
    write_Arabic_About()

    st.session_state.subscribed_status = check_customers_ara()
    subscribe_to_service_ara()
    cancel_service_ara()
    forgot_password_ara()


def change_language_to_English():
    st.divider()
    st.subheader(
        ':violet[☘️ You can now interact with any document, website, or Youtube video.]')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image('gpt_logos/GPTdoc.png')
    with col2:
        st.image('gpt_logos/GPTweb.png')
    with col3:
        st.image('gpt_logos/GPTyoutube.png')
    st.divider()
    write_english_About()

    st.session_state.subscribed_status = check_customers_eng()
    subscribe_to_service_eng()
    cancel_service_eng()
    forgot_password_eng()


def first_page():
    col1, col2, col3 = st.columns(3)

    with col3:

        if st.session_state.mylanguage == 'English':
            language_options = ('English', 'العربية')
        else:
            language_options = ('العربية', 'English')

        my_language = st.selectbox("/", options=language_options,
                                   label_visibility='hidden')

    if my_language == 'English':
        with col1:
            change_text_style_english("GPT Analyzer", 'title', violet)
            st.write("")

        with col3:
            change_text_style_arabic("🌏  اختر لغتك", 'head', violet)

        st.session_state.mylanguage = 'English'
        change_language_to_English()

    if my_language == 'العربية':
        with col1:
            change_text_style_arabic("محلل جي بي تي", 'title', violet)

        with col3:
            change_text_style_english("🌏  Choose your language", 'head', violet)

        st.session_state.mylanguage = 'العربية'
        change_language_to_Arabic()


first_page()
