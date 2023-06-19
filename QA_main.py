#pip install python-dotenv
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import PyPDF2

st.set_page_config(layout="wide")

st.caption("Developed & managed by Samuel Chazy: www.samuelchazy.com")
st.title("GPT Document Analyzer")
st.write('This application harnesses the power of Large Language Models (GPT) to enable you to seamlessly upload PDF documents and engage with them. In the query section, you can pose any question or request GPT to extract information, analyze content, or generate summaries from the uploaded document.')
st.write('Simply upload your PDF file from the menu to the left & start querying the documents.')
st.sidebar.caption('')


if file_to_upload := st.sidebar.file_uploader(
    'Please select a PDF file to upload:',
    type='pdf',
    accept_multiple_files=True,):
    conversation_memory = ConversationBufferMemory(return_messages=True)
    for file in file_to_upload:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=20,length_function=len)
        chunks = text_splitter.split_text(text=text)

        llm = ChatOpenAI(temperature=0.7, model='gpt-4') # gpt-4 or gpt-3.5-turbo
        embedding = OpenAIEmbeddings(openai_api_key=secret_key)
        my_database = Chroma.from_texts(chunks, embedding)
        retriever = my_database.as_retriever()

    ########## RetrievalQA from chain type ##########
    @st.cache_resource(ttl=3600)
    def run_model(question,_main_llm,_main_retriever,_conversation_memory):

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
        chain_type_kwargs = {'prompt':prompt}

        query_model = RetrievalQA.from_chain_type(
            llm=_main_llm,
            chain_type="stuff",
            retriever=_main_retriever,
            chain_type_kwargs=chain_type_kwargs,
            verbose=False)

        response = query_model.run(question)

        _conversation_memory.chat_memory.add_user_message(question)
        _conversation_memory.chat_memory.add_ai_message(response)

        return response,_conversation_memory


    def input_query(_conversation_memory):
        # Create a text area
        st.subheader("What is your query?")
        user_input = st.text_area("Start typing...", value="",placeholder='Enter your text...')

        # Create a submit button
        if st.button("Submit"):
            st.write("Query submitted. This may take a minute while we search the database...")
            st.write("-----------------------------------------------------------------------")
            response,one_memory = run_model(user_input, llm, retriever, _conversation_memory)
            st.write(response)

            return response, one_memory

    input_query(conversation_memory)

else:
    st.sidebar.error('No file selected yet!')