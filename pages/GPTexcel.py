import streamlit as st
from src.gptexcelapp_eng import launch_excel_app_eng
from src.Change_Text_Style import change_text_style_arabic

if 'mylanguage' not in st.session_state:
    st.session_state.mylanguage = 'English'

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

client_started = False
subscribed = False

st.set_page_config(layout="wide", initial_sidebar_state='expanded', page_icon="🔬", page_title='GPT Excel Engine ')

violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"

# Check if a user is subscribed to launch the GPTapp
# if "subscribed_status" in st.session_state:
subscribed_user = False
subscribed_user = st.session_state.user_status

if st.session_state.mylanguage == 'English':

    if subscribed_user == 'True':
        launch_excel_app_eng()
        client_started = True
    else:
        st.header(':red[Subscription is not valid!]')
        st.subheader(':violet[Please Login or Subscribe in the About page.]')