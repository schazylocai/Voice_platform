import streamlit as st
import smtplib
import re
import os
from src.Change_Text_Style import change_text_style_arabic
from email.mime.text import MIMEText

video_url_ara = "https://youtu.be/35GxvfPku0Y"


def write_Arabic_About():

    violet = "rgb(169, 131, 247)"
    red = "rgb(232,89,83)"
    white = "rgb(255,255,255)"

    # section 2
    col1, col2, col3 = st.columns(3)

    with col3:
        change_text_style_arabic("استفد من قوة الذكاء الاصطناعي لتحليل وثائقك.", 'text_red', red)
        st.markdown("")
        change_text_style_arabic("أهلآً بك في محلل المستندات. التطبيق الثوري الذي يستغل قدرات النماذج اللغوية الكبيرة.",
                          'head', violet)

    with col2:
        change_text_style_arabic("ما الذي يمكن لهذا النموذج أن يفعله لك؟", 'text_red', red)
        st.markdown("")
        change_text_style_arabic(
            "مع هذه الأداة المتقدمة، يمكنك بسهولة تحميل عدة مستندات PDF، Word، أو نص والتفاعل معها كما لم تفعل من قبل",
            'subhead', violet)
        st.markdown("")
        change_text_style_arabic(
            "توجه بأسئلة، استخرج معلومات قيمة، قم بتحليل المحتوى، وانتج ملخصات موجزة مباشرة من المستندات التي تم تحميلها!",
            'text_violet', violet)
        st.markdown("")
        change_text_style_arabic("شاهد الفيديو لترى كيف يعمل هذا النموذج ⬅︎", 'text_violet', violet)
    with col1:
        st.video(video_url_ara)

    # section 3
    st.divider()
    change_text_style_arabic("تفاصيل الاشتراك", 'head', violet)
    change_text_style_arabic("الاستخدام الكامل: 15 دولار أمريكي في الشهر + فترة تجربة مجانية لمدة يوم واحد", 'subhead', violet)
    change_text_style_arabic("اشترك للوصول إلى الإمكانات الكاملة لنموذج الذكاء الاصطناعي لدينا.", 'text_violet', violet)

    def Terms_ara():
        # section 4
        change_text_style_arabic("الأسئلة والأجوبة / نصائح",'text_violet',violet)
        st.caption("")
        with st.expander(""):
            change_text_style_arabic("ما هو محلل الوثائق هذا؟",'text_violet',violet)
            change_text_style_arabic("محلل الوثائق هو أداة تستخدم نماذج لغوية كبيرة لتحليل وتلخيص الوثائق. يمكن استخدامها لاستخلاص الأفكار الرئيسية من الوثائق، وتحديد المواضيع المهمة، وإنشاء ملخصات دقيقة وموجزة",'text_white',white)

            change_text_style_arabic("كيف يعمل محلل الوثائق؟",'text_violet',violet)
            change_text_style_arabic("محلل المستندات يستخدم نموذج لغوي ضخم لمعالجة نص المستند. يتم تدريب النموذج اللغوي على مجموعة بيانات ضخمة تتضمن نصوصًا وشفرات، ويمكن للنموذج أن يتعلم التعرف على الأنماط والعلاقات في اللغة. يتيح هذا للنموذج اللغوي استخلاص الأفكار الرئيسية من المستندات، وتحديد المواضيع المهمة، وإنشاء ملخصات دقيقة وموجزة في نفس الوقت",'text_white',white)

            change_text_style_arabic("ما هي فوائد استخدام محلل الوثائق؟",'text_violet',violet)
            change_text_style_arabic("هناك العديد من الفوائد في استخدام محلل المستندات، بما في ذلك",'text_white',white)
            change_text_style_arabic("زيادة الإنتاجية: يمكن لمحلل المستندات مساعدتك في توفير الوقت من خلال أتمتة عملية تحليل وتلخيص المستندات",'text_white',white)
            change_text_style_arabic("تحسين الدقة: يمكن لمحلل المستندات مساعدتك في إنتاج ملخصات أكثر دقة من خلال تحديد المعلومات الأكثر أهمية في المستند",'text_white',white)
            change_text_style_arabic("رؤى أفضل: يمكن لمحلل المستندات مساعدتك في الحصول على رؤى جديدة في المستندات من خلال تحديد الأنماط والعلاقات في النص",'text_white',white)

            change_text_style_arabic("كيف يمكنني استخدام محلل المستندات؟",'text_violet',violet)
            change_text_style_arabic("محلل المستندات سهل الاستخدام. قم ببساطة بتحميل المستند إلى الموقع الإلكتروني، ثم اطرح سؤالاً متعلقاً بالمستند المحمل، وسيقوم محلل المستندات بتحليل المستند",'text_white',white)

            change_text_style_arabic("ما هي قيود محلل المستندات؟",'text_violet',violet)
            change_text_style_arabic("محلل المستندات هو أداة قوية، ولكن لديه بعض القيود. فهو غير قادر على التعامل مع جميع أنواع المستندات. فيما يلي بعض القيود المحددة للأخذ في الاعتبار",'text_white',white)
            change_text_style_arabic("بشكل عام، يجب أن يحتوي المستندات المحملة على صور لا تزيد نسبتها عن 40٪ من المحتوى الإجمالي",'text_white',white)
            change_text_style_arabic("إذا توقف المستند عن التحميل وتعلق، فيجب حذفه والمحاولة مرة أخرى",'text_white',white)
            change_text_style_arabic("هذا النموذج مناسب لأوراق البحث والمستندات المستندة إلى النص، وليس الكتب الموضوعية والقصص",'text_white',white)

            change_text_style_arabic("وإليك بعض النصائح لاستخدام محلل المستندات",'text_violet',violet)
            change_text_style_arabic("اختر مستندات مكتوبة بشكل جيد وسهلة الفهم",'text_white',white)
            change_text_style_arabic("تجنب المستندات التي تكون طويلة جدًا أو معقدة للغاية",'text_white',white)
            change_text_style_arabic("إذا لم تكن متأكدًا مما إذا كان المستند مناسبًا لمحلل المستندات، جرب تحميل جزء صغير منه أولاً",'text_white',white)

        change_text_style_arabic("سياسة الخصوصية", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            change_text_style_arabic("نحن ملتزمون بحماية خصوصيتك وضمان أمان معلوماتك الشخصية. تحدد هذه سياسة الخصوصية كيفية جمعنا واستخدامنا وحماية البيانات التي تقدمها لنا عند استخدام خوارزمية تعلم الآلة لمعالجة المستندات. يرجى قراءة هذه السياسة بعناية لفهم ممارساتنا فيما يتعلق ببياناتك الشخصية",'text_white',white)
            change_text_style_arabic("جمع المعلومات الشخصية",'text_violet',violet)
            change_text_style_arabic("عند استخدامك لموقعنا وتحميل المستندات الخاصة بك، قد نقوم بجمع بعض المعلومات الشخصية، مثل اسمك وعنوان بريدك الإلكتروني، لتوفير الخدمات المطلوبة لك. لا نقوم بتخزين مستنداتك أو أي بيانات معالجة بشكل دائم. يتم الاحتفاظ بالمستندات في الذاكرة فقط أثناء جلستك ويتم حذفها فوراً بعدها",'text_white',white)
            change_text_style_arabic("استخدام المعلومات الشخصية",'text_violet',violet)
            change_text_style_arabic("نستخدم المعلومات الشخصية التي يتم جمعها لتشغيل وتحسين خوارزمية التعلم الآلي الخاصة بنا، وتوفير دعم العملاء، والتواصل معك بشأن حسابك والاشتراكات الخاصة بك. ليس لدينا وصول إلى مستنداتك المحملة أو عرضها. خصوصيتك وسرية بياناتك أمران مهمان للغاية بالنسبة لنا",'text_white',white)
            change_text_style_arabic("تدابير الأمان",'text_violet',violet)
            change_text_style_arabic( "نتخذ تدابير الأمان المناسبة لحماية معلوماتك الشخصية من الوصول غير المصرح به أو التغيير أو الكشف. يتم تأمين موقعنا بتشفير SSL لضمان سرية بياناتك أثناء النقل",'text_white',white)

        change_text_style_arabic("شروط الخدمة", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            change_text_style_arabic("تحدد هذه الشروط الاتفاقية بيننا ومستخدمي خوارزمية التعلم الآلي لمعالجة المستندات. عن طريق الوصول إلى موقعنا واستخدام خدماتنا، فإنك توافق على الالتزام بهذه الشروط",'text_white',white)
            change_text_style_arabic("استخدام الخدمة",'text_violet',violet)
            change_text_style_arabic("تتيح خوارزمية التعلم الآلي لمستخدميها تحميل ومعالجة المستندات الخاصة بهم لأغراض الاستعلام أو التلخيص. قد يتفاوت أداء الخوارزمية بناءً على جودة وتعقيد المستندات المدخلة",'text_white',white)
            change_text_style_arabic("الدفع والاشتراكات",'text_violet',violet)
            change_text_style_arabic("للوصول إلى خدماتنا على أساس شهري، يتعين على المستخدمين الاشتراك وإجراء الدفعات اللازمة من خلال موقع دفع آمن. الدفعات غير قابلة للاسترداد ما لم ينص صراحة على خلاف ذلك",'text_white',white)
            change_text_style_arabic("الملكية الفكرية",'text_violet',violet)
            change_text_style_arabic("جميع حقوق الملكية الفكرية المرتبطة بخوارزمية التعلم الآلي لدينا، بما في ذلك أي برامج أو شفرات أو وثائق، تعود لنا. يحظر على المستخدمين نسخ أو تعديل أو توزيع أو إجراء تفكيك عكسي للخوارزمية",'text_white',white)
            change_text_style_arabic("تحديد المسؤولية",'text_violet',violet)
            change_text_style_arabic("نحن غير مسؤولين عن أي أضرار مباشرة أو غير مباشرة ناتجة عن استخدام أو عدم القدرة على استخدام خدماتنا، بما في ذلك ولكن لا تقتصر على فقدان البيانات أو الإيرادات أو الأرباح. تتم تقديم خدماتنا",'text_white',white)

    st.write("")
    st.write("")
    Terms_ara()

    def contact_us_form_ara():

        change_text_style_arabic("اتصل بنا", 'text_violet', violet)
        st.caption("")
        with st.expander(""):
            sender_name = st.text_input(':violet[الاسم]', key='name_ara')
            sender_email = st.text_input(':violet[البريد الإلكتروني]', key='email_ara')
            sender_message = st.text_area(':violet[الرسالة]', key='message_ara')
            submitted = st.button(':red[انقر هنا]',key='submitarabicform')

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
                    send_email_ara(
                        sender_name=str(sender_name.encode('UTF-8')),
                        recipient=os.environ["MY_EMAIL_ADDRESS"],
                        subject="Contact Form Submission",
                        body=sender_message.encode('UTF-8'),
                        sender_email=sender_email)
                    st.success(':violet[!تم إرسال الاستعلام بنجاح. سنعود إليك في أقرب وقت ممكن]')

    contact_us_form_ara()

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.divider()
    st.markdown(":violet[© 2023 FAB DWC LLC. جميع الحقوق محفوظة]")


def send_email_ara(sender_name, recipient, subject, body, sender_email):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(recipient, os.environ["EMAIL_PASSWORD"])
        server.sendmail(sender_name, recipient, f"Subject: {subject}\n\n{sender_name}: {sender_email}\n\n{body}")