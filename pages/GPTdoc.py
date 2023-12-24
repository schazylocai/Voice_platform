import streamlit as st
from src.gptapp_eng import launch_app_eng

client_started = False
subscribed = False

st.set_page_config(layout="wide", initial_sidebar_state='expanded', page_icon="🔬", page_title='GPT Engine ')

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

if 'language' not in st.session_state:
    st.session_state.language = 'English'

violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"

# Check if a user is subscribed to launch the GPTapp
subscribed_user = st.session_state.user_status

if st.session_state.language == 'English':

    if subscribed_user == 'True':
        launch_app_eng()
        client_started = True
    else:
        st.header(':red[Subscription is not valid!]')
        st.subheader(':violet[Please Login or Subscribe in the About page.]')
