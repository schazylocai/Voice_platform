import streamlit as st
from dotenv import load_dotenv
load_dotenv() # read local .env file
import stripe
from datetime import datetime
import os
from Azure_storage import write_subscription_ids_to_azure_blob,read_subscription_from_azure_blob

success_url="https://gptdocanalyzer.com/"
cancel_url="https://gptdocanalyzer.com/"
user_email = ""

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
stripe_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

subscribed_user = 'False'
stripe.api_key = stripe_secret_key
endpoint_secret = 'whsec_eac84f5766a6c4217bf122ac3bdde25880776a36172ae67ff80ec9a347a5222b'

def get_days_left(subscription):
    current_timestamp = datetime.now().timestamp()
    current_period_end = subscription['data'][0]['current_period_end']
    return max(0, int((current_period_end - current_timestamp) / (24 * 3600)))


def check_customers():

    user = False
    username = ''

    # Check customers
    st.sidebar.write("")
    st.sidebar.title(":red[Login to start!]")
    email = st.sidebar.text_input(":violet[Please enter your email address:]",key='email_add')
    email = email.strip().lower()
    password = st.sidebar.text_input(":violet[Enter your password]", key='password_add', type='password')
    password = password.strip()

    if len(email) == 0:
        st.sidebar.write(":blue[Enter your email]")

    elif email_button := st.sidebar.button(":red[Submit]",key='submit_add'):

        if len(password) < 4:
            st.sidebar.write(":red[Enter a valid password]")

        else:
            customers = stripe.Customer.list()

            if len(customers.data) > 0:
                for user in range(len(customers.data)):

                    customer = customers.data[user]
                    username = customer.email.strip().lower()

                    if username == email:

                        # Check password
                        username_azure,password_azure = read_subscription_from_azure_blob(username)
                        if password_azure == password:

                            # Check subscription
                            subscriptions = stripe.Subscription.list(customer=customer.id)
                            status = stripe.Subscription.list(customer=customer.id)['data'][0]['status']

                            if status in ['active', 'canceled']:
                                st.sidebar.write(':violet[Subscription is valid!]')
                                customer_id = customer.id
                                subscription = stripe.Subscription.list(customer=customer_id)
                                days_left = get_days_left(subscription)

                                if subscription['data'][0]['cancel_at_period_end']:
                                    st.sidebar.write(f":red[Subscription will be canceled in {days_left} days.]")
                                else:
                                    st.sidebar.write(f":violet[{days_left} days left for this month.]")

                                if days_left == 0 and status == 'canceled':
                                    st.sidebar.write(':red[Subscription period ended after cancellation!]')
                                    user = False
                                else:
                                    st.sidebar.title(':blue[Click at the top of this page ] :red[GPTapp]:blue[ tab to start...]')
                                    user = True

                            elif status in ['trialing']:
                                st.sidebar.write(':red[Subscription is on trial mode!]')

                            else:
                                st.sidebar.write(':red[No active subscription found!]')

                        else: st.sidebar.write(":red[Incorrect password]")

                    if email == os.environ['ADMIN_EMAIL'] and password == os.environ['ADMIN_PASSWORD']:
                        user = True

            else:
                st.sidebar.write(':red[You are not subscribed to this service!]')
                user = True

    return user


def subscribe_to_service():

    username = ''
    def proceed_to_payment():

        # Open stripe session
        session = stripe.checkout.Session.create(
            api_key=stripe_secret_key,
            payment_method_types=["card"],
            line_items=[{"price": stripe_api_key, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data = {'trial_period_days': 1})

        # Create a clickable link to the payment URL
        pay_link = f'<a href="{session.url}" target="_blank">Click here to proceed to payment!</a>'
        st.sidebar.write(pay_link, unsafe_allow_html=True)

    st.sidebar.divider()
    st.sidebar.title(":violet[Want to subscribe?]")
    # Check if customer exists
    email = st.sidebar.text_input(":violet[Enter your email address]", key='email_check')
    email = email.strip().lower()
    password = st.sidebar.text_input(":violet[Create a password and save it]", key='password_check', type='password')
    password = password.strip()

    if len(email) == 0:
        st.sidebar.write(":blue[Enter your email]")

    else:
        if email_button := st.sidebar.button(":red[Submit]", key='submit_email_check'):
            customers = stripe.Customer.list()
            if len(customers.data) > 0:
                customer = customers.data[0]
                username = customer.email.strip().lower()

                if username == email:
                    st.sidebar.write(":red[User already exists. Please login!]")

            if len(password) < 4:
                st.sidebar.write(":red[Enter a valid password]")
                st.sidebar.write(":red[Password should be at least 4 numbers/characters)]")

            else:
                # Write email & password to Azure blob
                email, password = write_subscription_ids_to_azure_blob(email, password)

                # Proceed to pay
                proceed_to_payment()

    return email,password


def cancel_service():

    username = ''

    # Cancel subscription to the service
    st.sidebar.divider()
    st.sidebar.subheader(":violet[Cancel subscription?]")
    # Check if customer exists
    email = st.sidebar.text_input(":violet[Please enter your email address:]",key='email_cancel')
    email = email.strip().lower()
    password = st.sidebar.text_input(":violet[Enter your password]", key='password_cancel', type='password')
    password = password.strip()

    if len(email) == 0:
        st.sidebar.write(":blue[Enter your email]")

    else:
        if email_button_cancel := st.sidebar.button(":red[Submit]",key='submit_cancel'):

            if len(password) < 4:
                    st.sidebar.write(":red[Enter a valid password]")

            else:
                customers = stripe.Customer.list()

                if len(customers.data) > 0:

                    for user in range(len(customers.data)):

                        customer = customers.data[user]
                        username = customer.email.strip().lower()

                        if username == email:

                            # Check password
                            username_azure, password_azure = read_subscription_from_azure_blob(username)
                            if password_azure == password:

                                subscriptions = stripe.Subscription.list(customer=customer.id)

                                if len(subscriptions.data) > 0:
                                    customer_id = customer.id
                                    subscription = stripe.Subscription.list(customer=customer_id)
                                    days_left = get_days_left(subscription)
                                    subscription_id = subscription['data'][0]['id']
                                    stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)

                                    if days_left == 1:
                                        stripe.Subscription.delete(subscription_id)

                                    st.sidebar.write(':violet[Subscription cancelled successfully for the next billing cycle!]')
                                    st.sidebar.write(f":red[{days_left} days left in the current subscription period.]")

                                else:
                                    st.sidebar.write(':red[No active subscription found!]')

                            else:
                                st.sidebar.write(":red[Incorrect password]")

                else:
                    st.sidebar.write(':red[No active subscription found!]')

    st.sidebar.divider()
    return subscribed_user