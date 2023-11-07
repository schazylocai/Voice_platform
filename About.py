import streamlit as st
import os
import datetime

from src.English_Language import write_english_About
from src.Arabic_Language import write_Arabic_About
from src.Change_Text_Style import change_text_style_arabic, change_text_style_english

from dotenv import load_dotenv
from src.stripe_functions_english import check_customers_eng, subscribe_to_service_eng, cancel_service_eng, \
    forgot_password_eng
from src.stripe_functions_arabic import check_customers_ara, subscribe_to_service_ara, cancel_service_ara, \
    forgot_password_ara

load_dotenv()  # read local .env file

LANGCHAIN_TRACING_V2 = os.environ['LANGCHAIN_TRACING_V2']
LANGCHAIN_ENDPOINT = os.environ['LANGCHAIN_ENDPOINT']
LANGCHAIN_API_KEY = os.environ['LANGCHAIN_API_KEY']
LANGCHAIN_PROJECT = os.environ['LANGCHAIN_PROJECT']

st.set_page_config(layout="wide", initial_sidebar_state='expanded', page_icon="🔬", page_title='GPT Document Analyzer')
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

##################### Define LLM Model ####################
llm_model = 'gpt-4-1106-preview'  # gpt-4 or gpt-3.5-turbo or gpt-3.5-turbo-16k or gpt-4-1106-preview

################### Set session states ###################
st.session_state.setdefault("mylanguage", 'English')
st.session_state.setdefault("user_status", 'False')

if 'mylanguage' not in st.session_state:
    st.session_state.mylanguage = 'English'

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
        ':violet[☘️ You can now interact with any document, website, or YouTube video]')
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

    # clear files from the cache folder
    # Define the path to the "cache" folder
    cache_folder = "cache"

    # Check if the "cache" folder exists
    if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
        # Get the current time
        current_time = datetime.datetime.now()

        # Define a time delta of 4 hours
        time_threshold = datetime.timedelta(hours=4)

        # Iterate through files in the "cache" folder
        for filename in os.listdir(cache_folder):
            file_path = os.path.join(cache_folder, filename)

            # Check if the path is a file (not a subdirectory)
            if os.path.isfile(file_path):
                # Get the modification time of the file
                modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                # Calculate the time difference
                time_difference = current_time - modification_time

                # If the file was modified more 4 hours ago then delete it
                if time_difference > time_threshold:
                    os.remove(file_path)


first_page()
