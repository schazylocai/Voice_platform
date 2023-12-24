import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2
import docx2txt
import textract
import tempfile
import smtplib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import SKLearnVectorStore
from src.Change_Text_Style import change_text_style_english
from langchain.storage import InMemoryStore

load_dotenv('.env')  # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

max_files = 5
final_result = {"question": "", "answer": ""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def launch_app_eng():
    ########################################### Set variables ##########################################
    st.session_state.gpt_doc_file_text_list_eng = []

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col2:
            st.subheader(f":red[File {file_name} couldn't be loaded. The file has some irregularities! Please remove "
                         f" it to proceed.]")
        return False

    ######################################### Clear all files #########################################
    # def clear_all_files():
    #     st.empty()
    #     st.session_state.gpt_doc_messages_files_eng = []
    #     st.session_state.gpt_doc_chat_history_files_eng = []
    #     st.session_state.gpt_doc_file_to_upload_1_eng = None
    #     st.session_state.gpt_doc_file_to_upload_2_eng = None
    #     st.session_state.gpt_doc_file_to_upload_3_eng = None
    #     st.session_state.gpt_doc_file_to_upload_list_1_eng = []
    #     st.session_state.gpt_doc_file_to_upload_list_2_eng = []
    #     st.session_state.gpt_doc_file_to_upload_list_3_eng = []
    #     st.session_state.gpt_doc_file_text_list_eng = []
    #     st.session_state.gpt_doc_continue_analysis_files_eng = False

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

    with col1:
        st.title(":red[GPT Document Analyzer]")

    with col2:
        ################################# upload file 1 #################################
        try:
            file_1 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_1_eng',
                label_visibility='hidden')

        except Exception as e:
            gpt_doc_send_email_error(e)

        if file_1:
            st.session_state.gpt_doc_file_to_upload_1_eng = file_1
            with st.session_state.gpt_doc_file_to_upload_1_eng:

                try:
                    st.session_state.gpt_doc_file_to_upload_1_eng = convert_file_to_text(file_1)
                    st.session_state.gpt_doc_file_text_list_eng.append(file_1)
                    st.session_state.gpt_doc_file_to_upload_list_1_eng = file_1.name

                except Exception as e:
                    st.sidebar.write("Sorry. An error occurred. Please try again.")

        else:
            st.session_state.gpt_doc_file_to_upload_1_eng = None

        ################################# upload file 2 #################################
        try:
            file_2 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_2_eng',
                label_visibility='hidden')

        except Exception as e:
            gpt_doc_send_email_error(e)

        if file_2:
            st.session_state.gpt_doc_file_to_upload_2_eng = file_2
            with st.session_state.gpt_doc_file_to_upload_2_eng:

                try:
                    st.session_state.gpt_doc_file_to_upload_2_eng = convert_file_to_text(file_2)
                    st.session_state.gpt_doc_file_text_list_eng.append(file_2)
                    st.session_state.gpt_doc_file_to_upload_list_2_eng = file_2.name

                except Exception as e:
                    st.sidebar.write("Sorry. An error occurred. Please try again.")

        else:
            st.session_state.gpt_doc_file_to_upload_2_eng = None

        ################################# upload file 3 #################################
        try:
            file_3 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_3_eng',
                label_visibility='hidden')

        except Exception as e:
            gpt_doc_send_email_error(e)

        if file_3:
            st.session_state.gpt_doc_file_to_upload_3_eng = file_3
            with st.session_state.gpt_doc_file_to_upload_3_eng:

                try:
                    st.session_state.gpt_doc_file_to_upload_3_eng = convert_file_to_text(file_3)
                    st.session_state.gpt_doc_file_text_list_eng.append(file_3)
                    st.session_state.gpt_doc_file_to_upload_list_3_eng = file_3.name

                except Exception as e:
                    st.sidebar.write("Sorry. An error occurred. Please try again.")

        else:
            st.session_state.gpt_doc_file_to_upload_3_eng = None

        # with col3:
        #     # set the clear button
        #     st.write("")
        #     st.write("")
        #     clear = st.button(':white[Clear conversation & memory]', key='clear', use_container_width=True)
        #
        #     if clear:
        #         clear_all_files()

        # Loop through uploaded files
        n = 1
        if (
                st.session_state.gpt_doc_file_to_upload_list_1_eng or st.session_state.gpt_doc_file_to_upload_list_2_eng or st.session_state.gpt_doc_file_to_upload_list_3_eng) and st.session_state.gpt_doc_file_text_list_eng:
            for file in st.session_state.gpt_doc_file_text_list_eng:
                if file:
                    st.write(f':violet[File {n}: {file.name}]')
                n += 1

    st.divider()

    ################################## Create final text file to pass to LLM ##################################
    def create_final_text():
        if st.session_state.gpt_doc_file_to_upload_1_eng or st.session_state.gpt_doc_file_to_upload_2_eng or st.session_state.gpt_doc_file_to_upload_3_eng:
            loop_through_files = [st.session_state.gpt_doc_file_to_upload_1_eng,
                                  st.session_state.gpt_doc_file_to_upload_2_eng,
                                  st.session_state.gpt_doc_file_to_upload_3_eng]
            return loop_through_files
        else:
            loop_through_files = []
            return loop_through_files

    text_list = create_final_text()

    # st.write(text_list)

    ####################################### Write chat history #######################################
    for message in st.session_state.gpt_doc_messages_files_eng:
        with st.chat_message(message['role']):
            change_text_style_english(message['content'], 'main_text_white', 'white')

    ######################################### Run LLM sequence #########################################
    if text_list:

        try:
            with st.spinner(text=":red[Please wait while we read the documents...]"):

                chunk_size = 1000
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50,
                                                               length_function=len)
                chunks = text_splitter.split_text(text=str(text_list))
                chunks = list(chunks)

                llm = ChatOpenAI(temperature=0.6, model=st.session_state.ChatOpenAI)
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=embedding,
                                                             persist_path=None)
                store = InMemoryStore()
                # vector_store.persist()
                retriever = vector_store.as_retriever(search_kwargs={"k": 3}, docstore=store)
                st.session_state.gpt_doc_continue_analysis_files_eng = True

        except Exception as e:
            st.subheader(":red[An error occurred. Please delete the uploaded file, and then uploaded it again]")
            st.session_state.gpt_doc_continue_analysis_files_eng = False
            st.markdown(e)

        #################################### documents ####################################
        if st.session_state.gpt_doc_continue_analysis_files_eng:

            # RetrievalQA from chain type ##########

            response_template = """
                • You will act as an English professional and a researcher.
                • Your task is to reply only in English even if the question is in another language.
                • Your task is to read through research papers, documents, journals, manuals, and articles.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • Before giving your answer, you should look through all the documents in the provided text.
                • Always keep the History of the chat in your memory from the text stored in the variable chat_history
                • If the user asks about a previous question, then you can look into the history using the text
                  stored in the variable chat_history.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation
                  marks and write: "It is highly likely that this sentence or paragraph is biased".
                  Explain why you think it is biased.
                • If you suspect incorrect or misleading information in the answer,
                  then highlight the concerned sentence or paragraph in quotation marks and write:
                  "It is highly likely that this sentence or paragraph is incorrect or misleading".
                  Explain why you think it is incorrect or misleading.
                • Always reply in a polite and professional manner.

                Divide your answer when possible into paragraphs:
                • What is your answer to the question?
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

                user_input = st.chat_input('Start querying the document here...',
                                           max_chars=500, key='chat_files_eng')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.gpt_doc_messages_files_eng.append({'role': 'user', 'content': user_input})

                    with st.spinner(
                            text=":red[Query submitted. This may take a minute while we query the documents...]"):
                        with st.chat_message('assistant'):
                            try:
                                message_placeholder = st.empty()
                                all_results = ''
                                chat_history = st.session_state.gpt_doc_chat_history_files_eng
                                result = query_model({"query": user_input})
                                user_query = result['query']
                                result = result['result']
                                st.session_state.gpt_doc_chat_history_files_eng.append((user_query, result))
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
                                                line-height: 2.2;
                                                font-weight: 400;
                                            }}
                                        </style>
                                        <div class="bold-text"><bdi>{all_results}</bdi></div>
                                        """, unsafe_allow_html=True)

                                st.session_state.gpt_doc_messages_files_eng.append(
                                    {'role': 'assistant', 'content': all_results})
                                return user_input, result, user_query

                            except Exception as e:
                                st.write(":red[Couldn't process the request. Please try again!]")
                                st.write(e)

            create_text_question()

    else:
        st.empty()


def gpt_doc_send_email_error(body):
    sender = 'GPT Doc'
    recipient = os.environ["MY_EMAIL_ADDRESS"]
    subject = 'Error message'
    sender_email = 'samuel'
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(recipient, os.environ["EMAIL_PASSWORD"])
        server.sendmail(sender, recipient, f"Subject: {subject}\n\n{sender}: {sender_email}\n\n{body}")