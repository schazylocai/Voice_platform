import streamlit as st
from src.gptapp_eng import launch_app_eng
from src.gptapp_ara import launch_app_ara
from src.Change_Text_Style import change_text_style_arabic

client_started = False
subscribed = False

st.set_page_config(layout="wide",initial_sidebar_state='expanded',page_icon="🔬",page_title='GPT Engine')

violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"

mylanguage = 'English'

# Check if a user is subscribed to launch the GPTapp
if "subscribed_status" in st.session_state and not client_started:
    subscribed_user = st.session_state.subscribed_status

    # if st.session_state.mylanguage == 'English':
    if mylanguage == 'English':

        if subscribed_user:
            launch_app_eng()
            client_started = True
        else:
            st.header(':red[Subscription is not valid!]')
            st.subheader(':violet[Please Login or Subscribe in the About page.]')

    elif st.session_state.mylanguage == 'العربية':

        if subscribed_user:
            launch_app_ara()
            client_started = True
        else:
            change_text_style_arabic("الاشتراك غير ساري المفعول!", 'head', red)
            change_text_style_arabic("الرجاء تسجيل الدخول أو الاشتراك في الصفحة الرئيسية.", 'subhead', violet)