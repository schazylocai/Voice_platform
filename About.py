import streamlit as st
import json
import os
from azure.storage.blob import BlobServiceClient

st.set_page_config(layout="wide")


def first_page():
    st.subheader('Subscription page')

    def read_subscription_from_azure_blob():
        # Read the Azure connection string from environment variables
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

        # Create a blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Specify the container and blob name
        container_name = "llm_id_container"
        blob_name = "subscription_ids.json"

        # Check if the blob exists
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        if not blob_client.exists():
            st.write("Please subscribe!")
            return None

        # Download the blob content
        blob_content = blob_client.download_blob().readall()

        # Decode and return the subscription data
        subscription_data = json.loads(blob_content.decode("utf-8"))

        return subscription_data

    ids = read_subscription_from_azure_blob()
    st.write(ids)

    user_email = st.text_input("Enter your email_id:")
    if st.button("Submit"):
        valid = True

        if valid:
            st.write('subscribed')
            # write user_id and status to subscription_ids
            status = True

            def write_subscription_ids_to_azure_blob(subscription_ids, connection_string):

                # Create a blob service client
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)

                # Create a container
                container_name = "llm_id_container"
                if not blob_service_client.get_container_client(container_name).exists():
                    blob_service_client.create_container(container_name)

                # Create a blob client
                blob_name = "subscription_ids.json"
                blob_client = blob_service_client.get_blob_client(container=container_name,blob=blob_name)

                # Write the subscription IDs to the blob
                blob_client.upload_blob(subscription_ids, overwrite=True)


            # Read the Azure connection string from environment variables
            connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

            # Prepare the subscription data
            subscription_data = [{"user_email": user_email,"status": status}]
            subscription_ids = json.dumps(subscription_data)

            # Write the subscription IDs to the Azure blob
            write_subscription_ids_to_azure_blob(subscription_ids, connection_string)

        else:

            st.write('Please subscribe to continue.')
            valid = False

        return valid

if __name__ == '__main__':
    subscription_valid = first_page()