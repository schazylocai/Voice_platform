import streamlit as st


def change_text_style_arabic(text_body, font_type, color):
    font_link = '<link href="https://fonts.googleapis.com/css2?family=Cairo+Play:wght@600;800&display=swap" rel="stylesheet">'
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
                                font-weight: 600;
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
                                font-weight: 600;
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
                                font-weight: 600;
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
                                font-size: 17px;
                                color: {color};
                                text-align: right;
                                line-height: 2.2;
                                font-weight: 600;
                            }}
                        </style>
                        <div class="normal-text"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)

    elif font_type == 'text_white':
        st.markdown(
            f"""
                        {font_link}
                        <style>
                            .light-text {{
                                font-family: {font_family};
                                font-size: 14px;
                                color: {color};
                                text-align: right;
                                line-height: 2.2;
                                font-weight: 600;
                            }}
                        </style>
                        <div class="light-text"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)

    elif font_type == 'text_red':
        st.markdown(
            f"""
                        {font_link}
                        <style>
                            .bold-text {{
                                font-family: {font_family};
                                font-size: 14px;
                                color: {color};
                                text-align: right;
                                line-height: 2.2;
                                font-weight: 800;
                            }}
                        </style>
                        <div class="bold-text"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)


def change_text_style_arabic_side(text_body, font_type, color):
    font_link = '<link href="https://fonts.googleapis.com/css2?family=Cairo+Play:wght@600;800&display=swap" rel="stylesheet">'
    font_family = "'Cairo Play', sans-serif"

    if font_type == 'subhead_side':
        st.sidebar.markdown(
            f"""
                        {font_link}
                        <style>
                            .sub-text_side {{
                                font-family: {font_family};
                                font-size: 22px;
                                color: {color};
                                text-align: right;
                                line-height: 2;
                                font-weight: 800;
                            }}
                        </style>
                        <div class="sub-text_side"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)

    elif font_type == 'text_violet_side':
        st.sidebar.markdown(
            f"""
                        {font_link}
                        <style>
                            .normal-text_side {{
                                font-family: {font_family};
                                font-size: 14px;
                                color: {color};
                                text-align: right;
                                line-height: 3;
                                font-weight: 600;
                            }}
                        </style>
                        <div class="normal-text_side"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)

    elif font_type == 'text_red_side':
        st.sidebar.markdown(
            f"""
                        {font_link}
                        <style>
                            .bold-text_side {{
                                font-family: {font_family};
                                font-size: 14px;
                                color: {color};
                                text-align: right;
                                line-height: 2.2;
                                font-weight: 800;
                            }}
                        </style>
                        <div class="bold-text_side"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)


def change_text_style_english(text_body, font_type, color):
    font_link_eng = '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">'
    font_family_eng = "'Roboto', sans-serif"

    if font_type == 'title':
        st.markdown(
            f"""
                        {font_link_eng}
                        <style>
                            .title-text {{
                                font-family: {font_family_eng};
                                font-size: 60px;
                                color: {color};
                                text-align: left;
                                line-height: 1;
                                font-weight: 700;
                            }}
                        </style>
                        <div class="title-text"><bdi>{text_body}</bdi></div>
                        """, unsafe_allow_html=True)

    elif font_type == 'head':
        st.markdown(
            f"""
                            {font_link_eng}
                            <style>
                                .heading-text {{
                                    font-family: {font_family_eng};
                                    font-size: 38px;
                                    color: {color};
                                    text-align: left;
                                    line-height: 1.6;
                                    font-weight: 400;
                                }}
                            </style>
                            <div class="heading-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

    elif font_type == 'subhead':
        st.markdown(
            f"""
                            {font_link_eng}
                            <style>
                                .sub-text {{
                                    font-family: {font_family_eng};
                                    font-size: 24px;
                                    color: {color};
                                    text-align: left;
                                    line-height: 2;
                                    font-weight: 400;
                                }}
                            </style>
                            <div class="sub-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

    elif font_type == 'text_violet':
        st.markdown(
            f"""
                            {font_link_eng}
                            <style>
                                .normal-text {{
                                    font-family: {font_family_eng};
                                    font-size: 16px;
                                    color: {color};
                                    text-align: left;
                                    line-height: 2.2;
                                    font-weight: 400;
                                }}
                            </style>
                            <div class="normal-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)

    elif font_type == 'text_red':
        st.markdown(
            f"""
                            {font_link_eng}
                            <style>
                                .bold-text {{
                                    font-family: {font_family_eng};
                                    font-size: 12px;
                                    color: {color};
                                    text-align: left;
                                    line-height: 2.2;
                                    font-weight: 400;
                                }}
                            </style>
                            <div class="bold-text"><bdi>{text_body}</bdi></div>
                            """, unsafe_allow_html=True)