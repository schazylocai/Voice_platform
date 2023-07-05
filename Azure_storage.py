import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
from azure.storage.blob import BlobServiceClient
import json

connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
container_name = "llmidcontainer"
blob_name = "subscriptionids.json"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def read_subscription_from_azure_blob(username):

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


def upload_file_to_azure_blob(file):

    file_path = os.path.join(".", file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    try:
        # Get the BlobClient instance
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.name)
        #blob_client.upload_blob(file,overwrite=True)

    except Exception as e:
        st.sidebar.error(f"An error occurred while uploading the file: {str(e)}")


def delete_file(files_path):

    try:
        # Get the BlobClient instance
        st.write(files_path)
        for file_path in files_path:
            st.write(file_path)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path)
            blob_client.delete_blob()

    except Exception as e:
        st.sidebar.error(f"An error occurred while deleting the local file: {str(e)}")


def read_file_from_azure_blob(filename):

    try:
        # Get the BlobClient instance
        blob_client = blob_service_client.get_blob_client(container="<container_name>", blob=filename)

        # Download the file from Azure Blob Storage
        file_contents = blob_client.download_blob().readall()

        # Display the file contents
        st.write(file_contents)
    except Exception as e:
        st.error(f"An error occurred while reading the file: {str(e)}")

# Streamlit app
def start():

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    if uploaded_file is not None:
        upload_file_to_azure_blob(uploaded_file)

        # Delete the local file after upload
        delete_file(uploaded_file)

    # st.subheader("Read File from Azure Blob Storage")
    #
    # # List the files in the Azure Blob Storage container
    # blob_container_client = blob_service_client.get_container_client(container="<container_name>")
    # blob_list = [blob.name for blob in blob_container_client.list_blobs()]
    #
    # if len(blob_list) > 0:
    #     # Select a file to read
    #     selected_file = st.selectbox("Select a file", blob_list)
    #
    #     if st.button("Read File"):
    #         # Read the selected file from Azure Blob Storage
    #         read_file_from_azure_blob(selected_file)
    # else:
    #     st.info("No files available in Azure Blob Storage")