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
from src.Change_Text_Style import change_text_style_arabic, change_text_style_arabic_side

load_dotenv()  # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

text_list = []
max_files = 5
final_result = {"query": "", "answer": ""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def launch_app_ara():
    continue_analyze = False
    file_uploaded = False

    def catch_exception(file_name):
        change_text_style_arabic_side(("لم يمكن تحميل الملف. يحتوي الملف" + " " + file_name + " " + "على بعض الشوائب!"),
                                      'text_red_side_big', red)
        return False

    global text_list
    st.session_state.setdefault(key='start')

    # upload files
    change_text_style_arabic_side(" حمل PDF, word, أو أي نص", 'text_violet_side_tight', violet)
    file_to_upload = st.sidebar.file_uploader(label=':violet[➜]', type=['pdf', 'docx', 'txt'],
                                              accept_multiple_files=True, key='files')
    change_text_style_arabic_side("يرجى تحميل ملف واحد تلو الآخر وليس كلها في نفس الوقت.", 'text_violet_side_tight',
                                  violet)
    change_text_style_arabic_side(
        "إذا حدث خطأ Axios قم إما بحذف الملف وتحميله مرة أخرى أو قم بتحديث الصفحة وتسجيل الدخول مرة أخرى أو عاود "
        "المحاولة بعد فترة من الوقت",
        'text_violet_side_tight', violet)
    st.sidebar.markdown("")

    clear = st.sidebar.button(':red[مسح المحادثة والذاكرة]', key='clear', use_container_width=True)
    if clear:
        st.session_state.messages = []
        text_list = []

    change_text_style_arabic(("GPT" + " " + "محلل المستندات"), 'title', red)
    change_text_style_arabic("قم بتحميل ملفاتك من القائمة اليسرى وابدأ في تحليل المستندات.", 'text_violet', violet)

    if len(file_to_upload) <= max_files:
        for file in file_to_upload:

            # Check if the upload file is a pdf
            try:
                if str(file.name).endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)
                    if len(text) > 5:
                        text_list.append(f"File: {file.name}")
                        text_list.append(f"Document name: {file.name}")
                        text_list.append(f"Document title: {os.path.splitext(file.name)[0]}")
                        text_list.append('<| beginning of text |>')
                        text_list.append(text)
                        text_list.append('<| end of text |>')
                        st.subheader(f':blue[{file.name}]')
                        file_uploaded = True

                    else:
                        catch_exception(file.name)
                        file_uploaded = False

                # Check if the upload file is a Word docx
                elif str(file.name).endswith('.docx'):
                    text = docx2txt.process(file)
                    if len(text) > 5:
                        text_list.append(f"File: {file.name}")
                        text_list.append(f"Document name: {file.name}")
                        text_list.append(f"Document title: {os.path.splitext(file.name)[0]}")
                        text_list.append('<| beginning of text |>')
                        text_list.append(text)
                        text_list.append('<| end of text |>')
                        st.subheader(f':blue[{file.name}]')
                        file_uploaded = True

                    else:
                        catch_exception(file.name)
                        file_uploaded = False

                # Check if the upload file is a text txt
                elif str(file.name).endswith('.txt'):
                    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                        tmp.write(file.read())
                        tmp.seek(0)
                        text = textract.process(tmp.name, method='txt')
                        if len(text) > 5:
                            text_list.append(f"File: {file.name}")
                            text_list.append(f"Document name: {file.name}")
                            text_list.append(f"Document title: {os.path.splitext(file.name)[0]}")
                            text_list.append('<| beginning of text |>')
                            text_list.append(text.decode('utf-8'))
                            text_list.append('<| end of text |>')
                            st.subheader(f':blue[{file.name}]')
                            file_uploaded = True

                        else:
                            catch_exception(file.name)
                            file_uploaded = False

                else:
                    catch_exception(file.name)
                    file_uploaded = False

            except Exception as e:
                catch_exception(file.name)
                file_uploaded = False

        if file_uploaded:

            try:
                with st.spinner(text=":red[يرجى الانتظار بينما نقرء المستندات...]"):

                    chunk_size = 2500
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100,
                                                                   length_function=len)
                    chunks = text_splitter.split_text(text=str(text_list))
                    chunks = list(chunks)

                    llm = ChatOpenAI(temperature=0.2, model='gpt-4')  # gpt-4 or gpt-3.5-turbo
                    embedding = OpenAIEmbeddings()

                    vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=embedding)
                    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
                    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                    continue_analyze = True

            except Exception as e:
                change_text_style_arabic("حدث خطأ. يرجى حذف الملف المحمّل ثم إعادة تحميله مرة أخرى.", 'subhead', 'red')
                st.markdown(e)

            if continue_analyze:
                # RetrievalQA from chain type ##########

                response_template = f"""
                • You will act as an Arabic professional and a researcher.
                • Your task is to reply only in Arabic even if the question is in another language.
                • Your task is to read through research papers, documents, journals, manuals, articles, and presentations.
                • You should be analytical, thoughtful, and reply in depth and details to any question.
                • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
                • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
                • Always reply in a polite and professional manner.
                • Don't connect or look for answers on the internet.
                • Only look for answers from the given documents and papers.
                • If you don't know the answer to the question, then reply: "أنا لست واثقًا من الإجابة على هذا السؤال بسبب غياب بعض المعلومات. حاول تحديد السؤال بطريقة اخرى."
    
                Divide your answer when possible into paragraphs:
                • What is your answer to the question?
                • Add citations when possible from the document that supports the answer.
                • Add references when possible related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.
    
                {{context}}
    
                Question: {{question}}
    
                Answer:
                """

                if 'ChatOpenAI' not in st.session_state:
                    st.session_state['ChatOpenAI'] = llm

                if 'messages' not in st.session_state:
                    st.session_state.messages = []

                for message in st.session_state.messages:
                    with st.chat_message(message['role']):
                        change_text_style_arabic_side(message['content'], 'bot_reply_text', 'white')

                prompt = PromptTemplate(template=response_template, input_variables=["context", "question"])
                chain_type_kwargs = {'prompt': prompt}
                query_model = RetrievalQA.from_chain_type(
                    llm=st.session_state['ChatOpenAI'],
                    chain_type="stuff",
                    memory=memory,
                    return_source_documents=False,
                    retriever=retriever,
                    chain_type_kwargs=chain_type_kwargs,
                    verbose=False)

                @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
                def create_text_question():

                    user_input = st.chat_input('ابدأ المحادثة هنا...')
                    if user_input:
                        with st.chat_message('user'):
                            change_text_style_arabic_side(user_input, 'bot_reply_text', 'white')

                        st.session_state.messages.append({'role': 'user', 'content': user_input})

                        with st.spinner(text=":red[تم إرسال المحادثة. قد يستغرق ذلك حوالي دقيقة لتحليل المستندات...]"):
                            with st.chat_message('assistant'):
                                message_placeholder = st.empty()
                                all_results = ''
                                chat_history = [(user_input, "answer")]
                                result = query_model({"query": user_input, "chat_history": chat_history})
                                user_query = result['query']
                                result = result['chat_history'][1].content
                                all_results += result
                                # message_placeholder.subheader(f'{all_results}')
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
                                # change_text_style_arabic_side(all_results,'bot_reply_text','white')

                                st.session_state.messages.append({'role': 'assistant', 'content': all_results})
                                return user_input, result, user_query

                create_text_question()

    if len(file_to_upload) == 0:
        change_text_style_arabic_side("لم يتم تحميل أي ملف حتى الآن", 'text_red_side', red)

    elif len(file_to_upload) >= max_files:
        change_text_style_arabic_side(("الحد الأقصى لعدد الملفات المحملة هو" + " " + str(max_files)), 'text_red_side',
                                      red)
        change_text_style_arabic_side(("يرجى إزالة بعض الملفات"), 'text_red_side', red)
