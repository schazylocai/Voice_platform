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


def launch_app():

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

    if len(file_to_upload) > 0:

        text_list = ''
        chunks = ''

        for file in file_to_upload:

            # Check if the upload file is a pdf
            if str(file.name).endswith('.pdf'):

                pdf_reader = PyPDF2.PdfReader(file)
                text = "".join(page.extract_text() for page in pdf_reader.pages)
                text_list += text
                with st.expander(file.name):
                    st.write(text)

            # Check if the upload file is a Word docx
            elif str(file.name).endswith('.docx'):
                text = docx2txt.process(file)
                text_list += text
                with st.expander(file.name):
                    st.write(text)

            # Check if the upload file is a text txt
            elif str(file.name).endswith('.txt'):
                with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                    tmp.write(file.read())
                    tmp.seek(0)
                    text = textract.process(tmp.name, method='txt')
                    text_list += text.decode('utf-8')
                    with st.expander(file.name):
                        text_lines = text.decode('utf-8').splitlines()
                        for line in text_lines:
                            st.write(line)
            else:
                st.sidebar.write(":red[File format is not correct!]")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20, length_function=len)
        chunks = text_splitter.split_text(text=text_list)
        chunks = list(chunks)

        llm = ChatOpenAI(temperature=0.7, model='gpt-4') # gpt-4 or gpt-3.5-turbo
        embedding = OpenAIEmbeddings(openai_api_key=secret_key)
        my_database = Chroma.from_texts(chunks, embedding)
        retriever = my_database.as_retriever()

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
        • If you don't know the answer to the question, then reply: "I can't be confident about my answer because I am missing the context or some information!"

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
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
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
                st.write(":red[Query submitted. This may take a :red[minute or two] while we query the documents...]")
                st.divider()

                response = query_model.run(_user_input)
                st.subheader(response)

                _submit_button = False

            return user_input,_submit_button

        user_input,submit_button = create_text_question()
        user_input,submit_button = run_model(user_input,submit_button)

    else:
        st.sidebar.caption(":red[=> No file selected yet!]")

# Check if a user is subscribed to launch the GPTapp
subscribed = False
if "subscribed_status" in st.session_state:
    subscribed_user = st.session_state.subscribed_status
    if subscribed_user:
        launch_app()
    else:
        st.header(':red[Subscription is not valid!]')
        st.subheader(':violet[Please Login or Subscribe in the About page.]')