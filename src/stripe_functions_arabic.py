import streamlit as st
from dotenv import load_dotenv
load_dotenv() # read local .env file
import stripe
from datetime import datetime
import os
import smtplib
from src.Azure_storage_arabic import write_subscription_ids_to_azure_keyvault_arabic,read_subscription_from_azure_keyvault_arabic,retrieve_password_from_azure_keyvault_arabic
from src.Change_Text_Style import change_text_style_arabic,change_text_style_english,change_text_style_arabic_side

success_url="https://gptdocanalyzer.com/"
cancel_url="https://gptdocanalyzer.com/"
user_email = ""

stripe_publishable_key = os.environ['STRIPE_PUBLISHABLE_KEY']
stripe_secret_key = os.environ['STRIPE_SECRET_KEY']
stripe_api_key = os.environ['STRIPE_API_KEY']

subscribed_user = 'False'
stripe.api_key = stripe_secret_key
endpoint_secret = 'whsec_eac84f5766a6c4217bf122ac3bdde25880776a36172ae67ff80ec9a347a5222b'

violet = "rgb(169, 131, 247)"
red = "rgb(232,89,83)"

def get_days_left(subscription):
    current_timestamp = datetime.now().timestamp()
    current_period_end = subscription['data'][0]['current_period_end']
    return max(0, int((current_period_end - current_timestamp) / (24 * 3600)))


def check_customers_ara():

    user = False
    username = ''

    # Check customers
    st.sidebar.write("")
    change_text_style_arabic_side("أدخل معلوماتك للبد ء !",'subhead_side_red',red)
    change_text_style_arabic_side("يرجى إدخال عنوان بريدك الإلكتروني", 'text_violet_side', violet)
    email = st.sidebar.text_input("email",key='email_add',label_visibility='collapsed')
    email = email.strip().lower()
    change_text_style_arabic_side("أدخل كلمة المرور", 'text_violet_side', violet)
    password = st.sidebar.text_input("password", type='password',label_visibility='collapsed')
    password = password.strip()

    if len(email) == 0:
        change_text_style_arabic_side("أدخل بريدك الإلكتروني", 'text_violet_side', violet)

    elif email_button := st.sidebar.button(":red[انقر هنا]",key='submit_add',use_container_width=True):

        if len(password) < 4:
            change_text_style_arabic_side("أدخل كلمة مرور صحيحة", 'text_red_side', red)

        else:
            customers = stripe.Customer.list()

            if len(customers.data) > 0:
                found = False
                pass_found = False
                for user in range(len(customers.data)):

                    customer = customers.data[user]
                    username = customer.email.strip().lower()

                    if username == email:

                        # Check password
                        username_azure,password_azure = read_subscription_from_azure_keyvault_arabic(username,password)
                        if password_azure == password:

                            # Check subscription
                            subscriptions = stripe.Subscription.list(customer=customer.id)
                            status = stripe.Subscription.list(customer=customer.id)['data']
                            if status:
                                status = status[0]['status']
                            else: status = 'Unknown'

                            if status in ['active']:
                                change_text_style_arabic_side("الاشتراك ساري المفعول", 'text_violet_side', violet)
                                customer_id = customer.id
                                subscription = stripe.Subscription.list(customer=customer_id)
                                days_left = get_days_left(subscription)

                                change_text_style_arabic_side("الأيام المتبقية لهذا الشهر:" + " " + str(days_left), 'text_violet_side', violet)
                                change_text_style_arabic_side("للبدء, انقر في الأعلى من هذه الصفحة على كلمة: GPTapp", 'subhead_side', violet)
                                found = True
                                pass_found = True
                                user = True
                                return user

                            elif status in ['canceled']:
                                customer_id = customer.id
                                subscription = stripe.Subscription.list(customer=customer_id)
                                days_left = get_days_left(subscription)

                                if days_left == 0 and status == 'canceled':
                                    change_text_style_arabic_side("انتهت فترة الاشتراك بعد الإلغاء!", 'text_red_side', red)
                                    found = True
                                    pass_found = True
                                    user = False
                                    return user

                                elif subscription['data'][0]['cancel_at_period_end']:
                                    change_text_style_arabic_side(":سيتم إلغاء الاشتراك في غضون" + " " + str(days_left),'text_violet_side', violet)
                                    change_text_style_arabic_side("للبدء, انقر في الأعلى من هذه الصفحة على كلمة: GPTapp", 'subhead_side', violet)

                                    found = True
                                    pass_found = True
                                    user = True
                                    return user

                                else:
                                    change_text_style_arabic_side("تم إلغاء الاشتراك", 'text_red_side',red)

                                    found = True
                                    pass_found = True
                                    user = False
                                    return user

                            elif status in ['trialing']:
                                change_text_style_arabic_side("الاشتراك في وضع التجربة!", 'text_red_side', red)
                                change_text_style_arabic_side("للبدء, انقر في الأعلى من هذه الصفحة على كلمة: GPTapp", 'subhead_side', violet)
                                found = True
                                pass_found = True
                                user = True
                                return user

                            else:
                                change_text_style_arabic_side("لا يوجد اشتراك", 'text_red_side', red)
                                found = True
                                pass_found = True
                                user = False
                                return user

                        else: change_text_style_arabic_side("أدخل كلمة مرور صحيحة", 'text_red_side', red)

                        found = True
                        pass_found = True
                        user = False
                        return user

                    elif email == os.environ['ADMIN_EMAIL'] and password == os.environ['ADMIN_PASSWORD']:
                        found = True
                        pass_found = True
                        user = True
                        return user

                if not found and not pass_found:
                    change_text_style_arabic_side("بيانات الاعتماد غير صحيحة", 'text_red_side', red)
                    found = False
                    pass_found = False
                    user = False
                    return user

            else:
                change_text_style_arabic_side("أنت غير مشترك في هذه الخدمة", 'text_red_side', red)
                found = False
                pass_found = False
                user = False
                return user

    return user


def subscribe_to_service_ara():

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
        pay_link = f'<a href="{session.url}" target="_blank">انقر هنا للمتابعة إلى عملية الدفع!</a>'
        st.sidebar.write(pay_link, unsafe_allow_html=True)

    st.sidebar.divider()
    change_text_style_arabic_side("هل ترغب في الاشتراك؟", 'subhead_side', violet)
    # Check if customer exists
    change_text_style_arabic_side("يرجى إدخال عنوان بريدك الإلكتروني", 'text_violet_side', violet)
    email = st.sidebar.text_input("email",key='email_check',label_visibility='collapsed')
    email = email.strip().lower()
    change_text_style_arabic_side("قم بإنشاء كلمة مرور واحفظها", 'text_violet_side', violet)
    password = st.sidebar.text_input("password_check", type='password',label_visibility='collapsed')
    password = password.strip()

    if len(email) == 0:
        change_text_style_arabic_side("أدخل بريدك الإلكتروني", 'text_violet_side', violet)

    else:
        if email_button := st.sidebar.button(":red[انقر هنا]", key='submit_email_check',use_container_width=True):
            customers = stripe.Customer.list()
            if len(customers.data) > 0:
                customer = customers.data[0]
                username = customer.email.strip().lower()

                if username == email:
                    change_text_style_arabic_side("المستخدم موجود. يرجى تسجيل الدخول!",'text_red_side', red)

            if len(password) < 4:
                change_text_style_arabic_side("أدخل كلمة مرور صحيحة", 'text_red_side', red)
                change_text_style_arabic_side("يجب أن تتكون كلمة المرور من 4 أحرف / أرقام على الأقل", 'text_red_side', red)

            else:
                # Write email & password to Azure blob
                email, password = write_subscription_ids_to_azure_keyvault_arabic(email, password)

                # Proceed to pay
                proceed_to_payment()

    return email,password


def cancel_service_ara():

    username = ''

    # Cancel subscription to the service
    st.sidebar.divider()
    change_text_style_arabic_side("هل ترغب في إلغاء الاشتراك؟", 'subhead_side', violet)
    # Check if customer exists
    change_text_style_arabic_side("يرجى إدخال عنوان بريدك الإلكتروني", 'text_violet_side', violet)
    email = st.sidebar.text_input("email",key='email_cancel',label_visibility='collapsed')
    email = email.strip().lower()
    change_text_style_arabic_side("أدخل كلمة المرور", 'text_violet_side', violet)
    password = st.sidebar.text_input("password_cancel", type='password',label_visibility='collapsed')
    password = password.strip()

    if len(email) == 0:
        change_text_style_arabic_side("أدخل بريدك الإلكتروني", 'text_violet_side', violet)

    else:
        if email_button_cancel := st.sidebar.button(":red[انقر هنا]",key='submit_cancel',use_container_width=True):

            if len(password) < 4:
                    change_text_style_arabic_side("أدخل كلمة مرور صحيحة", 'text_red_side', red)

            else:
                customers = stripe.Customer.list()

                if len(customers.data) > 0:

                    for user in range(len(customers.data)):

                        customer = customers.data[user]
                        username = customer.email.strip().lower()

                        if username == email:

                            # Check password
                            username_azure, password_azure = read_subscription_from_azure_keyvault_arabic(username,password)
                            if password_azure == password:

                                subscriptions = stripe.Subscription.list(customer=customer.id)

                                if len(subscriptions.data) > 0:

                                    status = stripe.Subscription.list(customer=customer.id)['data'][0]['status']

                                    if status == 'active':
                                        customer_id = customer.id
                                        subscription = stripe.Subscription.list(customer=customer_id)
                                        days_left = get_days_left(subscription)
                                        subscription_id = subscription['data'][0]['id']
                                        stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)

                                        if days_left == 0:
                                            stripe.Subscription.delete(subscription_id)

                                        change_text_style_arabic_side("تم إلغاء الاشتراك بنجاح لفترة الفوترة التالية!", 'text_violet_side',violet)
                                        change_text_style_arabic_side("الأيام المتبقية لهذا الشهر:" + " " + str(days_left), 'text_violet_side',violet)

                                    elif status == 'trialing':
                                        customer_id = customer.id
                                        subscription = stripe.Subscription.list(customer=customer_id)
                                        subscription_id = subscription['data'][0]['id']
                                        stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)
                                        stripe.Subscription.delete(subscription_id)

                                        change_text_style_arabic_side("تم إلغاء الاشتراك بنجاح!",'text_violet_side', violet)

                                else:
                                    change_text_style_arabic_side("لا يوجد اشتراك", 'text_red_side', red)

                            else:
                                change_text_style_arabic_side("أدخل كلمة مرور صحيحة", 'text_red_side', red)

                else:
                    change_text_style_arabic_side("لا يوجد اشتراك", 'text_red_side', red)

    st.sidebar.divider()
    return subscribed_user


def forgot_password_ara():

    def send_email(sender, recipient_email, body):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(os.environ["MY_EMAIL_ADDRESS"],os.environ["EMAIL_PASSWORD"])
            server.sendmail(sender, recipient_email, body)

    user = False

    # Check customers
    st.sidebar.write("")
    change_text_style_arabic_side("هل نسيت كلمة المرور؟", 'subhead_side', violet)
    change_text_style_arabic_side("يرجى إدخال عنوان بريدك الإلكتروني", 'text_violet_side', violet)
    email = st.sidebar.text_input("email",key='email_find',label_visibility='collapsed')
    email = email.strip().lower()

    if email_button := st.sidebar.button(":red[انقر هنا]",key='submit_find_email',use_container_width=True):

        customers = stripe.Customer.list()

        if len(customers.data) > 0:
            for user in range(len(customers.data)):

                customer = customers.data[user]
                username = customer.email.strip().lower()

                if username == email:

                    # retrieve password
                    username_azure,password_azure = retrieve_password_from_azure_keyvault_arabic(username)

                    change_text_style_arabic_side("تم إرسال كلمة المرور إلى عنوان بريدك الإلكتروني", 'text_red_side', red)

                    subject = 'طلبت منا كلمة المرور'
                    body = f"GPT Document Analyzer :كما طلبت، يرجى العثور أدناه على كلمة المرور الخاصة بك للموقع: \n\n {password_azure} \n\n كل التوفيق \n GPT Document Analyzer الفريق"
                    send_email(os.environ["MY_EMAIL_ADDRESS"], email, f"Subject: {subject} \n\n{body}")
                    user = True

                    return password_azure

                else: user = False

            if not user:
                change_text_style_arabic_side("البريد الإلكتروني غير موجود في قاعدة بياناتنا", 'text_red_side', red)
                return user

        else:
            change_text_style_arabic_side("البريد الإلكتروني غير موجود في قاعدة بياناتنا", 'text_red_side', red)
            return user

    st.sidebar.divider()
    return user