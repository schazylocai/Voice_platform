import requests
import re
import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2
import docx2txt
import textract
import tempfile
from tenacity import retry, stop_after_attempt, wait_random_exponential

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import SKLearnVectorStore
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer

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

llm_model = 'gpt-3.5-turbo'  # gpt-4 or gpt-3.5-turbo


def launch_app_eng():
    ######################################### Set session states #########################################

    st.session_state.setdefault(key='start')

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'ChatOpenAI' not in st.session_state:
        st.session_state.ChatOpenAI = llm_model

    if 'messages_files' not in st.session_state:
        st.session_state.messages_files = []

    if 'chat_history_files' not in st.session_state:
        st.session_state.chat_history_files = []

    if 'messages_weblinks' not in st.session_state:
        st.session_state.messages_weblinks = []

    if 'chat_history_weblinks' not in st.session_state:
        st.session_state.chat_history_weblinks = []

    if 'file_to_upload_1' not in st.session_state:
        st.session_state.file_to_upload_1 = None

    if 'file_to_upload_2' not in st.session_state:
        st.session_state.file_to_upload_2 = None

    if 'file_to_upload_3' not in st.session_state:
        st.session_state.file_to_upload_3 = None

    if 'file_to_upload_list_1' not in st.session_state:
        st.session_state.file_to_upload_list_1 = []

    if 'file_to_upload_list_2' not in st.session_state:
        st.session_state.file_to_upload_list_2 = []

    if 'file_to_upload_list_3' not in st.session_state:
        st.session_state.file_to_upload_list_3 = []

    if 'file_text_list' not in st.session_state:
        st.session_state.file_text_list = []

    if 'weblink_1' not in st.session_state:
        st.session_state.weblink_1 = ''

    if 'weblink_2' not in st.session_state:
        st.session_state.weblink_2 = ''

    if 'weblink_3' not in st.session_state:
        st.session_state.weblink_3 = ''

    if 'web_text_list_1' not in st.session_state:
        st.session_state.web_text_list_1 = []

    if 'web_text_list_2' not in st.session_state:
        st.session_state.web_text_list_2 = []

    if 'web_text_list_3' not in st.session_state:
        st.session_state.web_text_list_3 = []

    if 'web_text_list' not in st.session_state:
        st.session_state.web_text_list = []

    if 'function_choice' not in st.session_state:
        st.session_state.function_choice = 'Documents'

    if 'continue_analysis' not in st.session_state:
        st.session_state.continue_analysis = False

    ########################################### Set variables ##########################################

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col3:
            st.subheader(f":red[File {file_name} couldn't be loaded. The file has some irregularities! Please remove "
                         f" it to proceed.]")
        return False

    ######################################### Clear all files #########################################
    def clear_all_files():
        st.empty()
        st.session_state.messages_files = []
        st.session_state.chat_history_files = []
        st.session_state.messages_weblinks = []
        st.session_state.chat_history_weblinks = []
        st.session_state.web_text_list_1 = []
        st.session_state.web_text_list_2 = []
        st.session_state.web_text_list_3 = []
        st.session_state.weblink_1 = ''
        st.session_state.weblink_2 = ''
        st.session_state.weblink_3 = ''
        st.session_state.file_text_list = []
        st.session_state.file_to_upload_1 = None
        st.session_state.file_to_upload_2 = None
        st.session_state.file_to_upload_3 = None
        st.session_state.file_to_upload_list_1 = []
        st.session_state.file_to_upload_list_2 = []
        st.session_state.file_to_upload_list_3 = []
        st.session_state.web_text_list = []

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

                        st.subheader(":red[Couldn't extract any information from this website]")
                        st.session_state.weblink_1 = ''
                        st.session_state.weblink_2 = ''
                        st.session_state.weblink_3 = ''
                        return []

                    except Exception as e:
                        st.session_state.weblink_1 = ''
                        st.session_state.weblink_2 = ''
                        st.session_state.weblink_3 = ''
                        return []

                else:
                    st.subheader(
                        f":red[This website: {url} didn't give us permission to access it. Response:"
                        f"{response.status_code} - Robot response: {robot_response.status_code}]")
                    st.session_state.weblink_1 = ''
                    st.session_state.weblink_2 = ''
                    st.session_state.weblink_3 = ''
                return []

            except requests.exceptions.RequestException:
                st.sidebar.subheader(':red[Not a valid weblink!]')
                st.session_state.weblink_1 = ''
                st.session_state.weblink_2 = ''
                st.session_state.weblink_3 = ''
                return []

        else:
            st.sidebar.subheader(':red[Not a valid weblink!]')
            st.session_state.weblink_1 = ''
            st.session_state.weblink_2 = ''
            st.session_state.weblink_3 = ''
            return []

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
        st.title(":violet[GPT Document Analyzer]")

    with col2:
        st.write("")
        st.subheader(':violet[Choose between :red[Documents] or :red[Weblinks]]')
        st.write(':violet[Upload your files or weblinks from the left menu with the arrow.]')
        st.session_state.function_choice = st.selectbox(label='Select', options=(['Documents', 'Weblinks']),
                                                        label_visibility='hidden', key='choice_type_eng')

        ################################# If choice is documents #################################
        if st.session_state.function_choice == 'Documents':
            st.empty()
            st.session_state.web_text_list_1 = []
            st.session_state.web_text_list_2 = []
            st.session_state.web_text_list_3 = []
            st.session_state.weblink_1 = ''
            st.session_state.weblink_2 = ''
            st.session_state.weblink_3 = ''
            st.session_state.web_text_list = []

            file_1 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text'
                      'files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_1_eng',
                label_visibility='hidden')
            st.session_state.file_to_upload_1 = file_1 or None

            file_2 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_2_eng',
                label_visibility='hidden')
            st.session_state.file_to_upload_2 = file_2 or None

            file_3 = st.sidebar.file_uploader(
                label=':violet[Select PDF, word, or text files to upload]',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False, key='file_3_eng',
                label_visibility='hidden')
            st.session_state.file_to_upload_3 = file_3 or None

        ################################# If choice is weblinks #################################
        elif st.session_state.function_choice == 'Weblinks':
            st.empty()
            st.session_state.file_to_upload_1 = None
            st.session_state.file_to_upload_2 = None
            st.session_state.file_to_upload_3 = None
            st.session_state.file_to_upload_list_1 = []
            st.session_state.file_to_upload_list_2 = []
            st.session_state.file_to_upload_list_3 = []
            st.session_state.file_text_list = []

            st.sidebar.write(
                ':violet[Please copy the :red[http] or :red[https] link from your browser and paste it here]')
            st.session_state.weblink_1 = st.sidebar.text_input(label=':violet[weblink 1]', key='web_1_eng')
            weblink_button_1 = st.sidebar.button(label=':violet[Upload weblink]', use_container_width=True,
                                                 key='web_s_1_eng')
            st.session_state.weblink_2 = st.sidebar.text_input(label=':violet[weblink 2]', key='web_2_eng')
            weblink_button_2 = st.sidebar.button(label=':violet[Upload weblink]', use_container_width=True,
                                                 key='web_s_2_eng')
            st.session_state.weblink_3 = st.sidebar.text_input(label=':violet[weblink 3]', key='web_3_eng')
            weblink_button_3 = st.sidebar.button(label=':violet[Upload weblink]', use_container_width=True,
                                                 key='web_s_3_eng')

            if weblink_button_1 and st.session_state.weblink_1:
                st.session_state.web_text_list_1 = is_web_link(st.session_state.weblink_1)

            if weblink_button_2 and st.session_state.weblink_2:
                st.session_state.web_text_list_2 = is_web_link(st.session_state.weblink_2)

            if weblink_button_3 and st.session_state.weblink_3:
                st.session_state.web_text_list_3 = is_web_link(st.session_state.weblink_3)

            st.write(":violet[Be mindful that not all websites permit access to their content!]")

    with col3:
        # set the clear button
        st.write("")
        st.write("")
        clear = st.button(':white[Clear files & weblinks conversation & memory]', key='clear', use_container_width=True)

        if clear:
            clear_all_files()

        # Loop through uploaded files
        n = 1
        st.session_state.file_text_list = [st.session_state.file_to_upload_1, st.session_state.file_to_upload_2,
                                           st.session_state.file_to_upload_3]
        if st.session_state.file_to_upload_1 or st.session_state.file_to_upload_2 or st.session_state.file_to_upload_3:
            for file in st.session_state.file_text_list:
                if file:
                    st.write(f':violet[File {n}: {file.name}]')
                n += 1

        # Loop through the uploaded web links
        k = 1
        st.session_state.web_text_list = [st.session_state.weblink_1, st.session_state.weblink_2,
                                          st.session_state.weblink_3]
        if st.session_state.weblink_1 or st.session_state.weblink_2 or st.session_state.weblink_3:
            for link in st.session_state.web_text_list:
                st.write(f':violet[weblink {k}: {link}]')
                k += 1

    st.divider()

    #################################### Create final file to pass to LLM ####################################
    def create_final_text():

        # If choice is web links
        if st.session_state.function_choice == 'Weblinks':
            # Loop through web links
            st.session_state.web_text_list = [st.session_state.web_text_list_1, st.session_state.web_text_list_2,
                                              st.session_state.web_text_list_3]
            doc = ''
            for idx, text_web in enumerate(st.session_state.web_text_list):
                if text_web:
                    if idx == 0:
                        doc = st.session_state.weblink_1
                    elif idx == 1:
                        doc = st.session_state.weblink_2
                    elif idx == 2:
                        doc = st.session_state.weblink_3

                    with st.expander(f'Retrieved text from website {doc}'):
                        st.write(text_web)

        # If choice is documents
        elif st.session_state.function_choice == 'Documents':
            # Loop through files
            if st.session_state.file_to_upload_1 is not None:
                st.session_state.file_to_upload_list_1 = convert_file_to_text(st.session_state.file_to_upload_1)
            if st.session_state.file_to_upload_2 is not None:
                st.session_state.file_to_upload_list_2 = convert_file_to_text(st.session_state.file_to_upload_2)
            if st.session_state.file_to_upload_3 is not None:
                st.session_state.file_to_upload_list_3 = convert_file_to_text(st.session_state.file_to_upload_3)

            st.session_state.file_text_list = []
            if st.session_state.file_to_upload_1 is not None:
                st.session_state.file_text_list.append(st.session_state.file_to_upload_list_1)
            if st.session_state.file_to_upload_2 is not None:
                st.session_state.file_text_list.append(st.session_state.file_to_upload_list_2)
            if st.session_state.file_to_upload_3 is not None:
                st.session_state.file_text_list.append(st.session_state.file_to_upload_list_3)

            # for text_list_files in st.session_state.file_text_list:
            #     st.markdown(text_list_files)

    create_final_text()

    ####################################### Write chat history #######################################
    if st.session_state.function_choice == 'Documents':
        for message in st.session_state.messages_files:
            with st.chat_message(message['role']):
                st.subheader(message['content'])
    elif st.session_state.function_choice == 'Weblinks':
        for message in st.session_state.messages_weblinks:
            with st.chat_message(message['role']):
                st.subheader(message['content'])

    ######################################### Run LLM sequence #########################################
    text_list = "Waiting for user input..."

    if st.session_state.file_to_upload_1 or st.session_state.file_to_upload_2 or st.session_state.file_to_upload_3:
        text_list = st.session_state.file_text_list
    elif st.session_state.weblink_1 or st.session_state.weblink_2 or st.session_state.weblink_3:
        text_list = st.session_state.web_text_list

    if text_list:

        try:
            with st.spinner(text=":red[Please wait while we read the documents...]"):

                chunk_size = 1500
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                               length_function=len)
                chunks = text_splitter.split_text(text=str(text_list))
                chunks = list(chunks)

                llm = ChatOpenAI(temperature=0.4, model=st.session_state.ChatOpenAI)  # gpt-4 or gpt-3.5-turbo
                embedding = OpenAIEmbeddings()

                vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=embedding)
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                memory_files = ConversationBufferMemory(memory_key="chat_history_files", return_messages=True)
                memory_weblinks = ConversationBufferMemory(memory_key="chat_history_weblinks", return_messages=True)
                st.session_state.continue_analysis = True

        except Exception as e:
            st.subheader(":red[An error occurred. Please delete the uploaded file, and then uploaded it again]")
            st.session_state.continue_analysis = False
            # st.markdown(e)

        #################################### If choice is documents ####################################
        if text_list != "Waiting for user input...":
            if st.session_state.continue_analysis and st.session_state.function_choice == 'Documents':
                # RetrievalQA from chain type ##########

                response_template = f"""
                • You will act as an English professional and a researcher.
                • Your task is to reply only in English even if the question is in another language.
                • Your task is to read through research papers, documents, journals, manuals, articles, and presentations.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
                • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                • Always reply in a polite and professional manner.
                • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information! Please try to be more precise and accurate in your query."
    
                Divide your answer when possible into paragraphs:
                • What is your answer to the question?
                • Add citations when possible from the document that supports the answer.
                • Add references when possible related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.
    
                {{context}}
    
                Question: {{question}}
    
                Answer:
                """

                prompt_files = PromptTemplate(template=response_template, input_variables=["context", "question"])
                chain_type_kwargs = {'prompt': prompt_files}
                query_model = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    memory=memory_files,
                    return_source_documents=False,
                    retriever=retriever,
                    chain_type_kwargs=chain_type_kwargs,
                    verbose=False)

                @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
                def create_text_question():

                    user_input = st.chat_input('Start querying the document here...', max_chars=500,
                                               key='files_input_eng')
                    if user_input:
                        with st.chat_message('user'):
                            st.markdown(user_input)

                        st.session_state.messages_files.append({'role': 'user', 'content': user_input})

                        with st.spinner(
                                text=":red[Query submitted. This may take a minute while we query the documents...]"):
                            with st.chat_message('assistant'):
                                message_placeholder = st.empty()
                                all_results = ''
                                chat_history = st.session_state.chat_history_files
                                result = query_model({"query": user_input, "chat_history_files": chat_history})
                                user_query = result['query']
                                result = result['chat_history_files'][1].content
                                st.session_state.chat_history_files.append((user_query, result))
                                all_results += result
                                message_placeholder.subheader(f'{all_results}')

                                st.session_state.messages_files.append({'role': 'assistant', 'content': all_results})
                                return user_input, result, user_query

                create_text_question()

            ################################### If choice is weblinks ##################################
            elif st.session_state.continue_analysis and st.session_state.function_choice == 'Weblinks':
                # RetrievalQA from chain type ##########

                response_template = f"""
                    • You will act as an English professional and a researcher.
                    • Your task is to reply only in English even if the question is in another language.
                    • Your task is to read through the websites.
                    • If a user asks you about a specific website url, then look inside the given documents for "Website" url to reply to the user.
                    • You should be analytical, thoughtful, and reply in depth and details to any question.
                    • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
                    • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                    • Always reply in a polite and professional manner.
                    • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information! Please try to be more precise and accurate in your query."

                    Divide your answer when possible into paragraphs:
                    • What is your answer to the question?
                    • Add citations when possible from the document that supports the answer.
                    • Add references when possible related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.

                    {{context}}

                    Question: {{question}}

                    Answer:
                    """

                prompt_weblinks = PromptTemplate(template=response_template, input_variables=["context", "question"])
                chain_type_kwargs = {'prompt': prompt_weblinks}

                query_model = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    memory=memory_weblinks,
                    return_source_documents=False,
                    retriever=retriever,
                    chain_type_kwargs=chain_type_kwargs,
                    verbose=False)

                @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
                def create_text_question():

                    user_input = st.chat_input('Start querying the document here...', max_chars=500,
                                               key='weblinks_input_eng')
                    if user_input:
                        with st.chat_message('user'):
                            st.markdown(user_input)

                        st.session_state.messages_weblinks.append({'role': 'user', 'content': user_input})

                        with st.spinner(
                                text=":red[Query submitted. This may take a minute while we query the documents...]"):
                            with st.chat_message('assistant'):
                                message_placeholder = st.empty()
                                all_results = ''
                                chat_history = st.session_state.chat_history_weblinks
                                result = query_model({"query": user_input, "chat_history_weblinks": chat_history})
                                user_query = result['query']
                                result = result['chat_history_weblinks'][1].content
                                st.session_state.chat_history_weblinks.append((user_query, result))
                                all_results += result
                                message_placeholder.subheader(f'{all_results}')

                                st.session_state.messages_weblinks.append({'role': 'assistant', 'content': all_results})
                                return user_input, result, user_query

                create_text_question()

    else:
        st.empty()
