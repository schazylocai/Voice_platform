import streamlit as st
import json
import os

st.set_page_config(layout="wide")


def first_page():
    st.cache()
    st.subheader('Subscription page')
    user_email = st.text_input("Enter your email_id:")
    if submit_button := st.button("Submit"):
        valid = True
        if valid:
            st.write('subscribed')
            # write user_id and status to subscription_ids
            status = True

            def write_subscription_to_file(user_email,status):
                # Create a dictionary with the subscription data
                subscription_data = {"user_email": user_email, "status": status}

                # Open the file in write mode
                with open("data/subscription_ids.json", "r") as file:
                    try:
                        # Load existing data from the file
                        existing_data = json.load(file)
                    except json.JSONDecodeError:
                        existing_data = []

                # Append the new subscription data
                existing_data.append(subscription_data)

                # Open the file in write mode
                with open("data/subscription_ids.json", "w") as file:
                    # Write the updated data to the file
                    json.dump(existing_data, file, indent=4)

            write_subscription_to_file(user_email,status)

        else:
            st.write('Please subscribe to continue.')
            valid = False

        return valid

 # Open the file in write mode
if not os.path.exists(os.path.join("data","subscription_ids.json")):
    with open("data/subscription_ids.json","w") as file:
        # Write the dictionary to the file
        json.dump([{"user_email": "samuel.chazy@gmail.com", "status": True}],file,indent=4)

if __name__ == '__main__':
    subscription_valid = first_page()