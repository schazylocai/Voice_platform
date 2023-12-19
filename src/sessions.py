import streamlit as st
import uuid
import pandas as pd


def initialize_params():
    ##################### Define LLM Model ####################

    llm_model = 'gpt-4-1106-preview'  # gpt-4 or gpt-3.5-turbo or gpt-3.5-turbo-16k or gpt-4-1106-preview

    ################### Set default states ###################

    st.session_state.setdefault("language", 'English')
    st.session_state.setdefault("user_status", 'False')

    ################### Set app session states ###################

    if 'language' not in st.session_state:
        st.session_state.language = 'English'

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'ChatOpenAI' not in st.session_state:
        st.session_state.ChatOpenAI = llm_model

    if 'session_key' not in st.session_state:
        st.session_state['session_key'] = str(uuid.uuid4())

    ################### Set GPT Doc session states ###################

    if 'gpt_doc_file_text_list_eng' not in st.session_state:
        st.session_state.gpt_doc_file_text_list_eng = []

    if 'gpt_doc_messages_files_eng' not in st.session_state:
        st.session_state.gpt_doc_messages_files_eng = []

    if 'gpt_doc_chat_history_files_eng' not in st.session_state:
        st.session_state.gpt_doc_chat_history_files_eng = []

    if 'gpt_doc_file_to_upload_1_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_1_eng = None

    if 'gpt_doc_file_to_upload_2_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_2_eng = None

    if 'gpt_doc_file_to_upload_3_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_3_eng = None

    if 'gpt_doc_file_to_upload_list_1_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_list_1_eng = []

    if 'gpt_doc_file_to_upload_list_2_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_list_2_eng = []

    if 'gpt_doc_file_to_upload_list_3_eng' not in st.session_state:
        st.session_state.gpt_doc_file_to_upload_list_3_eng = []

    if 'gpt_doc_continue_analysis_files_eng' not in st.session_state:
        st.session_state.gpt_doc_continue_analysis_files_eng = False

    ######################################### Set GPT Excel session states #########################################

    if 'gpt_excel_messages_eng' not in st.session_state:
        st.session_state.gpt_excel_messages_eng = []

    if 'gpt_excel_chat_history_eng' not in st.session_state:
        st.session_state.gpt_excel_chat_history_eng = []

    if 'gpt_excel_sheets_frame_eng' not in st.session_state:
        st.session_state.gpt_excel_sheets_frame_eng = pd.DataFrame()

    if 'gpt_excel_sheets_frame_eng_adjusted' not in st.session_state:
        st.session_state.gpt_excel_sheets_frame_eng_adjusted = pd.DataFrame()

    if 'gpt_excel_continue_analysis_eng' not in st.session_state:
        st.session_state.gpt_excel_continue_analysis_eng = False

    if 'gpt_excel_header_row_index' not in st.session_state:
        st.session_state.gpt_excel_header_row_index = 0

    if 'gpt_excel_file_in_memory' not in st.session_state:
        st.session_state.gpt_excel_file_in_memory = 0

    if 'gpt_excel_file_to_upload' not in st.session_state:
        st.session_state.gpt_excel_file_to_upload = None

    if 'gpt_excel_output_dataframe' not in st.session_state:
        st.session_state.gpt_excel_output_dataframe = None

    if 'gpt_excel_output_chart' not in st.session_state:
        st.session_state.gpt_excel_output_chart = None

    ######################################### Set GPT Web session states #########################################

    if 'gpt_web_messages_weblinks_eng' not in st.session_state:
        st.session_state.gpt_web_messages_weblinks_eng = []

    if 'gpt_web_chat_history_weblinks_eng' not in st.session_state:
        st.session_state.gpt_web_chat_history_weblinks_eng = []

    if 'gpt_web_weblink_1_eng' not in st.session_state:
        st.session_state.gpt_web_weblink_1_eng = ''

    if 'gpt_web_text_list_1_eng' not in st.session_state:
        st.session_state.gpt_web_text_list_1_eng = []

    if 'gpt_web_continue_analysis_weblink_eng' not in st.session_state:
        st.session_state.gpt_web_continue_analysis_weblink_eng = False

    ######################################### Set GPT Youtube session states #########################################

    if 'gpt_youtube_messages_eng' not in st.session_state:
        st.session_state.gpt_youtube_messages_eng = []

    if 'gpt_youtube_chat_history_eng' not in st.session_state:
        st.session_state.gpt_youtube_chat_history_eng = []

    if 'gpt_youtube_video_link_eng' not in st.session_state:
        st.session_state.gpt_youtube_video_link_eng = []

    if 'gpt_youtube_content_eng' not in st.session_state:
        st.session_state.gpt_youtube_content_eng = []

    if 'gpt_youtube_continue_analysis_eng' not in st.session_state:
        st.session_state.gpt_youtube_continue_analysis_eng = False
