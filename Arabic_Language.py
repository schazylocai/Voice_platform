import streamlit as st
import smtplib
import re
import os
import codecs
video_url = "https://youtu.be/PgXjVwHmqbg"


def write_Arabic_About():
    violet = "rgb(169, 131, 247)"
    red = "rgb(232,89,83)"

    def change_text_style(text_body, font_type, color):

        font_link = '<link href="https://fonts.googleapis.com/css2?family=Cairo+Play:wght@600&display=swap" rel="stylesheet">'
        font_family = "'Cairo Play', sans-serif"
        if font_type == 'title':
            st.markdown(
                f"""
                            {font_link}
                            <style>
                                .title-text {{
                                    font-family: {font_family};
                                    font-size: 42px;
                                    color: {color};
                                    text-align: right;
                                    line-height: 1.5;
                                }}
                            </style>
                            <div class="title-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

        elif font_type == 'head':
            st.markdown(
                f"""
                            {font_link}
                            <style>
                                .heading-text {{
                                    font-family: {font_family};
                                    font-size: 38px;
                                    color: {color};
                                    text-align: right;
                                    line-height: 1.6;
                                }}
                            </style>
                            <div class="heading-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

        elif font_type == 'subhead':
            st.markdown(
                f"""
                            {font_link}
                            <style>
                                .sub-text {{
                                    font-family: {font_family};
                                    font-size: 24px;
                                    color: {color};
                                    text-align: right;
                                    line-height: 2;
                                }}
                            </style>
                            <div class="sub-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

        elif font_type == 'text_violet':
            st.markdown(
                f"""
                            {font_link}
                            <style>
                                .normal-text {{
                                    font-family: {font_family};
                                    font-size: 16px;
                                    color: {color};
                                    text-align: right;
                                    line-height: 2.2;
                                }}
                            </style>
                            <div class="normal-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

        elif font_type == 'text_red':
            st.markdown(
                f"""
                            {font_link}
                            <style>
                                .bold-text {{
                                    font-family: {font_family};
                                    font-size: 12px;
                                    color: {color};
                                    text-align: right;
                                    line-height: 2.2;
                                }}
                            </style>
                            <div class="bold-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

    #     change_text_style("تحليل المستندات بمساعدة جي بي تي", 'title', violet)

    # section 2
    col1, col2, col3 = st.columns(3)

    with col3:
        change_text_style("استفد من قوة الذكاء الاصطناعي لتحليل وثائقك.", 'text_red', red)
        st.markdown("")
        change_text_style("مرحبًا بك في محلل المستندات، التطبيق الثوري الذي يستغل قدرات النماذج اللغوية الكبيرة.",
                          'head', violet)

    with col2:
        change_text_style("ما الذي يمكن لهذا النموذج أن يفعله لك؟", 'text_red', red)
        st.markdown("")
        change_text_style(
            "مع هذه الأداة المتقدمة، يمكنك بسهولة تحميل عدة مستندات PDF، Word، أو نص والتفاعل معها كما لم تفعل من قبل.",
            'subhead', violet)
        st.markdown("")
        change_text_style(
            "توجه بأسئلة، استخرج معلومات قيمة، قم بتحليل المحتوى، وانتج ملخصات موجزة مباشرة من المستندات التي تم تحميلها.!",
            'text_violet', violet)
        st.markdown("")
        change_text_style("شاهد الفيديو لترى كيف يعمل هذا النموذج ⬅︎", 'text_violet', violet)
    with col1:
        st.video(video_url)

    # section 3
    st.divider()
    change_text_style("تفاصيل الاشتراك", 'head', violet)
    change_text_style("الاستخدام الكامل: 15 دولار أمريكي في الشهر + فترة تجربة مجانية لمدة يوم واحد", 'subhead', violet)
    change_text_style("اشترك للوصول إلى الإمكانات الكاملة لنموذج الذكاء الاصطناعي لدينا.", 'text_violet', violet)

    def Terms():
        # section 4
        change_text_style("الأسئلة والأجوبة / نصائح",'text_violet',violet)
        st.caption("")
        with st.expander(""):
            change_text_style("ما هو محلل الوثائق هذا؟",'text_violet',violet)
            change_text_style("محلل الوثائق هو أداة تستخدم نماذج لغوية كبيرة لتحليل وتلخيص الوثائق. يمكن استخدامها لاستخلاص الأفكار الرئيسية من الوثائق، وتحديد المواضيع المهمة، وإنشاء ملخصات دقيقة وموجزة",'text_red',violet)
            change_text_style("كيف يعمل محلل الوثائق؟",'text_violet',violet)
            change_text_style("محلل المستندات يستخدم نموذج لغوي ضخم لمعالجة نص المستند. يتم تدريب النموذج اللغوي على مجموعة بيانات ضخمة تتضمن نصوصًا وشفرات، ويمكن للنموذج أن يتعلم التعرف على الأنماط والعلاقات في اللغة. يتيح هذا للنموذج اللغوي استخلاص الأفكار الرئيسية من المستندات، وتحديد المواضيع المهمة، وإنشاء ملخصات دقيقة وموجزة في نفس الوقت",'text_red',violet)
            change_text_style("ما هي فوائد استخدام محلل الوثائق؟",'text_violet',violet)
            change_text_style(":هناك العديد من الفوائد في استخدام محلل المستندات، بما في ذلك",'text_red',violet)
            change_text_style("زيادة الإنتاجية: يمكن لمحلل المستندات مساعدتك في توفير الوقت من خلال أتمتة عملية تحليل وتلخيص المستندات",'text_red',violet)
            change_text_style("تحسين الدقة: يمكن لمحلل المستندات مساعدتك في إنتاج ملخصات أكثر دقة من خلال تحديد المعلومات الأكثر أهمية في المستند",'text_red',violet)
            change_text_style("رؤى أفضل: يمكن لمحلل المستندات مساعدتك في الحصول على رؤى جديدة في المستندات من خلال تحديد الأنماط والعلاقات في النص",'text_red',violet)
            change_text_style("كيف يمكنني استخدام محلل المستندات؟",'text_violet',violet)
            change_text_style("محلل المستندات سهل الاستخدام. قم ببساطة بتحميل المستند إلى الموقع الإلكتروني، ثم اطرح سؤالاً متعلقاً بالمستند المحمل، وسيقوم محلل المستندات بتحليل المستند",'text_red',violet)
            change_text_style("ما هي قيود محلل المستندات؟",'text_violet',violet)
            change_text_style(":محلل المستندات هو أداة قوية، ولكن لديه بعض القيود. فهو غير قادر على التعامل مع جميع أنواع المستندات. فيما يلي بعض القيود المحددة للأخذ في الاعتبار",'text_red',violet)
            change_text_style("بشكل عام، يجب أن يحتوي المستندات المحملة على صور لا تزيد نسبتها عن 40٪ من المحتوى الإجمالي",'text_red',violet)
            change_text_style("إذا توقف المستند عن التحميل وتعلق، فيجب حذفه والمحاولة مرة أخرى",'text_red',violet)
            change_text_style("هذا النموذج مناسب لأوراق البحث والمستندات المستندة إلى النص، وليس الكتب الموضوعية والقصص",'text_red',violet)
            change_text_style(":وإليك بعض النصائح لاستخدام محلل المستندات",'text_violet',violet)
            change_text_style("اختر مستندات مكتوبة بشكل جيد وسهلة الفهم",'text_red',violet)
            change_text_style("تجنب المستندات التي تكون طويلة جدًا أو معقدة للغاية",'text_red',violet)
            change_text_style("إذا لم تكن متأكدًا مما إذا كان المستند مناسبًا لمحلل المستندات، جرب تحميل جزء صغير منه أولاً",'text_red',violet)

        change_text_style("سياسة الخصوصية", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            change_text_style("نحن ملتزمون بحماية خصوصيتك وضمان أمان معلوماتك الشخصية. تحدد هذه سياسة الخصوصية كيفية جمعنا واستخدامنا وحماية البيانات التي تقدمها لنا عند استخدام خوارزمية تعلم الآلة لمعالجة المستندات. يرجى قراءة هذه السياسة بعناية لفهم ممارساتنا فيما يتعلق ببياناتك الشخصية",'text_red',violet)
            change_text_style(":جمع المعلومات الشخصية",'text_violet',violet)
            change_text_style("عند استخدامك لموقعنا وتحميل المستندات الخاصة بك، قد نقوم بجمع بعض المعلومات الشخصية، مثل اسمك وعنوان بريدك الإلكتروني، لتوفير الخدمات المطلوبة لك. لا نقوم بتخزين مستنداتك أو أي بيانات معالجة بشكل دائم. يتم الاحتفاظ بالمستندات في الذاكرة فقط أثناء جلستك ويتم حذفها فوراً بعدها",'text_red',violet)
            change_text_style(":استخدام المعلومات الشخصية",'text_violet',violet)
            change_text_style("نستخدم المعلومات الشخصية التي يتم جمعها لتشغيل وتحسين خوارزمية التعلم الآلي الخاصة بنا، وتوفير دعم العملاء، والتواصل معك بشأن حسابك والاشتراكات الخاصة بك. ليس لدينا وصول إلى مستنداتك المحملة أو عرضها. خصوصيتك وسرية بياناتك أمران مهمان للغاية بالنسبة لنا",'text_red',violet)
            change_text_style(":تدابير الأمان",'text_violet',violet)
            change_text_style( "نتخذ تدابير الأمان المناسبة لحماية معلوماتك الشخصية من الوصول غير المصرح به أو التغيير أو الكشف. يتم تأمين موقعنا بتشفير SSL لضمان سرية بياناتك أثناء النقل",'text_red',violet)

        change_text_style("شروط الخدمة", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            change_text_style("تحدد هذه الشروط الاتفاقية بيننا ومستخدمي خوارزمية التعلم الآلي لمعالجة المستندات. عن طريق الوصول إلى موقعنا واستخدام خدماتنا، فإنك توافق على الالتزام بهذه الشروط",'text_red',violet)
            change_text_style(":استخدام الخدمة",'text_violet',violet)
            change_text_style("تتيح خوارزمية التعلم الآلي لمستخدميها تحميل ومعالجة المستندات الخاصة بهم لأغراض الاستعلام أو التلخيص. قد يتفاوت أداء الخوارزمية بناءً على جودة وتعقيد المستندات المدخلة",'text_red',violet)
            change_text_style(":الدفع والاشتراكات",'text_violet',violet)
            change_text_style("للوصول إلى خدماتنا على أساس شهري، يتعين على المستخدمين الاشتراك وإجراء الدفعات اللازمة من خلال موقع دفع آمن. الدفعات غير قابلة للاسترداد ما لم ينص صراحة على خلاف ذلك",'text_red',violet)
            change_text_style(":الملكية الفكرية",'text_violet',violet)
            change_text_style("جميع حقوق الملكية الفكرية المرتبطة بخوارزمية التعلم الآلي لدينا، بما في ذلك أي برامج أو شفرات أو وثائق، تعود لنا. يحظر على المستخدمين نسخ أو تعديل أو توزيع أو إجراء تفكيك عكسي للخوارزمية",'text_red',violet)
            change_text_style(":تحديد المسؤولية",'text_violet',violet)
            change_text_style("نحن غير مسؤولين عن أي أضرار مباشرة أو غير مباشرة ناتجة عن استخدام أو عدم القدرة على استخدام خدماتنا، بما في ذلك ولكن لا تقتصر على فقدان البيانات أو الإيرادات أو الأرباح. تتم تقديم خدماتنا",'text_red',violet)

    st.write("")
    st.write("")
    Terms()

    def send_email(sender, recipient, subject, body):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(sender, os.environ["EMAIL_PASSWORD"])
            server.sendmail(sender, recipient, f"Subject: {subject}\n\n{body}")

    def contact_us_form():

        change_text_style("!اتصل بنا", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            sender_name = st.text_input(':violet[الاسم]', key='name')
            sender_email = st.text_input(':violet[البريد الإلكتروني]', key='email')
            sender_message = st.text_area(':violet[الرسالة]', key='message')
            submitted = st.button(':red[انقر هنا]')

            def is_valid_email(sender_email):
                # Use a regular expression pattern to validate the email address format
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                return re.match(pattern, sender_email) is not None

            if submitted:
                if sender_name.strip() == '':
                    st.error(':red[!أدخل أسمك]')
                elif sender_email.strip() == '':
                    st.error(':red[!أدخل بريدك الإلكتروني]')
                elif not is_valid_email(sender_email.strip()):
                    st.error(':red[!أدخل عنوان بريد إلكتروني صالح]')
                elif sender_message.strip() == '':
                    st.error(':red[!أدخل رسالة]')
                else:
                    send_email(
                        sender=os.environ["MY_EMAIL_ADDRESS"],
                        recipient=os.environ["MY_EMAIL_ADDRESS"],
                        subject="Contact Form Submission",
                        body=sender_message.encode('UTF-8'))
                    st.success(':violet[!تم إرسال الاستعلام بنجاح. سنعود إليك في أقرب وقت ممكن]')

    contact_us_form()

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.divider()
    st.markdown(":violet[© 2023 FAB DWC LLC. جميع الحقوق محفوظة]")