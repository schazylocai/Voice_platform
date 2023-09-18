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
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
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


def launch_web_app_ara():
    ######################################### Set session states #########################################

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'messages_weblinks_ara' not in st.session_state:
        st.session_state.messages_weblinks_ara = []

    if 'chat_history_weblinks_ara' not in st.session_state:
        st.session_state.chat_history_weblinks_ara = []

    if 'weblink_1_ara' not in st.session_state:
        st.session_state.weblink_1_ara = ''

    if 'web_text_list_1_ara' not in st.session_state:
        st.session_state.web_text_list_1_ara = []

    if 'continue_analysis_weblink_ara' not in st.session_state:
        st.session_state.continue_analysis_weblink_ara = False

    ########################################### Set variables ##########################################

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col1:
            change_text_style_arabic(
                ("لم يمكن تحميل الملف. يحتوي الملف" + " " + file_name + " " + ".على بعض الشوائب!" + " " + "يرجى حذفه."),
                'subhead', red)
        return False

    ######################################### Clear all files #########################################
    def clear_all_files():
        st.empty()
        st.session_state.chat_history_weblinks_ara = []
        st.session_state.messages_weblinks_ara = []
        st.session_state.weblink_1_ara = ''
        st.session_state.web_text_list_1_ara = []
        st.session_state.continue_analysis_weblink_ara = False

    ############################### Check web links and read their content ###############################
    def is_web_link(web_link):
        # Define a regular expression pattern for a basic URL
        url_pattern = re.compile(r'https?://\S+')

        # Use the findall() method to search for URLs in the text
        url = re.findall(url_pattern, web_link)

        # If any URLs are found
        if len(url) > 0:
            url = url[0]
            try:
                response = requests.get(url)
                robots_url = f'{url}/robots.txt'
                robot_response = requests.get(robots_url)
                if response.status_code == 200:
                    try:
                        # Load HTML
                        loader = AsyncHtmlLoader(url)
                        html = loader.load()
                        # Transform
                        bs_transformer = BeautifulSoupTransformer()
                        docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["div"])
                        # Result
                        pattern = r'([A-Z])'
                        result = docs_transformed[0].page_content
                        result = re.sub(pattern, r' \1', result)
                        result = result.lower()
                        result = f'Website {url} ======> {result}'
                        if len(result) > 0:
                            return result

                        change_text_style_arabic("لم يمكن استخراج أي معلومات من هذا الموقع", 'text_red', red)
                        return []

                    except Exception as e:
                        return []

                else:
                    change_text_style_arabic("هذا الموقع: " + f"{url}, " + "لم يمنحنا إذنًا للوصول إليه.",
                                             'text_red', red)
                    change_text_style_arabic("الاستجابة:" + f" {response.status_code} - " + "استجابة الروبوت:"
                                             + f" {robot_response.status_code}",
                                             'text_red', red)
                return []

            except requests.exceptions.RequestException:
                change_text_style_arabic_side("هذا الرابط غير صالح", 'subhead_side_red', red)
                return []

        else:
            change_text_style_arabic_side("هذا الرابط غير صالح", 'subhead_side_red', red)
            return []

    ######################################### Compose layout #########################################
    col1, col2, col3 = st.columns(3)

    with col3:
        change_text_style_arabic(("محلل المحتوى"), 'title', red)
        change_text_style_arabic(("من مواقع الإنترنت"), 'title', red)

    with col2:
        ################################# load weblinks #################################
        st.write("")
        st.write("")
        change_text_style_arabic("يرجى أخذ الإعتبار أن بعض المواقع لا تسمح بالوصول إلى محتواها.",
                                 'text_violet', violet)

        change_text_style_arabic_side(
            "يرجى نسخ الرابط *** http *** أو *** https *** من متصفح الإنترنت الخاص بك وكتابته هنا",
            'text_violet_side_tight_medium', violet)
        st.sidebar.write("")
        web_1 = st.sidebar.text_input(label=':violet[رابط الإنترنت]', key='web_1_ara',
                                      help="نموزج: https://www.worldwildlife.org/")
        weblink_button_1 = st.sidebar.button(label=':violet[قم بتحميل الرابط الإلكتروني]',
                                             use_container_width=True,
                                             key='web_s_1_ara')
        if weblink_button_1 and web_1:
            st.session_state.web_text_list_1_ara = web_1
            change_text_style_arabic(
                f"{web_1} :الرابط", 'text_violet', violet)
            st.session_state.weblink_1_ara = is_web_link(web_1)

    with col1:
        # set the clear button
        st.write("")
        st.write("")
        clear = st.button(':white[مسح المحادثة والذاكرة]', key='clear', use_container_width=True)

        if clear:
            clear_all_files()

    #################################### Create final text file to pass to LLM ####################################
    st.divider()

    if st.session_state.weblink_1_ara:
        with st.expander('النص المُستخرَج من الموقع الإلكتروني'):
            st.write(st.session_state.weblink_1_ara)

    st.divider()

    ####################################### Write chat history #######################################
    for message in st.session_state.messages_weblinks_ara:
        with st.chat_message(message['role']):
            change_text_style_arabic(message['content'], 'main_text_white', 'white')

    ######################################### Run LLM sequence #########################################
    if st.session_state.weblink_1_ara:

        try:
            with st.spinner(text=":red[Please wait while we read the documents...]"):

                chunk_size = 1500
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                               length_function=len)
                chunks = text_splitter.split_text(text=str(st.session_state.weblink_1_ara))
                chunks = list(chunks)

                llm = ChatOpenAI(temperature=0.6, model=st.session_state.ChatOpenAI)  # gpt-4 or gpt-3.5-turbo
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=embedding,
                                                             persist_path=None)
                # vector_store.persist()
                retriever = vector_store.as_retriever(search_kwargs={"k": 4})
                st.session_state.continue_analysis_weblink_ara = True

        except Exception as e:
            st.subheader(":red[حدث خطأ. يرجى إعادة تحميل الموقع من جديد]")
            st.session_state.continue_analysis_weblink_ara = False
            # st.markdown(e)

        ################################### weblinks ##################################
        if st.session_state.continue_analysis_weblink_ara:

            ##################################### RetrievalQA from chain type #####################################

            response_template = """
                • You will act as an Arabic professional and a researcher.
                • Your task is to reply only in Arabic even if the question is in another language.
                • Your task is to read through the websites.
                • If a user asks you about a specific website url, then look inside the given documents for "Website"
                  url to reply to the user.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • Before giving your answer, you should look through all the documents in the provided text.
                • Always keep the History of the chat in your memory from the text stored in the variable chat_history
                • If the user asks about a previous question, then you can look into the history using the text
                  stored in the variable chat_history.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation
                  marks and write: "It is highly likly that this sentence or paragrph is biased".
                  Explain why do yuo think it is biased.
                • If you suspect incorrect or misleading information in the answer, then highlight the concerned
                  sentence or paragraph in quotation marks and write: "It is highly likly that this sentence
                  or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                • Always reply in a polite and professional manner.
                • If you don't know the answer to the question, then reply:
                  "أنا لست واثقًا من الإجابة على هذا السؤال بسبب غياب بعض المعلومات. حاول تحديد السؤال بطريقة اخرى."
    
                Divide your answer when possible into paragraphs:
                • What is your answer to the question?
                • Add citations when possible from the document that supports the answer.
                • Add references when possible related to questions from the given documents only, in bullet points,
                  each one separately, at the end of your answer.

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

            prompt_weblinks = PromptTemplate(template=response_template,
                                             input_variables=["history", "context", "question"])

            query_model = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                return_source_documents=False,
                retriever=retriever,
                chain_type_kwargs={"verbose": False,
                                   "prompt": prompt_weblinks,
                                   "memory": ConversationBufferMemory(memory_key="history",
                                                                      input_key="question",
                                                                      return_messages=True)})

            def create_text_question():

                user_input = st.chat_input('...ابدأ المحادثة هنا',
                                           max_chars=500, key='chat_weblinks_ara')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.messages_weblinks_ara.append({'role': 'user', 'content': user_input})

                    with st.spinner(
                            text=":red[...تم إرسال المحادثة. قد يستغرق ذلك حوالي دقيقة لتحليل المستندات]"):
                        with st.chat_message('assistant'):
                            message_placeholder = st.empty()
                            all_results = ''
                            chat_history = st.session_state.chat_history_weblinks_ara
                            result = query_model({"query": user_input})
                            user_query = result['query']
                            result = result['result']
                            st.session_state.chat_history_weblinks_ara.append((user_query, result))
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

                            st.session_state.messages_weblinks_ara.append({'role': 'assistant', 'content': all_results})
                            return user_input, result, user_query

            create_text_question()

    else:
        st.empty()
