import streamlit as st
import os

import azure.identity
import azure.keyvault.secrets
import re

from dotenv import load_dotenv
load_dotenv()  # read local .env file

tenant_id = os.environ["AZURE_TENANT_ID"]
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]
keyvault_name = os.environ["AZURE_KEYVAULT_NAME"]
keyvault_uri = os.environ["AZURE_KEYVAULT_URI"]

_credential = azure.identity.ClientSecretCredential(tenant_id=tenant_id, client_id=client_id,
                                                    client_secret=client_secret)
client = azure.keyvault.secrets.SecretClient(vault_url=keyvault_uri, credential=_credential)


def read_subscription_from_azure_keyvault(user_email, user_password):
    try:
        # Clean the user_email to use it as the secret name
        username = re.sub(r'\W+', '', user_email)
        # Check if the secret already exists in the Key Vault
        try:
            existing_secret = client.get_secret(username)
            existing_password = existing_secret.value
            return user_email, existing_password

        except Exception as ex:
            # If the secret doesn't exist, write it to the Key Vault
            return user_email, user_password

    except Exception as e:
        st.write(":red[Error retrieving data from Azure Key Vault!]")
        return None, None


def write_subscription_ids_to_azure_keyvault(user_email, user_password):
    try:
        # Clean the user_email to use it as the secret name
        username = re.sub(r'\W+', '', user_email)

        # Check if the secret already exists in the Key Vault
        try:
            existing_secret = client.get_secret(username)
            return 'exists', 'exists'

        except Exception as ex:
            # If the secret doesn't exist, write it to the Key Vault
            secret = client.set_secret(username, user_password)
            st.sidebar.write(":violet[Credentials saved!]")

        return user_email, user_password

    except Exception as e:
        st.write(f":red[Error writing data to Azure Key Vault: {e}]")
        return None, None


def retrieve_password_from_azure_keyvault(user_email):
    try:
        # Clean the user_email to use it as the secret name
        username = re.sub(r'\W+', '', user_email)
        # Check if the secret already exists in the Key Vault
        try:
            existing_secret = client.get_secret(username)
            existing_password = existing_secret.value
            return existing_secret, existing_password

        except Exception as ex:
            # If the secret doesn't exist, write it to the Key Vault
            return user_email, "Password not found!"

    except Exception as e:
        st.write(":red[Error retrieving data from Azure Key Vault!]")
        return user_email, "Password not found!"

# connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
# container_name = "llmidcontainer"
# blob_name = "subscriptionids.json"
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# def read_subscription_from_azure_blob(username):
#
#     # Check if the blob exists
#     container_client = blob_service_client.get_container_client(container_name)
#     if not container_client.get_blob_client(blob_name).exists():
#         st.write(":red[No data found!]")
#         return None
#
#     else:
#         # Download the blob content
#         blob_content = container_client.download_blob(blob_name).readall()
#
#         # Decode and return the subscription data
#
#         subscription_data = json.loads(blob_content.decode("utf-8"))
#
#         for user in range(len(subscription_data)):
#
#             if username == subscription_data[user]['user_email']:
#                 username = subscription_data[user]["user_email"]
#                 password = subscription_data[user]["password"]
#
#                 return username, password
#
#
# def write_subscription_ids_to_azure_blob(user_email,password):
#
#     # Create a container
#     container_client = blob_service_client.get_container_client(container_name)
#     if not container_client.exists():
#         container_client.create_container()
#
#     # Create a blob client
#     blob_client = container_client.get_blob_client(blob_name)
#
#     # Check if the blob exists
#     if blob_client.exists():
#         # Download the existing blob content
#         existing_content = blob_client.download_blob().readall()
#
#         # Append new data to the existing content
#         existing_data = json.loads(existing_content.decode("utf-8"))
#         new_data = [{"user_email": user_email, "password": password}]
#         combined_data = existing_data + new_data
#
#         # Convert the combined data to JSON
#         updated_content = json.dumps(combined_data)
#
#         # Upload the updated content to the blob
#         blob_client.upload_blob(updated_content, overwrite=True)
#     else:
#         # Prepare the subscription data
#         subscription_data = [{"user_email": user_email, "password": password}]
#         subscription_ids = json.dumps(subscription_data)
#         # Write the subscription IDs to the blob (since it doesn't exist yet)
#         blob_client.upload_blob(subscription_ids, overwrite=True)
#
#     return user_email,password
#
#
# def upload_file_to_azure_blob(file):
#
#     file_path = os.path.join("..", file.name)
#     with open(file_path, "wb") as f:
#         f.write(file.getbuffer())
#
#     try:
#         # Get the BlobClient instance
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.name)
#         blob_client.upload_blob(file,overwrite=True)
#
#     except Exception as e:
#         st.sidebar.error(f"An error occurred while uploading the file: {str(e)}")
#
#
# def delete_file(files):
#
#     try:
#         # Get the BlobClient instance
#         for file in files:
#             blob_client = blob_service_client.get_blob_client(container=container_name, blob=files)
#             blob_client.delete_blob()
#
#     except Exception as e:
#         st.sidebar.error(f"An error occurred while deleting the local file: {str(e)}")
#
#
# def read_file_from_azure_blob(file):
#
#     try:
#         # Get the BlobClient instance
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.name)
#
#         # Download the file from Azure Blob Storage
#         file_contents = blob_client.download_blob()
#
#         return file_contents.name
#
#     except Exception as e:
#         st.error(f"An error occurred while reading the file: {str(e)}")


# # Read subscription from Azure Key Vault
# stored_username, stored_password = read_subscription_from_azure_keyvault(username)
# if stored_username is not None:
#     st.write("Retrieved subscription:")
#     st.write(f"Username: {stored_username}")
#     st.write(f"Password: {stored_password}")
# else:
#     st.write("No data found!")
#
# # Write subscription to Azure Key Vault
# stored_username, stored_password = write_subscription_ids_to_azure_keyvault(username, password)
# if stored_username is not None:
#     st.write("Successfully wrote subscription to Azure Key Vault:")
#     st.write(f"Username: {stored_username}")
#     st.write(f"Password: {stored_password}")
# else:
#     st.write("Error occurred while writing data to Azure Key Vault!")
