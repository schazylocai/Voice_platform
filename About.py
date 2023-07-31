import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from src.English_Language import write_english_About
from src.Arabic_Language import write_Arabic_About
from src.Change_Text_Style import change_text_style_arabic,change_text_style_english

st.set_page_config(layout="wide",initial_sidebar_state='expanded',page_icon="🔬")
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
from src.stripe_functions_english import check_customers_eng,subscribe_to_service_eng,cancel_service_eng,forgot_password_eng
from src.stripe_functions_arabic import check_customers_ara,subscribe_to_service_ara,cancel_service_ara,forgot_password_ara

def first_page():
    status = False
    valid_email = False
    violet = "rgb(169, 131, 247)"
    red = "rgb(232,89,83)"

    def intro():

        col1, col2, col3 = st.columns(3)

        with col1:
            # blue, green, orange, red, violet.
            change_text_style_english("GPT Document Analyzer",'title',violet)
            st.write("")

        language = 'English'

        # with col3:
        #
        #     language = st.selectbox("/", options=('العربية','English'), label_visibility='hidden', key='language')

        if language == 'English':
            # with col3:
            #     change_text_style_arabic("🌏  اختر لغتك", 'head', violet)

            st.divider()
            write_english_About()

        elif language == 'العربية':
            with col3:
                change_text_style_english("🌏Choose your language", 'head', violet)

            st.divider()
            write_Arabic_About()

        return language

    # Run Intro
    language = intro()

    if language == 'English':
        st.session_state.subscribed_status = check_customers_eng()
        st.session_state.messages = []
        subscribe_to_service_eng()
        cancel_service_eng()
        forgot_password_eng()


    else:
        st.session_state.subscribed_status = check_customers_ara()
        st.session_state.messages = []
        subscribe_to_service_ara()
        cancel_service_ara()
        forgot_password_ara()


first_page()