# !pip install yt_dlp
# !pip install pydub
# !pip install librosa
# !pip install youtube-transcript-api
# pip install pytube

import os
import re

import requests
import streamlit as st
import stripe
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import YoutubeLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SKLearnVectorStore
from langchain.storage import InMemoryStore

from src.Change_Text_Style import change_text_style_english

load_dotenv('.env')  # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

if 'language' not in st.session_state:
    st.session_state.language = 'English'

max_files = 5
final_result = {"query": "", "answer": ""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def launch_youtube_app_eng():
    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col1:
            st.subheader(f":red[File {file_name} couldn't be loaded. The link has some irregularities! Please remove "
                         f" it to proceed.]")
        return False

    ######################################### Clear all files #########################################
    # def clear_all_files():
    #     st.empty()
    #     st.session_state.gpt_youtube_messages_eng = []
    #     st.session_state.gpt_youtube_chat_history_eng = []
    #     st.session_state.gpt_youtube_content_eng = []
    #     st.session_state.gpt_youtube_continue_analysis_eng = False
    #     st.session_state.gpt_youtube_video_link_eng = []

    ############################### Check youtube links and read their content ###############################
    def is_youtube_link_eng(web_link):
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
                        result_id = f":violet[Found a video from: {result[0].metadata['author']}, that is: {result[0].metadata['length']} seconds long]"
                        st.write(result_id)
                        result = result[0].page_content
                        result = result.lower()
                        result = f'Youtube video: {url} ======> {result}'

                        if result:
                            return result

                    except Exception as e:
                        st.subheader(f':red[No transcription found for the video on Youtube.]')
                        # st.markdown(e)
                        return []
                        # try:
                        #     with st.spinner('No transcribtion found for the video on Youtube. Transcribing video. This might take a few minutes depending on the size and the length of the video...'):
                        #         loader = GenericLoader(YoutubeAudioLoader([url_check],
                        #                                                   save_dir='cache'),
                        #                                OpenAIWhisperParser())
                        #         docs = loader.load()
                        #         combined_docs = [doc.page_content for doc in docs]
                        #         result = " ".join(combined_docs)
                        #
                        #         result = result.lower()
                        #         result = f'Youtube video: {url} ======> {result}'
                        #
                        #         if result:
                        #             return result
                        #         else:
                        #             st.write('no result')
                        #
                        # except Exception as e:
                        #     # st.write(e)
                        #     return []

                else:
                    st.subheader(
                        f":red[This video: {url} can't be accessed...")
                return []

            except requests.exceptions.RequestException:
                st.sidebar.subheader(':red[Not a valid weblink!]')
                return []

        else:
            st.sidebar.subheader(':red[Not a valid weblink!]')
            return []

    ######################################### Compose layout #########################################
    col1, col2 = st.columns(2)

    with col1:
        st.title(":red[GPT Youtube Analyzer]")
        st.write(f":red[Attention:]")
        st.write(f":violet[* Only English videos are supported...]")
        st.write(f":violet[* Youtube shorts can't be played...]")

        st.sidebar.subheader(
            ':violet[Please copy the :red[https] youtube link from your browser and paste it here]')
        youtube_link = st.sidebar.text_input(label=':violet[youtube link]', key='youtube_1_eng',
                                             help='Example: https://www.youtube.com/watch?v=fw2W1lUIdgQ')
        youtube_button = st.sidebar.button(label=':violet[Upload youtube link]',
                                           use_container_width=True,
                                           key='youtube_s_1_eng')
        if youtube_button:
            st.write('')
            st.write('')
            st.write(f':violet[youtube link: {youtube_link}]')
            youtube_content = is_youtube_link_eng(youtube_link)
            if len(youtube_content) > 0:
                st.session_state.gpt_youtube_content_eng = youtube_content
                st.session_state.gpt_youtube_video_link_eng = youtube_link

        with col2:

            ################################# set clear button #################################
            # st.write("")
            # st.write("")
            # clear = st.button(':white[Clear conversation & memory]', key='clear', use_container_width=True)
            #
            # if clear:
            #     clear_all_files()

            ################################# load youtube link #################################
            # Always display the video if there's a link in the session state
            if st.session_state.gpt_youtube_video_link_eng :
                st.video(st.session_state.gpt_youtube_video_link_eng)

        ################################## Create final text file to pass to LLM ##################################
        # with st.expander('Retrieved text from the YouTube link'):
        #     st.write(st.session_state.gpt_youtube_content_eng)

    st.divider()

    ####################################### Write chat history #######################################
    for message in st.session_state.gpt_youtube_messages_eng:
        with st.chat_message(message['role']):
            change_text_style_english(message['content'], 'main_text_white', 'white')

    ######################################## Run LLM sequence #########################################
    if st.session_state.gpt_youtube_content_eng:

        try:
            with st.spinner(text=":red[Please wait while we read the document...]"):

                chunk_size = 1000
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                               length_function=len)
                youtube_chunks = text_splitter.split_text(st.session_state.gpt_youtube_content_eng)

                youtube_llm = ChatOpenAI(temperature=0.5, model=st.session_state.ChatOpenAI)
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(youtube_chunks, embedding=embedding,
                                                             persist_path=None)

                st.session_state.gpt_youtube_continue_analysis_eng = True

        except Exception as e:
            st.subheader(":red[An error occurred. Please upload the youtube link again]")
            st.session_state.gpt_youtube_continue_analysis_eng = False
            # st.markdown(e)

        ################################## Youtube ##################################
        if st.session_state.gpt_youtube_continue_analysis_eng:

            ##################################### RetrievalQA from chain type #####################################

            response_template = """
                • You will act as an English professional and a researcher.
                • Your task is to reply only in English even if the question is in another language.
                • Your task is to read through the Youtube video and its content.
                • If a user asks you about a specific video url, then look inside the given documents for "Video" url
                  to reply to the user.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • Before giving your answer, you should look through all the documents in the provided text.
                • Always keep the History of the chat in your memory from the text stored in the variable chat_history
                • If the user asks about a previous question, then you can look into the history using the text
                  stored in the variable chat_history.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation
                  marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do you
                  think it is biased.
                • If you suspect incorrect or misleading information in the answer, then highlight the concerned
                  sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or
                  paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                • Always reply in a polite and professional manner.

                Divide your answer when possible into paragraphs:
                • What is your answer to the question?

                <ctx>
                {context}
                </ctx>
                --------
                <hs>
                {history}
                </hs>
                --------
                {question}
                Answer:
                """

            prompt_youtube = PromptTemplate(template=response_template,
                                            input_variables=["history", "context", "question"])

            store = InMemoryStore()
            # vector_store.persist()

            def execute_model(user_input, k):

                retriever = vector_store.as_retriever(search_kwargs={"k": k}, docstore=store)

                query_model = RetrievalQA.from_chain_type(
                    llm=youtube_llm,
                    chain_type="stuff",
                    return_source_documents=False,
                    retriever=retriever,
                    chain_type_kwargs={"verbose": False,
                                       "prompt": prompt_youtube,
                                       "memory": ConversationBufferMemory(memory_key="history",
                                                                          input_key="question",
                                                                          return_messages=True)})

                result = query_model({"query": user_input})

                return result

            def create_text_question():

                user_input = st.chat_input('Start querying the video here...',
                                           max_chars=500, key='chat_youtube_eng')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.gpt_youtube_messages_eng.append({'role': 'user', 'content': user_input})

                    with st.spinner(
                            text=":red[Query submitted. This may take a minute while we query the content...]"):
                        with st.chat_message('assistant'):
                            try:
                                message_placeholder = st.empty()
                                all_results = ''
                                chat_history = st.session_state.gpt_youtube_chat_history_eng

                                user_query = None
                                result = None

                                for k in range(3, 0, -1):
                                    try:
                                        result = execute_model(user_input, k=k)
                                        user_query = result['query']
                                        result = result['result']
                                        break
                                    except Exception as e:
                                        pass

                                st.session_state.gpt_youtube_chat_history_eng.append((user_query, result))
                                all_results += result
                                font_link_eng = '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">'
                                font_family_eng = "'Roboto', sans-serif"
                                message_placeholder.markdown(
                                    f"""
                                        {font_link_eng}
                                        <style>
                                            .bold-text {{
                                                font-family: {font_family_eng};
                                                font-size: 22px;
                                                color: 'white;
                                                text-align: left;
                                                line-height: 1.8;
                                                font-weight: 400;
                                            }}
                                        </style>
                                        <div class="bold-text"><bdi>{all_results}</bdi></div>
                                        """, unsafe_allow_html=True)

                                st.session_state.gpt_youtube_messages_eng.append({'role': 'assistant', 'content': all_results})
                                return user_input, result, user_query

                            except Exception as e:
                                st.write(":red[Couldn't process the request. Please try again!]")
                                st.write(e)

            create_text_question()

    else:
        st.empty()
