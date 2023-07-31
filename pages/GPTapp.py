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

    continue_analyze = False
    def catch_exception(file_name):
        st.sidebar.write(f":red[File {file_name} couldn't be loaded. The file has some irregularities!]")
        return False

    global text_list
    st.session_state.setdefault(key='start')

    # Choose domain
    sector = st.sidebar.selectbox(":red[Choose your Domain]",("Education & Training","Business & Management",
                                                        "Technology & Engineering","Healthcare & Medicine",
                                                        "Creative & Media","Retail & Commerce"))

    # upload files
    st.sidebar.title(":red[File uploader]")
    file_to_upload = st.sidebar.file_uploader(label=':violet[Select PDF, word, or text files to upload]', type=['pdf','docx','txt'],
                                                  accept_multiple_files=True, key='files')
    st.sidebar.caption(":violet[As a general rule, files should not contain images that exceed 40% of the total content.]")
    clear = st.sidebar.button(':white[Clear conversation]',key='clear')
    if clear:
        st.session_state.messages = []
    st.title(":violet[GPT Document Analyzer]")
    st.write(':violet[Upload your PDF files from the left menu & start querying the documents.]')

    if 0 < len(file_to_upload) <= max_files:
        for file in file_to_upload:

            # Check if the upload file is a pdf
            try:
                if str(file.name).endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)
                    if len(text) > 5:
                        text_list.append(text)
                        st.subheader(f':blue[{file.name}]')
                        # with st.expander(file.name):
                        #     st.write(text)
                        continue_analyze = True

                    else:
                        catch_exception(file.name)
                        continue_analyze = False

                # Check if the upload file is a Word docx
                elif str(file.name).endswith('.docx'):
                    text = docx2txt.process(file)
                    if len(text) > 5:
                        text_list.append(text)
                        st.subheader(f':blue[{file.name}]')
                        # with st.expander(file.name):
                        #     st.write(text)
                        continue_analyze = True

                    else:
                        catch_exception(file.name)
                        continue_analyze = False

                # Check if the upload file is a text txt
                elif str(file.name).endswith('.txt'):
                    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
                        tmp.write(file.read())
                        tmp.seek(0)
                        text = textract.process(tmp.name, method='txt')
                        if len(text) > 5:
                            st.subheader(f':blue[{file.name}]')
                            text_list.append(text.decode('utf-8'))
                            # with st.expander(file.name):
                            #     text_lines = text.decode('utf-8').splitlines()
                            #     for line in text_lines:
                            #         st.write(line)
                            continue_analyze = True

                        else:
                            catch_exception(file.name)
                            continue_analyze = False

                else:
                    catch_exception(file.name)
                    continue_analyze = False

            except Exception as e:
                catch_exception(file.name)
                continue_analyze = False

        if continue_analyze:

            with st.spinner(text=":red[Please wait while we process the documents...]"):

                length_words = len(str(text_list))
                chunk_size = 1000 if length_words > 1000 else int(length_words * 1)
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size * 0.001, length_function=len)
                chunks = text_splitter.split_text(text=str(text_list))
                chunks = list(chunks)


                llm = ChatOpenAI(temperature=0.3, model='gpt-4') # gpt-4 or gpt-3.5-turbo
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
            • Add citations when possible from the document that supports the answer.
            • Always add full references related to questions from the given documents only, in bullet points, each one separately, at the end of your answer.
    
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
                    st.subheader(message['content'])

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

                user_input = st.chat_input('Start querying the document here...')
                if user_input:
                    with st.chat_message('user'):
                        st.markdown(user_input)

                    st.session_state.messages.append({'role':'user','content':user_input})

                    with st.spinner(text=":red[Query submitted. This may take a :red[minute or two] while we query the documents...]"):
                        with st.chat_message('assistant'):
                            message_placeholder = st.empty()
                            all_results = ''
                            chat_history = [(user_input, "answer")]
                            result = query_model({"query": user_input, "chat_history": chat_history})
                            user_query = result['query']
                            result = result['chat_history'][1].content
                            all_results += result
                            message_placeholder.subheader(f'{all_results}')

                            st.session_state.messages.append({'role':'assistant','content':all_results})
                            return user_input, result, user_query

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