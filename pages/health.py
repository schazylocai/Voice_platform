import streamlit as st
from src.Change_Text_Style import change_text_style_arabic

violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


if st.session_state.mylanguage == 'English':
    st.subheader(':red[No issues reported today!]')
    st.write(':violet[Please continue enjoying the app...]')
else:
    change_text_style_arabic("لا توجد مشاكل مُبلغ عنها اليوم", 'head', red)
    change_text_style_arabic("يرجى الاستمرار في التمتع بالتطبيق...", 'text_violet',violet)