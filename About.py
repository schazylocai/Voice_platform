import streamlit as st
import json
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from azure.storage.blob import BlobServiceClient
from validate_email import validate_email
import stripe
from pages.GPTapp import second_page

st.set_page_config(layout="wide")
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

video_url = "https://www.youtube.com/watch?v=YXpdalfhgoQ"

def first_page():
    #global status, valid_email
    status = False
    valid_email = False

    def intro():
        st.title(":red[GPT Document Analyzer]") # blue, green, orange, red, violet.
        st.write("")
        st.write("")
        st.write("")
        st.write("")

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

        st.title(":red[Subscription details:]")
        st.subheader(":violet[Full access: $15 USD/Month]")
        st.write(":violet[Subscribe today to unlock the full potential of our AI model. As a special bonus, you'll enjoy a 1-day free trial period to thoroughly test its capabilities. Only if you decide to continue after the trial, your subscription will be billed at $15 USD per month.]")
        st.title(":red[Let's start!]")
        # user_email_input = st.text_input("🗝️ :violet[...Enter your email address to subscribe or to cancel your subscription:]")
        # st.subheader(" 💎 :violet[...Click the submit button to proceed to a secure payment channel:]")

    # Run Intro
    user_email = intro()

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
        payment_link = "https://buy.stripe.com/test_fZe9APbAraUZ3HqfYZ"

        # Initialize Stripe payment
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": stripe_api_key,
                    "quantity": 1
                }
            ],
            mode="subscription",
            #success_url=payment_link,
            success_url="https://gptdocanalyzer.azurewebsites.net/GPTapp",
            cancel_url="https://gptdocanalyzer.azurewebsites.net/"
        )

        # Get the payment link from the Stripe Checkout Session
        payment_link = session.url

        # Redirect the user to the payment portal
        if st.button(":violet[Proceed to Payment]"):
            # Redirect the user to the payment portal
            st.markdown(f'<meta http-equiv="refresh" content="0;url={payment_link}" />', unsafe_allow_html=True)

    run_stripe()

    # # Start the process
    # if st.button(":red[Submit]"):
    #     st.session_state["user_email"] = user_email
    #     if validate_email(user_email):
    #         #st.write("The email address is valid.")
    #         valid_email = True
    #
    #         if valid_email:
    #             # Write user_id and status to subscription_ids
    #             run_stripe()
    #             # status = False
    #             # valid = False
    #             #write_subscription_ids_to_azure_blob()
    #             # return status
    #
    #     else:
    #         st.write(":red[Please enter a valid email address.]")
    #         valid = False
    #         status = False
    #         return  status

        #ids = read_subscription_from_azure_blob()

if __name__ == '__main__':
    subscription_valid = first_page()