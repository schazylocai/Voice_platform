import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv() # read local .env file
import stripe
import webbrowser
from datetime import datetime
import os
from Azure_storage import write_subscription_ids_to_azure_blob,read_subscription_from_azure_blob

#payment_link = "https://buy.stripe.com/test_fZe9APbAraUZ3HqfYZ"
success_url="https://gptdocanalyzer.azurewebsites.net/GPTapp"
cancel_url="https://gptdocanalyzer.azurewebsites.net/"
user_email = ""

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
stripe_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

subscribed_user = 'False'
stripe.api_key = stripe_secret_key

def get_days_left(subscription):
    current_timestamp = datetime.now().timestamp()
    current_period_end = subscription['data'][0]['current_period_end']
    return max(0, int((current_period_end - current_timestamp) / (24 * 3600)))

def check_customers():

    user = False
    username = ''

    # Check customers
    st.sidebar.title(":red[Login to start!]")
    email = st.sidebar.text_input(":violet[Please enter your email address:]",key='email_add')
    email = email.strip().lower()
    password = st.sidebar.text_input(":violet[Enter your password]", key='password_add')
    password = password.strip()

    if len(email) == 0:
        st.sidebar.write(":blue[Enter your email]")

    else:
        if email_button := st.sidebar.button(":red[Submit]",key='submit_add'):

            if len(password) < 4:
                st.sidebar.write(":red[Enter a valid password]")

            else:

                customers = stripe.Customer.list()

                if len(customers.data) > 0:
                    customer = customers.data[0]
                    username = customer.email

                    if username == email:

                        # Check password
                        username_azure,password_azure = read_subscription_from_azure_blob(username)
                        if password == password_azure:

                            # Check subscription
                            subscriptions = stripe.Subscription.list(customer=customer.id)

                            if len(subscriptions.data) > 0:
                                st.sidebar.write(':violet[Subscription is valid!]')
                                customer_id = customer.id
                                subscription = stripe.Subscription.list(customer=customer_id)
                                days_left = get_days_left(subscription)

                                if subscription['data'][0]['cancel_at_period_end']:
                                    st.sidebar.write(f":red[Subscription will be canceled in {days_left} days.]")
                                else:
                                    st.sidebar.write(f":red[{days_left} days left for this month.]")

                                st.sidebar.subheader(':red[Click up on GPTapp to proceed.]')
                                user = True

                        else: st.write(":red[Incorrect password]")

                    else:
                        st.sidebar.write(':red[Subscription is not valid!]')
                        user = False

                else:
                    st.sidebar.write(':red[You are not subscribed to this service!]')
                    user = True

    return user


def subscribe_to_service():

    def proceed_to_payment():

        # if pay := st.sidebar.button(":blue[Proceed to Payment]", key='proceed_payment'):
            # Initialize Stripe payment
        session = stripe.checkout.Session.create(
            api_key=stripe_secret_key,
            payment_method_types=["card"],
            line_items=[{"price": stripe_api_key, "quantity": 1}],
            mode="subscription",
            success_url=cancel_url,
            cancel_url=cancel_url)

        # Redirect the user to the payment portal
        webbrowser.open(url=session.url, new=0)


    def subscribe_menu():

        username = ''

        st.sidebar.divider()
        st.sidebar.title(":red[Want to subscribe?]")
        # Check if customer exists
        email = st.sidebar.text_input(":violet[Enter your email address]", key='email_check')
        email = email.strip().lower()
        password = st.sidebar.text_input(":violet[Create a password and save it]", key='password_check')
        password = password.strip()

        if len(email) == 0:
            st.sidebar.write(":blue[Enter your email]")

        else:
            if email_button := st.sidebar.button(":red[Submit]", key='submit_email_check'):
                customers = stripe.Customer.list()
                if len(customers.data) > 0:
                    customer = customers.data[0]
                    username = customer.email

                if username == email:
                    st.sidebar.write(":red[User already exists. Please login!]")

                else:
                    if len(password) < 4:
                        st.sidebar.write(":red[Enter a valid password]")
                        st.sidebar.write(":red[Password should be at least 4 numbers/characters)]")

                    else:
                        proceed_to_payment()
                        write_subscription_ids_to_azure_blob(email, password)

    subscribe_menu()


def cancel_service():

    username = ''

    # Cancel subscription to the service
    st.sidebar.divider()
    st.sidebar.subheader(":blue[Cancel subscription?]")
    # Check if customer exists
    email = st.sidebar.text_input(":red[Please enter your email address:]",key='email_cancel')
    email = email.strip().lower()
    password = st.sidebar.text_input(":violet[Enter your password]", key='password_cancel')
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
                    customer = customers.data[0]
                    username = customer.email

                    if username == email:
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
                        st.sidebar.write(":red[Customer doesn't exist]")
                else:
                    st.sidebar.write(':red[No active subscription found!]')

    st.sidebar.divider()
    return subscribed_user