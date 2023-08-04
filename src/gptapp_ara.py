import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2
import docx2txt
import textract
import tempfile

load_dotenv() # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

text_list = []
max_files = 5
final_result = {"query":"","answer":""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from src.Change_Text_Style import change_text_style_arabic,change_text_style_arabic_side

st.session_state.mylanguage = 'العربية'

def launch_app_ara():

    continue_analyze = False
    def catch_exception(file_name):
        change_text_style_arabic_side(("لم يمكن تحميل الملف. يحتوي الملف"+" "+ file_name +" "+ "على بعض الشوائب!"),'text_red_side',red)
        return False

    global text_list
    st.session_state.setdefault(key='start')

    # Choose domain
    change_text_style_arabic_side("اختر مجالك", 'text_violet_side_tight', violet)
    sector = st.sidebar.selectbox(":violet[➜]",("التعليم والتدريب","الأعمال والإدارة",
                                                        "التكنولوجيا والهندسة","الرعاية الصحية والطب",
                                                        "الإبداع والإعلام","التجزئة والتجارة"))

    # upload files
    change_text_style_arabic_side(" حمل PDF, word, أو أي نص", 'text_violet_side_tight', violet)
    file_to_upload = st.sidebar.file_uploader(label=':violet[➜]', type=['pdf','docx','txt'],
                                                  accept_multiple_files=True, key='files')
    change_text_style_arabic_side("على سبيل القاعدة العامة، لا يجب أن تحتوي الملفات على صور تزيد عن 40% من المحتوى الكلي.", 'text_violet_side_tight', violet)
    st.sidebar.markdown("")
    clear = st.sidebar.button(':red[مسح المحادثة]',key='clear',use_container_width=True)
    if clear:
        st.session_state.messages = []
    change_text_style_arabic(("GPT"+" "+"محلل المستندات"),'title',red)
    change_text_style_arabic("قم بتحميل ملفاتك من القائمة اليسرى وابدأ في تحليل المستندات.", 'text_violet', violet)

    if len(file_to_upload) <= max_files:
        for file in file_to_upload:

            # Check if the upload file is a pdf
            try:
                if str(file.name).endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)
                    if len(text) > 5:
                        text_list.append(text)
                        st.subheader(f':blue[{file.name}]')

                    else:
                        catch_exception(file.name)

                # Check if the upload file is a Word docx
                elif str(file.name).endswith('.docx'):
                    text = docx2txt.process(file)
                    if len(text) > 5:
                        text_list.append(text)
                        st.subheader(f':blue[{file.name}]')

                    else:
                        catch_exception(file.name)

                # Check if the upload file is a text txt
                elif str(file.name).endswith('.txt'):
                    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                        tmp.write(file.read())
                        tmp.seek(0)
                        text = textract.process(tmp.name, method='txt')
                        if len(text) > 5:
                            st.subheader(f':blue[{file.name}]')
                            text_list.append(text.decode('utf-8'))

                        else:
                            catch_exception(file.name)

                else:
                    catch_exception(file.name)

            except Exception as e:
                catch_exception(file.name)

        with st.spinner(text=":red[يرجى الانتظار بينما نحلل المستندات...]"):

            length_words = len(str(text_list))
            chunk_size = 1000 if length_words > 1000 else int(length_words * 1)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size * 0.001, length_function=len)
            chunks = text_splitter.split_text(text=str(text_list))
            chunks = list(chunks)


            llm = ChatOpenAI(temperature=0.3, model='gpt-3.5-turbo') # gpt-4 or gpt-3.5-turbo
            embedding = OpenAIEmbeddings(openai_api_key=secret_key)
            my_database = Chroma.from_texts(chunks, embedding)
            retriever = my_database.as_retriever(search_kwargs={"k": 1})
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        ########## RetrievalQA from chain type ##########

        response_template = f"""
        • You will act as a professional and a researcher in the {sector} Field.
        • Your task is to reply in Arabic.
        • Your task is to read through research papers, documents, journals, manuals, articles, and presentations that are related to the {sector} sector.
        • You should be analytical, thoughtful, and reply in depth and details to any question.
        • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
        • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
        • Always reply in a polite and professional manner.
        • Don't connect or look for answers on the internet.
        • Only look for answers from the given documents and papers.
        • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information! Please try to be more precise and accurate in your query."

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
                #st.subheader(message['content'])
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

        def create_text_question():

            user_input = st.chat_input('ابدأ المحادثة هنا...')
            if user_input:
                with st.chat_message('user'):
                    #st.markdown(user_input)
                    change_text_style_arabic_side(user_input, 'bot_reply_text', 'white')


                st.session_state.messages.append({'role':'user','content':user_input})

                with st.spinner(text=":red[تم إرسال المحادثة. قد يستغرق ذلك حوالي دقيقة لتحليل المستندات...]"):
                    with st.chat_message('assistant'):
                        message_placeholder = st.empty()
                        all_results = ''
                        chat_history = [(user_input, "answer")]
                        result = query_model({"query": user_input, "chat_history": chat_history})
                        user_query = result['query']
                        result = result['chat_history'][1].content
                        all_results += result
                        #message_placeholder.subheader(f'{all_results}')
                        font_link = '<link href="https://fonts.googleapis.com/css2?family=Cairo+Play:wght@600;800&display=swap" rel="stylesheet">'
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
                        #change_text_style_arabic_side(all_results,'bot_reply_text','white')

                        st.session_state.messages.append({'role':'assistant','content':all_results})
                        return user_input, result, user_query

        create_text_question()

    if len(file_to_upload) == 0:
        change_text_style_arabic_side("لم يتم تحميل أي ملف حتى الآن", 'text_red_side', red)

    elif len(file_to_upload) >= max_files:
        change_text_style_arabic_side(("الحد الأقصى لعدد الملفات المحملة هو"+" "+str(max_files)), 'text_red_side', red)
        change_text_style_arabic_side(("يرجى إزالة بعض الملفات"), 'text_red_side',red)