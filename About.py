import streamlit as st
import json
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from azure.storage.blob import BlobServiceClient
import stripe
import webbrowser

st.set_page_config(layout="wide",initial_sidebar_state='expanded',page_icon="🔬")
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

video_url = "https://www.youtube.com/watch?v=YXpdalfhgoQ"
payment_link = "https://buy.stripe.com/test_fZe9APbAraUZ3HqfYZ"
success_url="https://gptdocanalyzer.azurewebsites.net/GPTapp"
cancel_url="https://gptdocanalyzer.azurewebsites.net/"
user_email = ""

def first_page():
    status = False
    valid_email = False

    def intro():

        # section 1
        st.title(":red[GPT Document Analyzer]") # blue, green, orange, red, violet.
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        # section 2
        col1,col2,col3 = st.columns(3)

        with col1:
            st.write(":red[Unlock the Power of AI to Query Your Documents.]")
            st.subheader(":violet[Welcome to GPT Document Analyzer, a revolutionary application that leverages the capabilities of Large Language Models (GPT).]")

        with col2:
            st.write(":red[What can this model do for you?]")
            st.write(":violet[With this cutting-edge tool, you can effortlessly upload PDF documents and interact with them like never before. Pose questions, extract valuable information, analyze content, and generate concise summaries directly from your uploaded documents.]")
            st.write(":violet[➜ Watch the video to see how this model works!]")

        with col3:
            st.video(video_url)

        # section 3
        st.header(":red[Subscription details]")
        st.subheader(":violet[Full access: $15 USD/Month]")
        st.write(
            ":violet[Subscribe today to unlock the full potential of our AI model. As a special bonus, you'll enjoy a :red[1-day free trial period] to thoroughly test its capabilities. Only if you decide to continue after the trial, your subscription will be billed at $15 USD per month.]")

        def Terms():
            # section 4
            with st.expander(":violet[Privacy Policy]"):
                st.caption("We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy outlines how we collect, use, and protect the data you provide to us when using our machine learning algorithm for document processing. Please read this policy carefully to understand our practices regarding your personal data.")
                st.write(":violet[Collection of Personal Information:]")
                st.caption("When you use our website and upload your documents, we may collect certain personal information, such as your name and email address, to provide you with the requested services.We do not store your documents or any processed data permanently. The documents are only kept in memory during your session and are deleted immediately afterward.")
                st.write(":violet[Use of Personal Information]")
                st.caption("We use the personal information collected to operate and improve our machine learning algorithm, provide customer support, and communicate with you regarding your account and subscriptions.We do not have access to or view your uploaded documents. Your privacy and the confidentiality of your data are of utmost importance to us.")
                st.write(":violet[Security Measures:]")
                st.caption("We take appropriate security measures to protect your personal information from unauthorized access, alteration, or disclosure.Our website is secured with SSL encryption to ensure the confidentiality of your data during transmission.")

            with st.expander(":violet[Terms of Service]"):
                st.caption("These Terms of Service outline the agreement between us and the users of our machine learning algorithm for document processing. By accessing or using our website and services, you agree to abide by these terms.")
                st.write(":violet[Service Usage:]")
                st.caption("Our machine learning algorithm allows users to upload and process their documents for querying or summarization purposes.The algorithm's performance may vary based on the quality and complexity of the input documents.")
                st.write(":violet[Payment and Subscriptions]")
                st.caption("To access our services on a monthly basis, users are required to subscribe and make the necessary payments through a secure payment website. Payments are non-refundable unless explicitly stated otherwise.")
                st.write(":violet[Intellectual Property:]")
                st.caption("All intellectual property rights associated with our machine learning algorithm, including any software, code, or documentation, are our property. Users are prohibited from copying, modifying, distributing, or reverse-engineering the algorithm.")
                st.write(":violet[Limitation of Liability:]")
                st.caption("We are not liable for any direct or indirect damages arising from the use or inability to use our services, including but not limited to loss of data, revenue, or profits. Our services are provided 'as is' without any warranties or guarantees.")

        st.write("")
        st.write("")
        Terms()

    # Run Intro
    intro()

def run_subscription():
    subscribed_user = 'False'
    # Run stripe
    st.sidebar.title(":red[Want to subscribe?]")
    # Set your Stripe API keys
    stripe.api_key = strip_secret_key

    if pay := st.sidebar.button(":violet[Proceed to Payment]", key='payment'):
        # Initialize Stripe payment
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": stripe_api_key, "quantity": 1}],
            mode="subscription",
            success_url=cancel_url,
            cancel_url=cancel_url)

        payment_link_access = session.url

        # Redirect the user to the payment portal
        webbrowser.open(payment_link_access,new=0,autoraise=False)

    # Check customers
    st.sidebar.title(":red[Already subscribed?]")
    email = st.sidebar.text_input(":violet[Please enter your email address:]")

    if email_button := st.sidebar.button(":violet[Submit]"):
        customer = stripe.Customer.list(email='samuel.chazy@gmail.com')
        if len(customer.data) == 0:
            subscribed_user = 'True'

        else:
            st.sidebar.write(':red[You are not subscribed to this service!]')
            subscribed_user = 'False'

    return subscribed_user

first_page()
#run_subscription()
st.session_state.subscribed_status = run_subscription()