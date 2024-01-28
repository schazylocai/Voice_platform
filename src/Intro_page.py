import streamlit as st
import smtplib
import re
import os

video_url_doc = "https://youtu.be/zx5rGXgYCLw"
video_url_web = "https://youtu.be/aVZyQoH1PT8"
video_url_youtube = "https://youtu.be/fTfgycMftFk"
video_url_excel = "https://youtu.be/j2grzjwLkmA"

if 'user_status' not in st.session_state:
    st.session_state.user_status = 'False'

if 'language' not in st.session_state:
    st.session_state.language = 'English'


def write_english_About():

    violet = "rgb(169, 131, 247)"
    red = "rgb(232,89,83)"
    white = "rgb(255,255,255)"

    # section 2
    col1, col2 = st.columns(2)

    with col1:
        st.write(":red[Unlock the Power of ] :blue[OpenAI GPT].")
        st.header(
            ":violet[Welcome to GPT Analyzer, a revolutionary application that leverages the capabilities of Large Language Models.]")

    with col2:
        st.write(":red[What can this model do for you?]")
        st.subheader(
            ":violet[With this cutting-edge tool, you can effortlessly upload documents, excel files, web links, or YouTube videos to interact with them like never before.]")
        st.write(
            ":violet[Pose questions, extract valuable information, analyze content, and generate concise summaries.]")

    # st.divider()
    #
    # col1, col2, col3, col4 = st.columns(4)
    #
    # with col1:
    #     # st.image('gpt_logos/GPTdoc.png')
    #     change_text_style_english("GPTdoc", 'title', red)
    # with col2:
    #     # st.image('gpt_logos/GPTweb.png')
    #     change_text_style_english("GPTweb", 'title', red)
    # with col3:
    #     # st.image('gpt_logos/GPTyoutube.png')
    #     change_text_style_english("GPTyoutube", 'title', red)
    # with col4:
    #     # st.image('gpt_logos/GPTexcel.png')
    #     change_text_style_english("GPTexcel", 'title', red)

    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.video(video_url_doc)
    with col2:
        st.video(video_url_web)
    with col3:
        st.video(video_url_youtube)
    with col4:
        st.video(video_url_excel)

    # section 3
    st.divider()
    st.header(":violet[Subscription details]")
    st.subheader(":violet[Full access: $15 USD/Month + 1 day free trial period upon subscription]")
    st.write(
        ":violet[Cancellation must be initiated before the 1-day trial period elapses if you do not wish to continue.]")

    def Terms():
        # # section 4
        # with st.expander(":violet[Q&A / Tips]"):
        #     st.write(":violet[A- What is GPT-Doc Analyzer?]")
        #     st.caption(
        #         "GPT-Doc Analyzer is a tool that uses large language models GPT4 to analyze and summarize documents. It can be used to extract key insights from documents, identify important topics, and generate summaries that are both accurate and concise.")
        #     st.write(":violet[B- How does GPT-Doc Analyzer work?]")
        #     st.caption(
        #         "GPT-Doc Analyzer uses a large language model to process the text of a document. The language model is trained on a massive dataset of text and code, and it can learn to recognize patterns and relationships in language. This allows the language model to extract key insights from documents, identify important topics, and generate summaries that are both accurate and concise.")
        #     st.write(":violet[C- What are the benefits of using GPT-Doc Analyzer?]")
        #     st.caption("There are many benefits to using GPT-Doc Analyzer, including:")
        #     st.caption(
        #         "• Increased productivity: GPT-Doc Analyzer can help you to save time by automating the process of analyzing and summarizing documents.")
        #     st.caption(
        #         "• Improved accuracy: GPT-Doc Analyzer can help you to produce more accurate summaries by identifying the most important information in a document.")
        #     st.caption(
        #         "• Better insights: GPT-Doc Analyzer can help you to gain new insights into documents by identifying patterns and relationships in the text.")
        #     st.write(":violet[D- How can I use GPT-Doc Analyzer?]")
        #     st.caption(
        #         "GPT-Doc Analyzer is easy to use. Simply upload a document to the website, ask a question related to the uploaded document, and GPT-Doc Analyzer will analyze the document.")
        #     st.write(":violet[E- What are the limitations of GPT-Doc Analyzer?]")
        #     st.caption(
        #         "GPT-Doc Analyzer is a powerful tool, but it has some limitations. It is not able to handle all types of documents. Here are some specific limitations to keep in mind:")
        #     st.caption(
        #         "• As a general rule, the uploaded documents should contain images that do not exceed 40% of the total content.")
        #     st.caption("• If the document hangs and stops from uploading, then delete it and try again.")
        #     st.caption(
        #         "• This model is suitable for research papers, text-based documents, and not illustrative books and stories.")
        #     st.write(":violet[F- Here are some tips for using GPT-Doc Analyzer]")
        #     st.caption("• Choose documents that are well-written and easy to understand.")
        #     st.caption("• Avoid documents that are too long or too complex.")
        #     st.caption(
        #         "• If you are not sure if a document is suitable for GPT-Doc Analyzer, try uploading a small portion of it first.")

        with st.expander(":violet[Privacy Policy]"):
            st.caption(
                "We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy outlines how we collect, use, and protect the data you provide to us when using our machine learning algorithm for document processing. Please read this policy carefully to understand our practices regarding your personal data.")
            st.write(":violet[Collection of Personal Information:]")
            st.caption(
                "When you use our website and upload your documents, we may collect certain personal information, such as your name and email address, to provide you with the requested services.We do not store your documents or any processed data permanently. The documents are only kept in memory during your session and are deleted immediately afterward.")
            st.write(":violet[Use of Personal Information]")
            st.caption(
                "We use the personal information collected to operate and improve our machine learning algorithm, provide customer support, and communicate with you regarding your account and subscriptions.We do not have access to or view your uploaded documents. Your privacy and the confidentiality of your data are of utmost importance to us.")
            st.write(":violet[Security Measures:]")
            st.caption(
                "We take appropriate security measures to protect your personal information from unauthorized access, alteration, or disclosure.Our website is secured with SSL encryption to ensure the confidentiality of your data during transmission.")

        with st.expander(":violet[Terms of Service]"):
            st.caption(
                "These Terms of Service outline the agreement between us and the users of our machine learning algorithm for document processing. By accessing or using our website and services, you agree to abide by these terms.")
            st.write(":violet[Service Usage:]")
            st.caption(
                "Our machine learning algorithm allows users to upload and process their documents for querying or summarization purposes.The algorithm's performance may vary based on the quality and complexity of the input documents.")
            st.write(":violet[Payment and Subscriptions]")
            st.caption(
                "To access our services on a monthly basis, users are required to subscribe and make the necessary payments through a secure payment website. Payments are non-refundable unless explicitly stated otherwise.")
            st.write(":violet[Intellectual Property:]")
            st.caption(
                "All intellectual property rights associated with our machine learning algorithm, including any software, code, or documentation, are our property. Users are prohibited from copying, modifying, distributing, or reverse-engineering the algorithm.")
            st.write(":violet[Limitation of Liability:]")
            st.caption(
                "We are not liable for any direct or indirect damages arising from the use or inability to use our services, including but not limited to loss of data, revenue, or profits. Our services are provided 'as is' without any warranties or guarantees.")

    st.write("")
    st.write("")
    Terms()

    def contact_us_form():

        with st.expander(':violet[Contact Us!]'):
            sender_name = st.text_input(':violet[Name]', key='name')
            sender_email = st.text_input(':violet[Email]', key='email')
            sender_message = st.text_area(':violet[Message]', key='message')
            submitted = st.button(':red[Submit]')

            def is_valid_email(sender_email):
                # Use a regular expression pattern to validate the email address format
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                return re.match(pattern, sender_email) is not None

            if submitted:
                if sender_name.strip() == '':
                    st.error(':red[Enter your name!]')
                elif sender_email.strip() == '':
                    st.error(':red[Enter your email!]')
                elif not is_valid_email(sender_email.strip()):
                    st.error(':red[Enter a valid email address!]')
                elif sender_message.strip() == '':
                    st.error(':red[Enter a message!]')
                else:
                    send_email_eng(sender=sender_name, recipient=os.environ["MY_EMAIL_ADDRESS"],
                                   subject="Contact Form Submission", body=sender_message, sender_email=sender_email)
                    st.success(':violet[Form submitted successfully. We will get back to you as soon as possible!]')

    contact_us_form()

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")


def send_email_eng(sender, recipient, subject, body, sender_email):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(recipient, os.environ["EMAIL_PASSWORD"])
        server.sendmail(sender, recipient, f"Subject: {subject}\n\n{sender}: {sender_email}\n\n{body}")