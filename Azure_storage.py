import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from azure.storage.blob import BlobServiceClient
import json

connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
container_name = "llmidcontainer"
blob_name = "subscriptionids.json"

def read_subscription_from_azure_blob(username):
    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Check if the blob exists
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.get_blob_client(blob_name).exists():
        st.write(":red[No data found!]")
        return None

    else:
        # Download the blob content
        blob_content = container_client.download_blob(blob_name).readall()

        # Decode and return the subscription data

        subscription_data = json.loads(blob_content.decode("utf-8"))

        for user in range(len(subscription_data)):

            if username == subscription_data[user]['user_email']:
                username = subscription_data[user]["user_email"]
                password = subscription_data[user]["password"]

                return username, password


def write_subscription_ids_to_azure_blob(user_email,password):
    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a container
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # Create a blob client
    blob_client = container_client.get_blob_client(blob_name)

    # Check if the blob exists
    if blob_client.exists():
        # Download the existing blob content
        existing_content = blob_client.download_blob().readall()

        # Append new data to the existing content
        existing_data = json.loads(existing_content.decode("utf-8"))
        new_data = [{"user_email": user_email, "password": password}]
        combined_data = existing_data + new_data

        # Convert the combined data to JSON
        updated_content = json.dumps(combined_data)

        # Upload the updated content to the blob
        blob_client.upload_blob(updated_content, overwrite=True)
    else:
        # Prepare the subscription data
        subscription_data = [{"user_email": user_email, "password": password}]
        subscription_ids = json.dumps(subscription_data)
        # Write the subscription IDs to the blob (since it doesn't exist yet)
        blob_client.upload_blob(subscription_ids, overwrite=True)

    return user_email,password