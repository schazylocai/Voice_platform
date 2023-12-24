import streamlit as st
import os
import datetime

from src.Intro_page import write_english_About
from src.Change_Text_Style import change_text_style_english

from dotenv import load_dotenv
from src.stripe_functions_english import check_customers_eng, subscribe_to_service_eng, cancel_service_eng, \
    forgot_password_eng
from src.sessions import initialize_params

load_dotenv()  # read local .env file

tenant_id = os.getenv("AZURE_TENANT_ID", "default-tenant-id")
open_ai = os.getenv("OPENAI_API_KEY")

LANGCHAIN_TRACING_V2 = os.environ['LANGCHAIN_TRACING_V2']
LANGCHAIN_ENDPOINT = os.environ['LANGCHAIN_ENDPOINT']
LANGCHAIN_API_KEY = os.environ['LANGCHAIN_API_KEY']
LANGCHAIN_PROJECT = os.environ['LANGCHAIN_PROJECT']

st.set_page_config(layout="wide", initial_sidebar_state='expanded', page_icon="🔬", page_title='GPT Document Analyzer')
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

# status = False
valid_email = False
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


# Function to initialize the session
def init_session():
    initialize_params()
    # Initialize other session-specific data
    st.session_state['data'] = {}


def change_language_to_English():
    col1, col2 = st.columns(2)

    with col1:
        change_text_style_english("GPT Analyzer", 'title', red)
        st.write('')

    st.divider()
    write_english_About()

    st.session_state.subscribed_status = check_customers_eng()
    subscribe_to_service_eng()
    cancel_service_eng()
    forgot_password_eng()


def first_page():
    init_session()
    st.session_state['data']['clicked'] = True
    # print('Session Key:', st.session_state['session_key'])
    # print('Session Data:', st.session_state['data'])

    change_language_to_English()
    cache_folder = "cache"

    # Check if the cache folder exists
    if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
        # Get the current time_
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
