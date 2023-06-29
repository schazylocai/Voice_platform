#pip install python-dotenv
import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2

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

def launch_app():
    file_to_upload = st.sidebar.file_uploader(label='Please select PDF files to upload:', type='pdf',
                                                  accept_multiple_files=True, key='files')

    # st.caption("Developed & managed by Samuel Chazy: www.samuelchazy.com")
    st.title(":violet[GPT Document Analyzer]")
    st.write(':violet[Upload your PDF files from the left menu & start querying the documents.]')

    if len(file_to_upload) > 0:

        text_list = ''
        chunks = ''

        for file in file_to_upload:
            pdf_reader = PyPDF2.PdfReader(file)
            text = "".join(page.extract_text() for page in pdf_reader.pages)
            text_list += text
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=20,length_function=len)
            chunks = text_splitter.split_text(text=text_list)
            chunks = list(chunks)

        llm = ChatOpenAI(temperature=0.7, model='gpt-4') # gpt-4 or gpt-3.5-turbo
        memory = ConversationBufferMemory(return_messages=True)
        embedding = OpenAIEmbeddings(openai_api_key=secret_key)
        my_database = Chroma.from_texts(chunks, embedding)
        retriever = my_database.as_retriever()

        ########## RetrievalQA from chain type ##########
        response_template = """
        • You are a professional in the Educational Field.
        • Your task is to read research papers, research documents, educational journals, and conference papers.
        • You should be analytical and reply in depth.
        • Always reply in a polite and professional manner.
        • Don't connect or look for answers on the internet.
        • Only look for answers from the given documents and papers.
        • Use conversation memory to link all question and responses together
        • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information!"
    
        Divide your answer when possible into paragraphs:
        • What is your answer to the question?
        • How did you come up with this answer?
        • Add citations from the document that supports the answer in bullet points at the end of your answer.
        • Add references related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.
    
        {context}
    
        Question: {question}
    
        Answer:
        """

        prompt = PromptTemplate(template=response_template, input_variables=["context", "question"])
        chain_type_kwargs = {'prompt': prompt}
        query_model = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
            memory=memory,
            verbose=False)

        def create_text_question():
            # Create a new text_area and button
            with st.container():
                st.subheader(':red[What is your query?]')
                _user_input = st.text_area(":violet[▼]", placeholder='Enter your text...')
                _submit_button = st.button(":violet[Submit]")

            return _user_input,_submit_button

        def run_model(_user_input,_submit_button):

            if _submit_button:
                st.divider()
                st.write(":red[Query submitted. This may take a :red[minute] while we query the documents...]")
                st.divider()

                response = query_model.run(_user_input)
                st.write(response)

                _submit_button = False

            return user_input,_submit_button

        user_input,submit_button = create_text_question()
        user_input,submit_button = run_model(user_input,submit_button)

    else:
        st.sidebar.caption(":red[=> No file selected yet!]")


subscribed = False
if "subscribed_status" in st.session_state:
    subscribed_user = st.session_state.subscribed_status
    if subscribed_user:
        launch_app()
    else:
        st.header(':red[You are not subscribed to this service!]')