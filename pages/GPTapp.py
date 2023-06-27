#pip install python-dotenv
import numpy as np
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

import stripe
stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import PyPDF2

global subscribed
subscribed = False
global chunks
global text_list

def second_page():
    #st.caption("Developed & managed by Samuel Chazy: www.samuelchazy.com")
    st.title("GPT Document Analyzer")
    st.write('This application harnesses the power of Large Language Models (GPT) to enable you to seamlessly upload PDF documents and engage with them. In the query section, you can pose any question or request GPT to extract information, analyze content, or generate summaries from the uploaded document.')
    st.write('Simply upload your PDF file from the menu to the left & start querying the documents.')

    text_list = ''

    if file_to_upload := st.sidebar.file_uploader(
        'Please select a PDF file to upload:',
        type='pdf',
        accept_multiple_files=True,):
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
    
        Divide your answer when possible into bullet points style:
        • What is the question?
        • What did you read in the document to analyze the question?
        • What is your answer to the question?
        • Add citations from the document that supports the answer in bullet points at the end of your answer.
        • What made you come up with this conclusion or response?
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

        if 'generated' not in st.session_state:
            st.session_state['generated'] = []

        if 'past' not in st.session_state:
            st.session_state['past'] = []

        def create_text_question():
            # Create a new text_area and button
            st.caption("-----------------------------------------------------------------------")
            with st.container():
                st.subheader('What is your query?')
                _user_input = st.text_area("▼", placeholder='Enter your text...')
                _submit_button = st.button("Submit")

            return _user_input,_submit_button

        def run_model(_user_input,_submit_button):

            if _submit_button:
                st.write("Query submitted. This may take a minute while we search the database...")
                st.caption("-----------------------------------------------------------------------")

                response = query_model.run(_user_input)
                st.session_state.past.append(_user_input)
                st.session_state.generated.append(response)
                st.write(response)
                #st.write(memory.load_memory_variables({}))

                _submit_button = False

            return user_input,_submit_button

        user_input,submit_button = create_text_question()
        user_input,submit_button = run_model(user_input,submit_button)

    else:
        st.sidebar.caption("No file selected yet!")

def check_subscription(subscribed_status):
    email = st.text_input(":violet[Please enter your email address:]")
    if st.button(":violet[Submit]"):
        stripe.api_key = strip_secret_key
        customer = stripe.Customer.list(email=email)
        if len(customer.data) > 0:
            subscribed_status = True
            second_page()
        else:
            st.header(':red[You are not subscribed to this service!]')
            st.write(':violet[Please subscribe using the About section.]')

        return subscribed_status

check_subscription(subscribed)