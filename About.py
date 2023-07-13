import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from English_Language import write_english_About
from Arabic_Language import write_Arabic_About

st.set_page_config(layout="wide",initial_sidebar_state='expanded',page_icon="🔬")
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
video_url = "https://youtu.be/PgXjVwHmqbg"
from stripe_functions import check_customers,subscribe_to_service,cancel_service

def first_page():
    status = False
    valid_email = False

    def intro():

        col1, col2, col3 = st.columns(3)

        with col1:
            # blue, green, orange, red, violet.
            st.title(":violet[GPT Document Analyzer]")
            st.write("")
            st.write("")
            st.write("")
            st.write("")

        # with col3:
        #     st.write("")
        #     st.subheader(":violet[Choose your language   🌎   اختر لغتك]")
        #     language = st.selectbox("Language", options=('English', 'العربية'), label_visibility='hidden', key='language')

        language = 'English'

        if language == 'English':
            write_english_About()

        elif language == 'العربية':
            write_Arabic_About()

    # Run Intro
    intro()


first_page()
st.session_state.subscribed_status = check_customers()
st.session_state.messages = []
subscribe_to_service()
cancel_service()