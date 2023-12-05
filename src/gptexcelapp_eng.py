import numpy as np
import openpyxl
import streamlit as st
import os
from dotenv import load_dotenv
import stripe
import PyPDF2
import docx2txt
import textract
import tempfile
import pandas as pd
import altair as alt
import warnings
import io
import altair_saver
from datetime import datetime
from langchain.callbacks.base import BaseCallbackManager
from langchain.schema.language_model import BaseLanguageModel

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory, StreamlitChatMessageHistory
from langchain.tools import BaseTool
from langchain.vectorstores import SKLearnVectorStore
from langchain.document_loaders import UnstructuredExcelLoader, DataFrameLoader
from langchain.agents import initialize_agent, load_tools, LLMSingleActionAgent, AgentOutputParser, \
    BaseSingleActionAgent, ZeroShotAgent, OpenAIFunctionsAgent
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.agent_types import AgentType
from langchain.prompts import StringPromptTemplate, PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.tools.render import render_text_description
from langchain.callbacks import StreamlitCallbackHandler

from langchain import hub

from typing import Callable, Optional, Dict, Any, Sequence
from typing import List, Union
import re

from src.Change_Text_Style import change_text_style_english

load_dotenv()  # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']
stripe.api_key = strip_secret_key

max_files = 5
final_result = {"question": "", "answer": ""}
violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"


def launch_excel_app_eng():
    ######################################### Set session states #########################################

    if 'user_status' not in st.session_state:
        st.session_state.user_status = 'False'

    if 'messages_excel_eng' not in st.session_state:
        st.session_state.messages_excel_eng = []

    if 'chat_history_excel_eng' not in st.session_state:
        st.session_state.chat_history_excel_eng = []

    if 'excel_sheets_dataframe_eng' not in st.session_state:
        st.session_state.excel_sheets_dataframe_eng = pd.DataFrame()

    if 'excel_sheets_pdf_eng' not in st.session_state:
        st.session_state.excel_sheets_pdf_eng = pd.DataFrame()

    if 'continue_analysis_excel_eng' not in st.session_state:
        st.session_state.continue_analysis_excel_eng = False

    if 'excel_output_dataframe' not in st.session_state:
        st.session_state.excel_output_dataframe = None

    if 'excel_output_chart' not in st.session_state:
        st.session_state.excel_output_chart = None

    ######################################### Catch exceptions #########################################
    def catch_exception(file_name):
        with col2:
            st.subheader(f":red[File {file_name} couldn't be loaded. The file has some irregularities!]")
        return False

    ######################################### Clear all files #########################################
    def clear_all_files():
        st.empty()
        st.session_state.messages_excel_eng = []
        st.session_state.chat_history_excel_eng = []
        st.session_state.excel_sheets_dataframe_eng = pd.DataFrame()

    #################################### Convert uploaded files to text ####################################
    def convert_excel_to_dataframe(my_file, sheet_idx):
        # Check if the upload file is an Excel file
        try:
            if str(my_file.name).endswith('.xlsx'):
                excel_file_uploaded = openpyxl.load_workbook(my_file, read_only=True)

                warnings.simplefilter("ignore")

                # Iterate through all sheets in the Excel file
                with (st.spinner('Loading in_data...')):
                    sheet_name = excel_file_uploaded.sheetnames[sheet_idx]
                    current_sheet_data = pd.read_excel(
                        my_file,
                        engine='openpyxl',
                        sheet_name=sheet_name,
                        parse_dates=True,
                        na_values=np.nan,
                        keep_default_na=True,
                        dtype_backend='numpy_nullable',
                        nrows=2500,
                    )
                    date_written = []
                    adjusted_frame = current_sheet_data.iloc[:-1, :]
                    # Write all column names in small caps
                    try:
                        adjusted_frame.columns = [frame.strip().lower() for frame in adjusted_frame.columns]
                    except Exception as e:
                        adjusted_frame.columns = adjusted_frame.columns

                    # Check if there is a date column
                    date_cols = adjusted_frame.drop(adjusted_frame.select_dtypes(exclude=[np.datetime64,
                                                                                          datetime]), axis=1)
                    if len(adjusted_frame.columns) > 1:
                        try:
                            date_written = [col for col in adjusted_frame if 'date' in col]
                            if date_cols.empty:
                                final_columns = date_written
                            else:
                                final_columns = date_cols.columns.tolist().append(date_written)
                            for col in [final_columns]:
                                adjusted_frame[col] = adjusted_frame[col].ffill()
                                adjusted_frame[col] = adjusted_frame[col].apply(pd.to_datetime)

                        except Exception as e:
                            st.write()

                    # Check if there is a numerical column
                    non_date_cols = adjusted_frame.drop(adjusted_frame.select_dtypes(include=[np.datetime64,
                                                                                              datetime]), axis=1)
                    numerical_cols_to_add = []
                    for col in non_date_cols.columns:
                        try:
                            adjusted_frame[col] = adjusted_frame[col].fillna(0)
                            adjusted_frame[col] = adjusted_frame[col].apply(pd.to_numeric)
                            numerical_cols_to_add.append(col)
                        except Exception as e:
                            st.write()

                    numerical_cols = adjusted_frame.loc[:, numerical_cols_to_add]

                    # replace null values in categorical column with 'NA'
                    categorical_cols = adjusted_frame.drop(date_cols, axis=1)
                    categorical_cols = adjusted_frame.drop(numerical_cols, axis=1)
                    categorical_cols = categorical_cols.fillna('Missing Data')

                    for col in categorical_cols.columns:
                        adjusted_frame[col] = categorical_cols[col]

                    adjusted_frame = adjusted_frame.reset_index(drop=True)
                    # convert an Excel sheet to pdf
                    adjusted_frame_pdf = adjusted_frame.to_csv()
                    return adjusted_frame, adjusted_frame_pdf

            else:
                catch_exception(my_file.name)
                return [], []

        except Exception as e:
            catch_exception(my_file.name)
            st.write(e)
            return [], []

    ######################################### Compose layout #########################################
    col1, col2, col3 = st.columns(3)

    with col1:
        st.title(":red[GPT Excel Analyzer]")

    st.subheader(":violet[• Ensure the :red[1st row] of the table contains the :red[column names] & "
                 "the :red[1st column] of the table is :red[not empty].]")
    st.subheader(':violet[• Refer to columns by their :red[exact column names] in each query:]')
    st.write(':violet[Example 1: What are the names of participant in the column :red["participants"]? Example 2: '
             'what is the total percentage time per office from the columns :red["time spent"] and :red["offices"]?]')

    with col2:
        ################################# load documents #################################
        max_retries = 3

        # upload file 1
        excel_file_1 = st.sidebar.file_uploader(
            label=':violet[Maximum allowed rows = 2,500]',
            type=['xlsx'],
            accept_multiple_files=False, key='excel_file_1_eng',
            label_visibility='visible')

        retry_count_1 = 0
        if excel_file_1:
            while retry_count_1 < max_retries:
                try:
                    if str(excel_file_1.name).endswith('.xlsx'):
                        excel_file = openpyxl.load_workbook(excel_file_1, read_only=True)

                        # Create a list of sheet names and their corresponding indices
                        sheet_info = [(i, sheet_name) for i, sheet_name in enumerate(excel_file.sheetnames)]

                        # Create a radio button to choose a sheet using its index
                        st.sidebar.subheader(':violet[Choose a sheet:]')
                        choose_sheet_index = st.sidebar.selectbox(label='Choose a sheet from the uploaded Excel file:',
                                                                  options=[sheet for sheet in sheet_info],
                                                                  format_func=lambda x: x[1],  # Display sheet names
                                                                  key='choose_sheet_index',
                                                                  label_visibility='hidden',
                                                                  )

                        # Get the selected sheet index
                        selected_index, selected_sheet_name = choose_sheet_index
                        st.session_state.continue_analysis_excel_eng = True

                        st.session_state.excel_sheets_dataframe_eng, st.session_state.excel_sheets_pdf_eng = convert_excel_to_dataframe(
                            excel_file_1, selected_index)
                        break

                except Exception as e:
                    retry_count_1 += 1
                    if retry_count_1 < max_retries:
                        continue
                    st.sidebar.write("Maximum retry attempts reached. Upload failed.")
                    break

        else:
            st.session_state.excel_sheets_dataframe_eng = pd.DataFrame()

    with col3:
        # set the clear button
        st.write("")
        st.write("")
        clear = st.button(':white[Clear conversation & memory]', key='clear', use_container_width=True)

        if clear:
            clear_all_files()

    ######################################### render tables #########################################
    st.divider()
    sheets_frame = st.session_state.excel_sheets_dataframe_eng
    sheets = st.session_state.excel_sheets_pdf_eng

    if excel_file_1:
        graph_type = 'None'
        col_A = 'None'
        col_B = 'None'
        # print dataframe
        # st.dataframe(data=sheets_frame, use_container_width=True)
        st.dataframe(data=sheets_frame, use_container_width=True)

        # select a graph type
        st.sidebar.subheader(':violet[Choose a graph type:]')
        graph_type = st.sidebar.selectbox(
            label='Choose a graph type',
            options=['None', 'bar chart', 'line chart', 'pie chart'],
            key='choose_type',
            label_visibility='hidden',
        )
        if graph_type == 'None':
            col_A = 'None'
            col_B = 'None'

        elif graph_type == 'bar chart':
            try:
                if len(sheets_frame.columns) > 1:
                    # select 1st column
                    col_A = st.sidebar.selectbox(
                        label='Choose first column (x-axis / distribution)',
                        options=['None'] + [sheet for sheet in
                                            sheets_frame.select_dtypes(exclude=['number', np.datetime64, datetime])],
                        key='choose_categorical_A_column',
                        label_visibility='visible',
                    )
                    # select second column
                    col_B = st.sidebar.selectbox(
                        label='Choose second column (y-axis / value)',
                        options=['None'] + [sheet for sheet in sheets_frame.select_dtypes(include='number') if
                                            sheet != col_A],
                        key='choose_value_A_column',
                        label_visibility='visible',
                    )
                    # Isolate dataframe with the selected variables
                    st.divider()
                    # output graph
                    if col_B == 'None':
                        graph_dataframe = pd.DataFrame(data=sheets_frame.loc[:, col_A], columns=[col_A])
                        chart = alt.Chart(graph_dataframe, height=800).mark_bar(cornerRadius=10).encode(
                            alt.X(f'{col_A}:N', axis=alt.Axis(
                                labelFontSize=16,
                                grid=False,
                                labelColor='cyan',
                                titleColor='cyan',
                                titleFontSize=16)),
                            alt.Y('count():Q', axis=alt.Axis(
                                labelFontSize=16,
                                grid=False,
                                labelColor='cyan',
                                titleColor='cyan',
                                titleFontSize=16)),
                            color=f'{col_A}:N'
                        )
                        # Display the chart in Streamlit
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        graph_dataframe = pd.DataFrame(data=sheets_frame.loc[:, [col_A, col_B]], columns=[col_A, col_B])
                        chart = alt.Chart(graph_dataframe, height=800).mark_bar(cornerRadius=10).encode(
                            alt.X(f'{col_A}:N', axis=alt.Axis(
                                labelFontSize=16,
                                grid=False,
                                labelColor='cyan',
                                titleColor='cyan',
                                titleFontSize=16)),
                            alt.Y(f'{col_B}:Q', axis=alt.Axis(
                                labelFontSize=16,
                                grid=False,
                                labelColor='cyan',
                                titleColor='cyan',
                                titleFontSize=16)),
                            color=f'{col_A}:N'
                        )
                        # Display the chart in Streamlit
                        st.altair_chart(chart, use_container_width=True)

                else:
                    st.sidebar.write(
                        ':red[Could not create a bar chart! Check the columns in the excel file. You need to '
                        'have at least 2 columns in the file (a category and a value).]')

            except Exception as e:
                st.write('')

        elif graph_type == 'line chart':
            try:
                if len(sheets_frame.columns) > 1:
                    # select 1st column
                    col_A = st.sidebar.selectbox(
                        label='Choose date column (x-axis)',
                        options=['None'] + [sheet for sheet in
                                            sheets_frame.select_dtypes(include=[np.datetime64, datetime])],
                        key='choose_date_column',
                        label_visibility='visible',
                    )
                    if col_A != 'None':
                        # select second column
                        my_vars = [sheet for sheet in sheets_frame.select_dtypes(include=['number'])]
                        col_B = st.sidebar.multiselect(
                            label='Choose value over time column',
                            options=set(my_vars),
                            key='choose_value_B_column',
                            label_visibility='visible',
                        )
                        if col_B:
                            # Melt the DataFrame to transform columns into rows
                            data_A = pd.DataFrame(data=sheets_frame.loc[:, col_A]).reset_index(drop=True)
                            data_B = pd.DataFrame(data=sheets_frame.loc[:, col_B]).reset_index(drop=True)

                            all_data = pd.concat([data_A, data_B], axis=1)
                            all_data = pd.melt(all_data, id_vars=[col_A], var_name='variables',
                                               value_name='points')
                            st.divider()

                            # output graph
                            chart = alt.Chart(all_data, height=600).mark_line(interpolate='monotone',
                                                                              strokeWidth=3,
                                                                              opacity=0.5).encode(
                                alt.X(f'{col_A}:T', axis=alt.Axis(
                                    labelFontSize=14,
                                    grid=False,
                                    labelColor='cyan',
                                    titleColor='cyan',
                                    titleFontSize=18)),
                                alt.Y('points:Q', axis=alt.Axis(
                                    labelFontSize=12,
                                    grid=False,
                                    labelColor='cyan',
                                    titleColor='cyan',
                                    titleFontSize=18)),
                                color='variables:N'
                            )
                            # Display the chart in Streamlit
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.sidebar.write(
                                ':red[Could not create a line chart! Check the columns in the excel file. You need to '
                                'have at least 2 columns in the file (a date and a value). ]')

                    else:
                        st.sidebar.write(
                            ':red[Could not create a line chart! Check the columns in the excel file. You need to '
                            'have at least 2 columns in the file (a date and a value). ]')

                else:
                    st.sidebar.write(
                        ':red[Could not create a line chart! Check the columns in the excel file. You need to '
                        'have at least 2 columns in the file (a date and a value). ]')

            except Exception as e:
                st.write('')

        elif graph_type == 'pie chart':
            try:
                # select column
                col_A = st.sidebar.selectbox(
                    label='Choose first column (distribution)',
                    options=['None'] + [sheet for sheet in sheets_frame.select_dtypes(exclude=[np.datetime64,
                                                                                               datetime, 'number'])],
                    key='choose_categorical_A_column',
                    label_visibility='visible',
                )
                # Isolate dataframe with the selected variables
                graph_dataframe = pd.DataFrame(data=sheets_frame.loc[:, col_A], columns=[col_A])
                st.divider()

                # Create a new DataFrame with the counts and percentages
                count_df = graph_dataframe[col_A].value_counts(normalize=True).reset_index()
                count_df.columns = ['Variable', 'Percentage']
                count_df['Percentage'] = (count_df['Percentage'] * 100).round(2)

                # output graph
                chart = alt.Chart(count_df, height=700).mark_arc(innerRadius=100, padAngle=0).encode(
                    theta=alt.Theta('Percentage:Q'),
                    color=alt.Color('Variable:N', scale=alt.Scale(scheme='category20c')),
                    tooltip=['Variable', 'Percentage'],
                )
                # Display the chart in Streamlit
                st.altair_chart(chart, use_container_width=True)

            except Exception as e:
                st.write('')

        else:
            graph_type = 'None'
            st.sidebar.write(':red[Choose graph type.]')

    st.divider()

    ####################################### Write chat history #######################################
    for message in st.session_state.messages_excel_eng:
        with st.chat_message(message['role']):
            change_text_style_english(message['content'], 'main_text_white', 'white')

    ##################################### chunk the document #########################################

    if len(sheets) > 0:
        @st.cache_resource
        def embed_text(sheets_text):
            try:
                with st.spinner(text=":red[Please wait while we process the excel file...]"):

                    chunk_size = 1500
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200,
                                                                   length_function=len)
                    chunks = text_splitter.split_text(text=str(sheets_text))
                    chunks = list(chunks)

                    in_llm = ChatOpenAI(temperature=0.0, model=st.session_state.ChatOpenAI)
                    in_embedding = OpenAIEmbeddings()

                    in_vector_store = SKLearnVectorStore.from_texts(texts=chunks, embedding=in_embedding,
                                                                    persist_path=None)
                    # in_vector_store.persist()
                    in_retriever = in_vector_store.as_retriever(search_kwargs={"k": 3})
                    st.session_state.continue_analysis_excel_eng = True

                    return in_llm, in_retriever

            except Exception as e:
                st.subheader(":red[An error occurred. Please delete the uploaded file, and then uploaded it again]")
                st.session_state.continue_analysis_excel_eng = True
                # st.markdown(e)
                return in_llm, in_retriever

        llm, retriever = embed_text(sheets)

    else:
        llm = ChatOpenAI(temperature=0.0, model=st.session_state.ChatOpenAI)  # gpt-4 or gpt-3.5-turbo
        embedding = OpenAIEmbeddings()
        vector_store = SKLearnVectorStore.from_texts(texts='No text provided...', embedding=embedding,
                                                     persist_path=None)
        retriever = vector_store.as_retriever(search_kwargs={"k": 1})
        st.session_state.continue_analysis_excel_eng = True

    ######################################## documents ########################################
    if st.session_state.continue_analysis_excel_eng:

        #################################### Templates ####################################

        response_template = """
                        - you are provided with a dataframe {{sheets}}
                        - Take a deep breath and work on this problem step-by-step.

                        - You are only allowed to use the dataframe {{sheets}} given to you.
                        - Don't use any information outside the given dataframe {{sheets}}.
                        - If you do not know the answer, reply as follows: "I do not know the answer..."

                        - Give your final solution in an excel like format.
                        - List all the in_lines of the solution.
                        - In your solution, sort the in_lines in descending order

                        - Example:
                            "Column 1": "Column 2"
                            "Data scientist": {{percentage}} of Data scientist in the column
                            "Data analyst": {{percentage}} of Data analyst in the column
                            "Web developer": {{percentage}} of Web developer in the column

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

        #################################### Run the model ####################################
        def create_text_question():

            user_input = st.chat_input('Start querying the tables here...',
                                       max_chars=500, key='user_input')
            if user_input:
                with st.chat_message('user'):
                    st.markdown(user_input)

                st.session_state.messages_excel_eng.append({'role': 'user', 'content': user_input})

                with st.spinner(text=":red[Query submitted. This may take a minute while we query the tables...]"):
                    with st.chat_message('assistant'):
                        all_results = ''
                        chat_files_eng = st.session_state.chat_history_excel_eng
                        # st_callback = StreamlitCallbackHandler(st.container())  # callbacks = [st_callback]
                        output = query_model({"query": user_input})
                        user_query = user_input
                        result = output['result']
                        st.session_state.chat_history_excel_eng.append((user_query, result))
                        all_results += result

                        st.session_state.messages_excel_eng.append({'role': 'assistant', 'content': all_results})
                        return result

        final_LLM_output = create_text_question()

        def render_data_frame(df_output):
            try:
                in_frame = df_output.strip().replace('-', '')
                in_frame = in_frame.split('\n')
                bullet_output_columns = []
                for fr in in_frame:
                    in_line = fr.split(': ')
                    bullet_output_columns.append(in_line)

                if len(bullet_output_columns) > 1:
                    pandas_df = pd.DataFrame(data=bullet_output_columns)
                    # Display the dataframe in Streamlit
                    st.dataframe(pandas_df, use_container_width=True)

                    # Create an in-memory Excel file
                    excel_buffer = io.BytesIO()
                    excel_writer = pd.ExcelWriter(excel_buffer, engine='openpyxl')
                    pandas_df.to_excel(excel_writer, index=False)

                    # Provide a download button to download the in-memory Excel file
                    st.download_button(
                        label='Save table',
                        data=excel_buffer.getvalue(),
                        key='download_button',
                        file_name='table.xlsx',
                        use_container_width=True,
                    )
                    return pandas_df
                else:
                    message_placeholder = st.empty()
                    font_link_eng = '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">'
                    font_family_eng = "'Roboto', sans-serif"
                    message_placeholder.markdown('According to the Excel file:')
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
                                                    <div class="bold-text"><bdi>{df_output}</bdi></div>
                                                    """, unsafe_allow_html=True)
                    # st.write(bullet_output)

            except Exception as e:
                st.write(df_output)
                return df_output

        def render_graph(data_graph):
            try:
                data_plot = data_graph.strip().replace('-', '').replace('%', '')
                data_plot = data_plot.split('\n')
                lines_graph = []
                for dg in data_plot:
                    line_graph = dg.split(': ')
                    lines_graph.append(line_graph)
                pandas_df_graph = pd.DataFrame(data=lines_graph)
                pandas_df_graph['value'] = pd.to_numeric(pandas_df_graph['value']).astype(float)

                # Create a Streamlit bar chart using Altair
                st.header('Bar Chart...')
                # Create a bar chart using Altair
                chart = alt.Chart(pandas_df_graph, height=600).mark_bar(cornerRadius=10, color='cyan').encode(
                    alt.Y('variable:N', axis=alt.Axis(labelFontSize=14)),
                    alt.X('value:Q', axis=alt.Axis(labelFontSize=12)), )
                # Display the chart in Streamlit
                st.altair_chart(chart, use_container_width=True)

                # Convert the Altair chart to a PNG image in memory
                chart_image = chart.to_html()
                # chart_saved = chart.save(fp='chart.png', ppi=300, format='png', engine="vl-convert")

                # Provide a download link for the in-memory image
                st.download_button(
                    label='Download bar chart',
                    data=chart_image,
                    key='download_chart_button',
                    file_name='chart.html',
                    use_container_width=True,
                )

                return chart
            except Exception as e:
                return ''

        if final_LLM_output is not None:
            try:
                data = ''
                for idx, d in enumerate(final_LLM_output):
                    if d == ': ':
                        data = final_LLM_output[idx + 1:]
                        break
                data_frame = data.strip().replace('-', '')
                data_frame = data_frame.split('\n')
                lines = []
                for d in data_frame:
                    line = d.split(': ')
                    lines.append(line)

                render_data_frame(final_LLM_output)
                render_graph(final_LLM_output)

            except Exception as e:
                st.write(':red[An error has occurred]')
        else:
            st.write('')

    else:
        st.empty()
