import streamlit as st
import json
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from azure.storage.blob import BlobServiceClient
import stripe

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
    #global status, valid_email
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
        col1, col2 = st.columns(2)
        with col1:
            st.header(":red[Subscription details:]")
            st.subheader(":violet[Full access: $15 USD/Month]")
            st.write(
                ":violet[Subscribe today to unlock the full potential of our AI model. As a special bonus, you'll enjoy a 1-day free trial period to thoroughly test its capabilities. Only if you decide to continue after the trial, your subscription will be billed at $15 USD per month.]")

            st.header(":red[Let's start!]")

    # Run Intro
    intro()

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

    def read_subscription_from_azure_blob():
        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Specify the container and blob name
        container_name = "llmidcontainer"
        blob_name = "subscriptionids.json"

        # Check if the blob exists
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.get_blob_client(blob_name).exists():
            st.write("Please subscribe!")
            return None

        # Download the blob content
        blob_content = container_client.download_blob(blob_name).readall()

        # Decode and return the subscription data
        return json.loads(blob_content.decode("utf-8"))

    def write_subscription_ids_to_azure_blob():
        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a container
        container_name = "llmidcontainer"
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        # Create a blob client
        blob_name = "subscriptionids.json"
        blob_client = container_client.get_blob_client(blob_name)

        # Check if the blob exists
        if blob_client.exists():
            # Download the existing blob content
            existing_content = blob_client.download_blob().readall()

            # Append new data to the existing content
            existing_data = json.loads(existing_content.decode("utf-8"))
            new_data = [{"user_email": user_email, "status": status}]
            combined_data = existing_data + new_data

            # Convert the combined data to JSON
            updated_content = json.dumps(combined_data)

            # Upload the updated content to the blob
            blob_client.upload_blob(updated_content, overwrite=True)
        else:
            # Prepare the subscription data
            subscription_data = [{"user_email": user_email, "status": status}]
            subscription_ids = json.dumps(subscription_data)
            # Write the subscription IDs to the blob (since it doesn't exist yet)
            blob_client.upload_blob(subscription_ids, overwrite=True)

    def run_stripe():
        # Set your Stripe API keys
        stripe.api_key = strip_secret_key

        # Redirect the user to the payment portal
        st.button(":violet[Proceed to Payment]")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        Terms()

        if st.button:
            # Redirect the user to the payment portal
            st.markdown(f'<meta http-equiv="refresh" content="0;url={payment_link}" />', unsafe_allow_html=True)

            # Initialize Stripe payment
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": stripe_api_key, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url)

    run_stripe()

if __name__ == '__main__':
    first_page()