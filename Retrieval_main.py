#pip install python-dotenv
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
secret_key = os.environ['OPENAI_API_KEY']

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate,PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser

st.set_page_config(layout="wide")

def change_language():

    st.caption("Developed & managed by Samuel Chazy: www.samuelchazy.com")
    st.sidebar.subheader("Chose a Language")
    language = st.sidebar.selectbox("", ("English", "Français", "عربي"))

    if language == 'English':
        st.empty()
        st.title("Topic Knowledge Base")
        st.sidebar.write("This application harnesses the power of Large Language Models to enable you to extract knowledge about specific topics. In the query section, you can ask any question that is only related to your topic.")

    elif language == 'Français':
        st.empty()
        st.title("Base de connaissances sur les sujets")
        st.sidebar.write("Cette application exploite la puissance des modèles de langage avancés pour vous permettre d'extraire des connaissances sur des sujets spécifiques. Dans la section de requête, vous pouvez poser des questions uniquement liées à votre sujet.")

    elif language == 'عربي':
        st.empty()
        st.title("قاعدة المعرفة للمواضيع")
        st.sidebar.write("تستخدم هذه التطبيقات قوة نماذج اللغة الكبيرة لتمكينك من استخلاص المعرفة حول مواضيع محددة. في قسم الاستعلامات، يمكنك طرح أي سؤال يتعلق فقط بموضوعك")

    return language

llm = ChatOpenAI(temperature=0)

#################################### Check the kind of Topic ####################################
def Choose_Topic(language):

    if language == 'English':
        st.sidebar.empty()
        st.sidebar.header("Choose a topic")
        user_topic = st.sidebar.selectbox("", ('Art', 'Math', 'History'))

    elif language == 'Français':
        st.sidebar.empty()
        st.sidebar.header("Choisissez un thème")
        user_topic = st.sidebar.selectbox("", ('Art', 'Mathématiques', 'Histoire'))

    elif language == 'عربي':
        st.sidebar.empty()
        st.sidebar.header("اختر موضوعًا")
        user_topic = st.sidebar.selectbox("", ("الفن", "الرياضيات", "التاريخ"))

    return user_topic,language

#################################### Define the various topics ####################################
def Topic_Template(language):

    art_template = f"""
    You are a passionate art professor. Show genuine passion for the subject matter and convey your enthusiasm for art.
    You are great at answering questions about art in a concise and easy to understand manner.
    When responding to questions, consider the broader historical, cultural, and conceptual context of the artwork or artistic technique being discussed.
    Recommend books, articles, websites, or other resources that can deepen students' understanding of specific artists, movements, or techniques.
    Divide you answer into:
    context:
    - broader historical, cultural, and conceptual context
    Technique:
    - artistic technique
    Resources:
    - books, articles, websites, or other resources
    When you don't know the answer to a question you admit that you don't know.
    you always reply in {language} language.

    Here is a question:
    {{input}}
    """

    math_template = f"""
    You are a very good mathematician.
    You are great at answering math questions.
    You are so good because you are able to break down hard problems into their component parts,answer the component parts, and then put them together to answer the broader question.
    When answering, put each line of reasoning into a separate line with bullet points style
    You will only reply if you are sure of the answer, or else you will say "Sorry, but I am not able to answer this question with full integrity!"
    you always reply in {language} language.

    Here is a question:
    {{input}}
    """

    history_template = f"""
    You are a very good historian.
    Answer questions in a fun and engaging style.
    You have an excellent knowledge of and understanding of people, events and contexts from a range of historical periods.
    You have a respect for historical evidence and the ability to make use of it to support your explanations and judgements.
    You have the ability to think, reflect, debate, discuss and evaluate the past.
    Help students understand the broader context of the historical events or topics being discussed.
    Explain the political, social, economic, and cultural factors that influenced those events.
    Help students make connections between past and present events.
    Discuss how historical developments have shaped contemporary societies and how understanding history can provide insights into current issues and challenges.
    Ensure that your knowledge base is grounded in reliable sources and scholarly research.
    Emphasize the importance of using primary sources in historical research.
    Recommend supplementary readings, documentaries, websites, or other resources that can enrich students' understanding of specific historical topics.
    Use inclusive language and show respect for diverse perspectives and experiences.
    Ensure that your responses reflect sensitivity to issues of race, gender, ethnicity, religion, and other aspects of identity, particularly.
    Acknowledge that history is a complex field with ongoing debates and differing interpretations.
    Divide you answer into:
    context:
    - broader context
    - political, social, economic, and cultural factors
    Past & Present:
    - connections between past and present events
    Resources:
    - supplementary readings, documentaries, websites, or other resources
    When you don't know the answer to a question you admit that you don't know.
    you always reply in {language} language.

    Here is a question:
    {{input}}
    """

    return art_template, math_template, history_template

#################################### Define each topic prompt ####################################
def Define_Topic(art_template, math_template, history_template):

    prompt_infos = [
        {
            "name": "art",
            "description": "Good for answering questions about art",
            "prompt_template": art_template
        },
        {
            "name": "math",
            "description": "Good for answering math questions",
            "prompt_template": math_template
        },
        {
            "name": "History",
            "description": "Good for answering history questions",
            "prompt_template": history_template
        },
    ]

    return prompt_infos

#################################### Define the destination chains ####################################
def Destination_Chains(prompt_infos):

    destination_chains = {}
    for p_info in prompt_infos:
        name = p_info["name"]
        prompt_template = p_info["prompt_template"]
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        destination_chains[name] = chain

    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)

    return destination_chains,destinations_str

#################################### Define a Default Prompt & Chain ####################################
def Default_Prompt():

    default_prompt = ChatPromptTemplate.from_template("{input}")
    default_chain = LLMChain(llm=llm, prompt=default_prompt)
    return default_chain

################### Define a Multi-Prompt Router Template & Router Template & Prompt ###################
def Router_Templates(destinations):

    MULTI_PROMPT_ROUTER_TEMPLATE = """
    Given a raw text input to a language model, select the model prompt that is best suited for the input.
    You will be given the names of the available prompts and a description of what the prompt is best suited for.
    You may also revise the original input if you think that revising it will ultimately lead to a better response from the language model.

    REMEMBER: "destination" MUST be one of the candidate prompt names specified below OR it can be "DEFAULT" if the input is not well suited for any of the candidate prompts.
    REMEMBER: "next_inputs" can just be the original input if you don't think any modifications are needed.

    << FORMATTING >>
    Return a markdown code snippet with a JSON object formatted to look like:
    ```json
    {{{{
        "destination": string \ name of the prompt to use or "DEFAULT"
        "next_inputs": string \ a potentially modified version of the original input
    }}}}
    ```
    << CANDIDATE PROMPTS >>
    {destinations}

    << INPUT >>
    {{input}}

    << OUTPUT >>
    """

    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations)
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser())

    return router_prompt

#################################### Define a Router Chain & Chain ####################################
def Router_chains(router_prompt,destination_chains,default_chain):

    llm_api = ChatOpenAI(temperature=0)
    router_chain = LLMRouterChain.from_llm(llm_api, router_prompt)
    chain = MultiPromptChain(router_chain=router_chain,
                             destination_chains=destination_chains,
                             default_chain=default_chain, verbose=False)

    return chain

#################################### Input Question ####################################
def Input_Question(topic,language):

    if language == 'English':
        st.subheader("Provide a question that is relevant to the specific topic that you chose!")
        user_input = st.text_input("")
    elif language == 'Français':
        st.subheader("Donner une question pertinente sur le sujet spécifique que vous avez choisi!")
        user_input = st.text_input("Donner une question pertinente sur le sujet spécifique que vous avez choisi!")
    elif language == 'عربي':
        st.subheader("قدم سؤالًا ذا صلة بالموضوع الذي اخترته")
        user_input = st.text_input("")

    relevance_question = f"is {user_input} a {topic} topic?"
    format_instructions = f"""
    Make sure that {user_input} is a {topic} topic
    Reply by Yes or No only

    << OUTPUT >>
    """

    # Create a submit button
    if st.button("Submit"):
        st.write("Query submitted. This may take a minute while we search the database............")
        st.write("--------------------------------------------------------------------------------")
        chat = ChatOpenAI(temperature=0)
        relevance_chat = ChatPromptTemplate.from_template(template=format_instructions)
        relevance_format = relevance_chat.format_messages(text=relevance_question,
                                                          format_instructions=format_instructions)
        response = chat(relevance_format).content.split('\n')

        if response[0] == 'No':
            topic_relevance = False

            if language == 'English':
                st.subheader("Please write a question that is relevant to the topic you chose!")
                st.write("Try again!")
            elif language == 'Français':
                st.subheader("Veuillez écrire une question pertinente par rapport au sujet que vous avez choisi!")
                st.write("Essayez à nouveau!")
            elif language == 'عربي':
                st.subheader("يرجى كتابة سؤال متعلق بالموضوع الذي اخترته")
                st.write("حاول مرة أخرى")

            return user_input,topic_relevance,language

        else:
            topic_relevance = True
            return user_input,topic_relevance,language
    else:
        topic_relevance = False
        return user_input,topic_relevance,language

#################################### Response ####################################
def Question_reply(language,question):

    if language == 'English':
        st.write(f"The answer to your question '{question}' is:")
        st.caption('-'*120)
    elif language == 'Français':
        print(f"La réponse a votre question '{question}' est:")
        st.caption('-'*120)
    elif language == 'عربي':
        print(f"{question}الجواب على سوآلك : ")
        st.caption('-'*120)

#################################### Run Chain ####################################
def Run_Chain(question,chain):
    answer = chain.run(question)
    return answer


#################################### Run module ####################################
def Run_module():
    def Question_relevance():

        art_template, math_template, history_template = Topic_Template(language)
        prompt_infos = Define_Topic(art_template, math_template, history_template)
        destination_chains,destinations = Destination_Chains(prompt_infos)

        default_chain = Default_Prompt()
        router_prompt = Router_Templates(destinations)
        chain = Router_chains(router_prompt,destination_chains,default_chain)
        answer = Run_Chain(question,chain)
        Question_reply(language, question)
        st.write(answer)
        st.caption('-'*120)

    language = change_language()
    topic,language = Choose_Topic(language)
    topic_relevance = False
    question,topic_relevance,language = Input_Question(topic,language)
    if topic_relevance:
        Question_relevance()

#################################### Execute model ####################################
Run_module()