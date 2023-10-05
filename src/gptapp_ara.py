import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2
import docx2txt
import textract
import tempfile

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import SKLearnVectorStore
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


def launch_app_ara():
    ######################################### Set session states #########################################

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'file_text_list_ara' not in st.session_state:
        st.session_state.file_text_list_ara = []

    if 'messages_files_ara' not in st.session_state:
        st.session_state.messages_files_ara = []

    if 'chat_history_files_ara' not in st.session_state:
        st.session_state.chat_history_files_ara = []

    if 'file_to_upload_1_ara' not in st.session_state:
        st.session_state.file_to_upload_1_ara = None

    if 'file_to_upload_2_ara' not in st.session_state:
        st.session_state.file_to_upload_2_ara = None

    if 'file_to_upload_3_ara' not in st.session_state:
        st.session_state.file_to_upload_3_ara = None

    if 'file_to_upload_list_1_ara' not in st.session_state:
        st.session_state.file_to_upload_list_1_ara = []

    if 'file_to_upload_list_2_ara' not in st.session_state:
        st.session_state.file_to_upload_list_2_ara = []

    if 'file_to_upload_list_3_ara' not in st.session_state:
        st.session_state.file_to_upload_list_3_ara = []

    if 'continue_analysis_files_ara' not in st.session_state:
        st.session_state.continue_analysis_files_ara = False

    ########################################### Set variables ##########################################
    st.session_state.file_text_list_ara = []

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col2:
            change_text_style_arabic(
                ("لم يمكن تحميل الملف. يحتوي الملف" + " " + file_name + " " + ".على بعض الشوائب!" + " " + "يرجى حذفه."),
                'subhead', 'red')
        return False

    ######################################### Clear all files #########################################
    def clear_all_files():
        st.empty()
        st.session_state.messages_files_ara = []
        st.session_state.chat_history_files_ara = []
        st.session_state.file_to_upload_1_ara = None
        st.session_state.file_to_upload_2_ara = None
        st.session_state.file_to_upload_3_ara = None
        st.session_state.file_to_upload_list_1_ara = []
        st.session_state.file_to_upload_list_2_ara = []
        st.session_state.file_to_upload_list_3_ara = []
        st.session_state.file_text_list_ara = []
        st.session_state.continue_analysis_files_ara = False

    #################################### Convert uploaded files to text ####################################
    def convert_file_to_text(my_file):
        text_list_return = []
        # Check if the upload file is a pdf
        try:
            if str(my_file.name).endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(my_file)
                text = "".join(page.extract_text() for page in pdf_reader.pages)
                if len(text) > 5:
                    text = text.replace("<|endofprompt|>", "")
                    text_list_return.append(f"File: {my_file.name}")
                    text_list_return.append(f"Document name: {my_file.name}")
                    text_list_return.append(f"Document title: {os.path.splitext(my_file.name)[0]}")
                    text_list_return.append(text)
                    return text_list_return

                else:
                    catch_exception(my_file.name)
                    return []

            # Check if the upload file is a Word docx
            elif str(my_file.name).endswith('.docx'):
                text = docx2txt.process(my_file)
                if len(text) > 5:
                    text_list_return.append(f"File: {my_file.name}")
                    text_list_return.append(f"Document name: {my_file.name}")
                    text_list_return.append(f"Document Title: {os.path.splitext(my_file.name)[0]}")
                    text_list_return.append(text)
                    return text_list_return

                else:
                    catch_exception(my_file.name)
                    return []

            # Check if the upload file is a text txt
            elif str(my_file.name).endswith('.txt'):
                with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                    tmp.write(my_file.read())
                    tmp.seek(0)
                    text = textract.process(tmp.name, method='txt')
                    if len(text) > 5:
                        text_list_return.append(f"File: {my_file.name}")
                        text_list_return.append(f"Document name: {my_file.name}")
                        text_list_return.append(f"Document title: {os.path.splitext(my_file.name)[0]}")
                        text_list_return.append(text.decode('utf-8'))
                        return text_list_return

                    else:
                        catch_exception(my_file.name)
                        return []

        except Exception as e:
            catch_exception(my_file.name)
            return []

    ######################################### Compose layout #########################################
    col1, col2, col3 = st.columns(3)

    with col3:
        change_text_style_arabic(("محلل المستندات"), 'title', red)

    with col2:
        ################################# load documents #################################
        max_retries = 3

        # upload file 1
        change_text_style_arabic_side(" حمل PDF, word, أو أي نص", 'text_violet_side_tight', violet)
        file_1 = st.sidebar.file_uploader(
            label=':violet[Select PDF, word, or text files to upload]',
            type=['pdf', 'docx', 'txt'],
            label_visibility='hidden',
            accept_multiple_files=False, key='file_1_ara')

        retry_count_1 = 0
        if file_1:
            while retry_count_1 < max_retries:
                try:
                    st.session_state.file_to_upload_list_1_ara = file_1
                    st.session_state.file_to_upload_1_ara = convert_file_to_text(file_1)
                    st.session_state.file_text_list_ara.append(file_1)
                    break

                except Exception as e:
                    retry_count_1 += 1
                    if retry_count_1 < max_retries:
                        continue
                    st.sidebar.write("تم الوصول إلى الحد الأقصى لمحاولات إعادة المحاولة. فشل التحميل")
                    break

        else:
            st.session_state.file_to_upload_1_ara = None

        # upload file 2
        change_text_style_arabic_side(" حمل PDF, word, أو أي نص", 'text_violet_side_tight', violet)
        file_2 = st.sidebar.file_uploader(
            label=':violet[Select PDF, word, or text files to upload]',
            type=['pdf', 'docx', 'txt'],
            label_visibility='hidden',
            accept_multiple_files=False, key='file_2_ara')

        retry_count_2 = 0
        if file_2:
            while retry_count_2 < max_retries:
                try:
                    st.session_state.file_to_upload_list_2_ara = file_2
                    st.session_state.file_to_upload_2_ara = convert_file_to_text(file_2)
                    st.session_state.file_text_list_ara.append(file_2)
                    break

                except Exception as e:
                    retry_count_2 += 1
                    if retry_count_2 < max_retries:
                        continue
                    st.sidebar.write("تم الوصول إلى الحد الأقصى لمحاولات إعادة المحاولة. فشل التحميل")
                    break

        else:
            st.session_state.file_to_upload_2_ara = None

        # upload file 3
        change_text_style_arabic_side(" حمل PDF, word, أو أي نص", 'text_violet_side_tight', violet)
        file_3 = st.sidebar.file_uploader(
            label=':violet[Select PDF, word, or text files to upload]',
            type=['pdf', 'docx', 'txt'],
            label_visibility='hidden',
            accept_multiple_files=False, key='file_3_ara')

        retry_count_3 = 0
        if file_3:
            while retry_count_3 < max_retries:
                try:
                    st.session_state.file_to_upload_list_3_ara = file_3
                    st.session_state.file_to_upload_3_ara = convert_file_to_text(file_3)
                    st.session_state.file_text_list_ara.append(file_3)
                    break

                except Exception as e:
                    retry_count_3 += 1
                    if retry_count_3 < max_retries:
                        continue
                    st.sidebar.write("تم الوصول إلى الحد الأقصى لمحاولات إعادة المحاولة. فشل التحميل")
                    break

        else:
            st.session_state.file_to_upload_3_ara = None

    with col1:
        # set the clear button
        st.write("")
        st.write("")
        clear = st.button(':white[مسح المحادثة والذاكرة]', key='clear', use_container_width=True)

        if clear:
            clear_all_files()

        # Loop through uploaded files
        n = 1
        if (st.session_state.file_to_upload_list_1_ara or st.session_state.file_to_upload_list_2_ara or st.session_state.file_to_upload_list_3_ara) and st.session_state.file_text_list_ara:
            for file in st.session_state.file_text_list_ara:
                if file:
                    st.write(f':violet[{file.name}:{n} الملف]')
                n += 1

    st.divider()

    #################################### Create final file to pass to LLM ####################################
    def create_final_text():

        if st.session_state.file_to_upload_1_ara or st.session_state.file_to_upload_2_ara or st.session_state.file_to_upload_3_ara:
            loop_through_files = [st.session_state.file_to_upload_1_ara,
                                  st.session_state.file_to_upload_2_ara,
                                  st.session_state.file_to_upload_3_ara]
            return loop_through_files
        else:
            loop_through_files = []
            return loop_through_files

    text_list = create_final_text()

    # st.write(text_list)

    ####################################### Write chat history #######################################
    for message in st.session_state.messages_files_ara:
        with st.chat_message(message['role']):
            change_text_style_arabic(message['content'], 'subhead', 'white')

    ######################################### Run LLM sequence #########################################
    if text_list:

        try:
            with st.spinner(text=":red[يرجى الانتظار بينما نقرء المستندات...]"):

                chunk_size = 1500
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                               length_function=len)
                chunks = text_splitter.split_text(text=str(text_list))
                chunks = list(chunks)

                llm = ChatOpenAI(temperature=0.6, model=st.session_state.ChatOpenAI)  # gpt-4 or gpt-3.5-turbo
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=embedding,
                                                             persist_path=None)
                # vector_store.persist()
                retriever = vector_store.as_retriever(search_kwargs={"k": 4})
                st.session_state.continue_analysis_files_ara = True

        except Exception as e:
            st.subheader(":red[حدث خطأ. يرجى حذف الملف المحمّل ثم إعادة تحميله مرة أخرى.]")
            st.session_state.continue_analysis_files_ara = False
            # st.markdown(e)

        #################################### documents ####################################
        if st.session_state.continue_analysis_files_ara:

            # RetrievalQA from chain type ##########

            response_template = """
                • You will act as an Arabic professional and a researcher.
                • Your task is to reply only in Arabic even if the question is in another language.
                • Your task is to read through research papers, documents, journals, manuals, and articles.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • Before giving your answer, you should look through all the documents in the provided text.
                • Always keep the History of the chat in your memory from the text stored in the variable chat_history
                • If the user asks about a previous question, then you can look into the history using the text
                  stored in the variable chat_history.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation
                  marks and write: "It is highly likly that this sentence or paragrph is biased".
                  Explain why do yuo think it is biased.
                • If you suspect incorrect or misleading information in the answer,
                  then highlight the concerned sentence or paragraph in quotation marks and write:
                  "It is highly likly that this sentence or paragrph is incorrect or misleading".
                  Explain why do yuo think it is incorrect or misleading.
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

            prompt_files = PromptTemplate(template=response_template,
                                          input_variables=["history", "context", "question"])

            query_model = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                return_source_documents=False,
                retriever=retriever,
                chain_type_kwargs={"verbose": False,
                                   "prompt": prompt_files,
                                   "memory": ConversationBufferMemory(memory_key="history",
                                                                      input_key="question",
                                                                      return_messages=True)})

            def create_text_question():

                user_input = st.chat_input('...ابدأ المحادثة هنا',
                                           max_chars=500, key='chat_files_ara')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.messages_files_ara.append({'role': 'user', 'content': user_input})

                    with st.spinner(
                            text=":red[...تم إرسال المحادثة. قد يستغرق ذلك حوالي دقيقة لتحليل المستندات]"):
                        with st.chat_message('assistant'):
                            message_placeholder = st.empty()
                            all_results = ''
                            chat_history = st.session_state.chat_history_files_ara
                            result = query_model({"query": user_input})
                            user_query = result['query']
                            result = result['result']
                            st.session_state.chat_history_files_ara.append((user_query, result))
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
                                            font-size: 22px;
                                            color: 'white;
                                            text-align: right;
                                            line-height: 2;
                                            font-weight: 800;
                                        }}
                                    </style>
                                    <div class="bot_reply_text"><bdi>{all_results}</bdi></div>
                                    """, unsafe_allow_html=True)

                            st.session_state.messages_files_ara.append({'role': 'assistant', 'content': all_results})
                            return user_input, result, user_query

            create_text_question()

    else:
        st.empty()
