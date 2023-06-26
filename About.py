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
stripe_api_key = os.environ['PUBLISHABLE_KEY']
strip_secret_key = os.environ['STRIPE_SECRET_KEY']

def first_page():
    global valid, valid_email
    valid = False
    valid_email = False
    st.subheader('Subscription page')

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

    user_email = st.text_input("Enter your email_id:")

    if st.button("Submit"):
        if validate_email(user_email):
            st.write("The email address is valid.")
            valid_email = True

        if valid_email:
            st.write('Subscribed')
            # Write user_id and status to subscription_ids
            status = True
            valid = True

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

            write_subscription_ids_to_azure_blob()

        else:
            st.write("Please enter a valid email address.")
            valid = False

        ids = read_subscription_from_azure_blob()

        def run_stripe():
            # Set your Stripe API keys
            stripe_keys = {"SECRET_KEY": strip_secret_key,"publishable_key": stripe_api_key,}

            # Create a subscription plan
            subscription_plan = stripe.Subscription.create(
                api_key=stripe_api_key,
                name="Monthly Plan",
                billing_cycle="monthly",)

            # Create a button to subscribe to the plan
            st.button("Subscribe to Plan", on_click=lambda: stripe.Subscription.create(
                customer=st.session_state[user_email],
                plan=subscription_plan.id))

        run_stripe()
        return valid

if __name__ == '__main__':
    subscription_valid = first_page()