import time

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

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

client_started = False
subscribed = False
text_list = []
max_files = 5
final_result = {"query":"","answer":""}

def launch_app():

    global text_list
    st.session_state.setdefault(key='start')

    # Choose domain
    st.sidebar.title(":red[Sectors of expertise]")
    sector = st.sidebar.selectbox(":violet[Choose your Domain]",("Education & Training","Business & Management",
                                                        "Technology & Engineering","Healthcare & Medicine",
                                                        "Creative & Media","Retail & Commerce"))
    st.sidebar.divider()

    # upload files
    st.sidebar.title(":red[File uploader]")
    file_to_upload = st.sidebar.file_uploader(label=':violet[Select PDF, word, or text files to upload]', type=['pdf','docx','txt'],
                                                  accept_multiple_files=True, key='files')
    st.title(":violet[GPT Document Analyzer]")
    st.write(':violet[Upload your PDF files from the left menu & start querying the documents.]')

    if 0 < len(file_to_upload) <= max_files:
        for file in file_to_upload:

            # Check if the upload file is a pdf
            try:
                if str(file.name).endswith('.pdf'):

                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)
                    text_list.append(text)
                    with st.expander(file.name):
                        st.write(text)

                # Check if the upload file is a Word docx
                elif str(file.name).endswith('.docx'):
                    text = docx2txt.process(file)
                    text_list.append(text)
                    with st.expander(file.name):
                        st.write(text)

                # Check if the upload file is a text txt
                elif str(file.name).endswith('.txt'):
                    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                        tmp.write(file.read())
                        tmp.seek(0)
                        text = textract.process(tmp.name, method='txt')
                        text_list.append(text.decode('utf-8'))
                        with st.expander(file.name):
                            text_lines = text.decode('utf-8').splitlines()
                            for line in text_lines:
                                st.write(line)
                else:
                    st.sidebar.write(":red[File format is not correct!]")

            except Exception as e:
                st.sidebar.write(":red[File couldn't be loaded. The file has some irregularities!]")
                return False

        with st.spinner(text=":red[Please wait while we collect all the documents...]"):

            length_words = len(str(text_list))
            if length_words > 2500:
                chunk_size = 2500

            else:
                chunk_size = int(length_words * 0.5)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size * 0.01, length_function=len)
            chunks = text_splitter.split_text(text=str(text_list))
            chunks = list(chunks)


            llm = ChatOpenAI(temperature=0.5, model='gpt-4') # gpt-4 or gpt-3.5-turbo
            embedding = OpenAIEmbeddings(openai_api_key=secret_key)
            my_database = Chroma.from_texts(chunks, embedding)
            retriever = my_database.as_retriever(search_kwargs={"k": 1})
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        ########## RetrievalQA from chain type ##########
        response_template = f"""
        • You will act as a professional and a researcher in the {sector} Field.
        • Your task is to read through research papers, documents, journals, manuals, articles, and presentations that are related to the {sector} sector.
        • You should be analytical, thoughtful, and reply in depth and details to any question.
        • If you suspect bias in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is biased". Explain why do yuo think it is biased.
        • If you suspect incorrect or misleading information in the answer, then highlight the concerned sentence or paragraph in quotation marks and write: "It is highly likly that this sentence or paragrph is incorrect or misleading". Explain why do yuo think it is incorrect or misleading.
        • Always reply in a polite and professional manner.
        • Don't connect or look for answers on the internet.
        • Only look for answers from the given documents and papers.
        • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information! Please try to be more precise and accurate in your query, and if need be, try to refer to the name of the document that you would like to query."

        Divide your answer when possible into paragraphs:
        • What is your answer to the question?
        • Add citations when possible from the document that supports the answer at the end of your answer.
        • Always add full references related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.

        {{context}}

        Question: {{question}}

        Answer:
        """

        prompt = PromptTemplate(template=response_template, input_variables=["context", "question"])
        chain_type_kwargs = {'prompt': prompt}
        query_model = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            memory=memory,
            return_source_documents=False,
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
            verbose=False)

        def create_text_question():
            # Create a new text_area and button
            st.subheader(':red[What is your query?]')
            user_text = st.text_area(":violet[▼]", placeholder='Enter your text...',key='user_text')

            with st.form(key='my_form'):
                user_input = user_text
                submit_button = st.form_submit_button(label=':violet[Submit]')
                if submit_button:
                    user_input, result_q, query = run_model(user_input)
                    final_result[query] = result_q

                return user_text

        def run_model(_user_input):

            st.divider()
            with st.spinner(text=":red[Query submitted. This may take a :red[minute or two] while we query the documents...]"):
                chat_history = [(_user_input, "answer")]
                result = query_model({"query":_user_input,"chat_history":chat_history})
                user_query = result['query']
                result = result['chat_history'][1].content
                st.subheader(result)

                return _user_input,result,user_query

        create_text_question()

    elif len(file_to_upload) == 0:
        st.sidebar.caption(":red[=> No file selected yet!]")

    elif len(file_to_upload) >= max_files:
        st.sidebar.caption(f":red[=> Maximum number of uploaded files is {max_files}. Please remove some files!]")


# Check if a user is subscribed to launch the GPTapp
if "subscribed_status" in st.session_state and client_started == False:
    subscribed_user = st.session_state.subscribed_status
    if subscribed_user:
        launch_app()
        client_started = True
    else:
        st.header(':red[Subscription is not valid!]')
        st.subheader(':violet[Please Login or Subscribe in the About page.]')