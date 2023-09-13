# !pip install yt_dlp
# !pip install pydub
# !pip install librosa
# !pip install youtube-transcript-api
# pip install pytube

import requests
import re
import streamlit as st
import os
from dotenv import load_dotenv
import stripe

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import SKLearnVectorStore
from langchain.document_loaders import YoutubeLoader
from youtube_transcript_api import YouTubeTranscriptApi
from src.Change_Text_Style import change_text_style_arabic, change_text_style_arabic_side

load_dotenv()  # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

max_files = 5
final_result = {"query": "", "answer": ""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def launch_youtube_app_ara():
    ######################################### Set session states #########################################

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'messages_youtube_ara' not in st.session_state:
        st.session_state.messages_youtube_ara = []

    if 'chat_history_youtube_ara' not in st.session_state:
        st.session_state.chat_history_youtube_ara = []

    if 'youtube_video_link_ara' not in st.session_state:
        st.session_state.youtube_video_link_ara = []

    if 'youtube_content_ara' not in st.session_state:
        st.session_state.youtube_content_ara = []

    if 'continue_analysis_youtube_ara' not in st.session_state:
        st.session_state.continue_analysis_youtube_ara = False

    ########################################### Set variables ##########################################

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col2:
            change_text_style_arabic(
                (
                            "لم يمكن تحميل الملف. يحتوي الرابط" + " " + file_name + " " + ".على بعض الشوائب!" + " " + "يرجى حذفه."),
                'subhead', red)
        return False

    ######################################### Clear all files #########################################
    def clear_all_files():
        st.empty()
        st.session_state.messages_youtube_ara = []
        st.session_state.chat_history_youtube_ara = []
        st.session_state.youtube_content_ara = []
        st.session_state.continue_analysis_youtube_ara = False
        st.session_state.youtube_video_link_ara = []

    ############################### Check web links and read their content ###############################
    def is_web_link_ara(web_link):
        # Define a regular expression pattern for a basic URL
        url_pattern = re.compile(r'https?://\S+')

        # Use the findall() method to search for URLs in the text
        url = re.findall(url_pattern, web_link)

        # If any URLs are found
        if len(url) > 0:
            url_check = url[0]
            url_parse = url
            try:
                response = requests.get(url_check)
                if response.status_code == 200:
                    try:
                        loader = YoutubeLoader.from_youtube_url(url_check, add_video_info=True)
                        result = loader.load()
                        result_id = f"وجدنا ڤيديو من: {result[0].metadata['author']}, وطوله: {result[0].metadata['length']} ثواني."
                        change_text_style_arabic(result_id, 'text_violet', violet)
                        result = result[0].page_content
                        result = result.lower()
                        result = f'Youtube video: {url} ======> {result}'

                        if result:
                            return result
                        change_text_style_arabic("لم يمكن استخراج أي معلومات من هذا الموقع", 'text_red', red)
                        return []

                    except Exception as e:
                        return []

                else:
                    change_text_style_arabic(
                        f"هذا الموقع: {url}, لم يمنحنا إذنًا للوصول إليه.",
                        'text_red',
                        red,
                    )
                return []

            except requests.exceptions.RequestException:
                change_text_style_arabic_side("هذا الرابط غير صالح", 'subhead_side_red', red)
                return []

        else:
            change_text_style_arabic_side("هذا الرابط غير صالح", 'subhead_side_red', red)
            return []

    ######################################### Compose layout #########################################
    col1, col2 = st.columns(2)

    with col2:
        change_text_style_arabic(("محلل المستندات"), 'title', red)
        change_text_style_arabic("من موقع يوتيوب", 'title', red)

        change_text_style_arabic_side(
            "يرجى نسخ الرابط *** https *** من موقع يوتيوب وكتابته هنا",
            'text_violet_side_tight_medium', violet)
        youtube_link = st.sidebar.text_input(label=':violet[رابط يوتيوب]', key='youtube_1_ara',
                                             help='نموزج: https://www.youtube.com/watch?v=fw2W1lUIdgQ')
        youtube_button = st.sidebar.button(label=':violet[قم بتحميل الرابط الإلكتروني]',
                                           use_container_width=True,
                                           key='web_s_1_ara')
        if youtube_button:
            st.write('')
            st.write('')
            change_text_style_arabic(f'{youtube_link} :الرابط', 'text_violet', violet)
            youtube_content = is_web_link_ara(youtube_link)
            st.session_state.youtube_content_ara = youtube_content
            st.session_state.youtube_video_link_ara = youtube_link

    with col1:

        ################################# set clear button #################################
        # set the clear button
        st.write("")
        st.write("")
        clear = st.button(':white[مسح المحادثة والذاكرة]', key='clear', use_container_width=True)

        if clear:
            clear_all_files()

        ################################# load youtube link #################################
        if st.session_state.youtube_video_link_ara:
            st.video(st.session_state.youtube_video_link_ara)

        ################################## Create final text file to pass to LLM ##################################
        # with st.expander('النص المُستخرَج من الموقع الإلكتروني'):
        #     st.write(st.session_state.youtube_content_ara)

    st.divider()

    ####################################### Write chat history #######################################
    for message in st.session_state.messages_youtube_ara:
        with st.chat_message(message['role']):
            change_text_style_arabic(message['content'], 'main_text_white', 'white')

    ######################################### Run LLM sequence #########################################
    if st.session_state.youtube_content_ara:

        try:
            with st.spinner(text=":red[Please wait while we read the documents...]"):

                chunk_size = 1500
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                               length_function=len)
                youtube_chunks = text_splitter.split_text(st.session_state.youtube_content_ara)

                youtube_llm = ChatOpenAI(temperature=0.4, model=st.session_state.ChatOpenAI)  # gpt-4 or gpt-3.5-turbo
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(youtube_chunks, embedding=embedding)
                retriever = vector_store.as_retriever(search_kwargs={"k": 1})
                memory_weblinks = ConversationBufferMemory(memory_key="chat_history_youtube_ara", return_messages=True)
                st.session_state.continue_analysis_youtube_ara = True

        except Exception as e:
            st.subheader(":red[An error occurred. Please upload the web link again]")
            st.session_state.continue_analysis_youtube_ara = False
            # st.markdown(e)

        ################################### Youtube ##################################
        if st.session_state.continue_analysis_youtube_ara:

            # RetrievalQA from chain type ##########

            response_template = f"""
                • You will act as an Arabic professional and a researcher.
                • Your task is to reply only in Arabic even if the question is in another language.
                • Your task is to read through the Youtube video and its content.
                • If a user asks you about a specific video url, then look inside the given documents for "Video" url to reply to the user.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
                • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                • Always reply in a polite and professional manner.
                • If you don't know the answer to the question, then reply: "أنا لست واثقًا من الإجابة على هذا السؤال بسبب غياب بعض المعلومات. حاول تحديد السؤال بطريقة اخرى."
    
                Divide your answer when possible into paragraphs:
                • What is your answer to the question?
                • Add citations when possible from the document that supports the answer.

                {{context}}

                Question: {{question}}

                Answer:
                """

            prompt_weblinks = PromptTemplate(template=response_template, input_variables=["context", "question"])
            chain_type_kwargs = {'prompt': prompt_weblinks}
            query_model = RetrievalQA.from_chain_type(
                llm=youtube_llm,
                chain_type="stuff",
                memory=memory_weblinks,
                return_source_documents=False,
                retriever=retriever,
                chain_type_kwargs=chain_type_kwargs)

            def create_text_question():

                user_input = st.chat_input('...ابدأ المحادثة هنا',
                                           max_chars=500, key='chat_weblinks_ara')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.messages_youtube_ara.append({'role': 'user', 'content': user_input})

                    with st.spinner(
                            text=":red[...تم إرسال المحادثة. قد يستغرق ذلك حوالي دقيقة لتحليل المحتوى]"):
                        with st.chat_message('assistant'):
                            message_placeholder = st.empty()
                            all_results = ''
                            chat_history = st.session_state.chat_history_youtube_ara
                            result = query_model({"query": user_input, "chat_history_youtube_ara": chat_history})
                            user_query = result['query']
                            result = result['chat_history_youtube_ara'][1].content
                            st.session_state.chat_history_youtube_ara.append((user_query, result))
                            all_results += result
                            font_link = '<link href="https://fonts.googleapis.com/css2?family=Cairo+Play:wght@600;800' \
                                        '&display=swap" rel="stylesheet">'
                            font_family = "'Cairo Play', sans-serif"
                            message_placeholder.markdown(
                                f"""
                                    {font_link}
                                    <style>
                                        .bot_reply_text {{
                                            font-family: {font_family};
                                            font-size: 18px;
                                            color: 'white;
                                            text-align: right;
                                            line-height: 2;
                                            font-weight: 800;
                                        }}
                                    </style>
                                    <div class="bot_reply_text"><bdi>{all_results}</bdi></div>
                                    """, unsafe_allow_html=True)

                            st.session_state.messages_youtube_ara.append({'role': 'assistant', 'content': all_results})
                            return user_input, result, user_query

            create_text_question()

    else:
        st.empty()
