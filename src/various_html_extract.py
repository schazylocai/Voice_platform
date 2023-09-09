# from html_text import extract_text
# from requests_html import HTMLSession
# from bs4 import BeautifulSoup
# if str(url).endswith('.pdf'):
#     cleaned_text = []
#     final_text = []
#     on_fly_mem_obj = io.BytesIO(response.content)
#     url_text = PyPDF2.PdfReader(on_fly_mem_obj)
#     for page in url_text.pages:
#         cleaned_text.append(page.extract_text().split('\n'))
#     final_text.append(f'Website page document: {url} ======> {cleaned_text}')
#
#     return final_text
#
# elif response.encoding in {'utf-8', 'UTF-8'}:
#     # Extract the main text content using html-text
#     temp_text = []
#     final_text = []
#     main_text = response.content
#     soup = BeautifulSoup(main_text, 'html.parser', from_encoding='utf-8')
#
#     links = soup.find_all('body')
#     counter = 0
#     for lin in links:
#         while counter < 1:
#             extracted_text = lin.get_text(strip=True)
#             temp_text.append(extracted_text)
#             counter += 1
#     cleaned_text = f'{counter} divider. Website page document: {url} ======> {temp_text}'
#     final_text.append(cleaned_text)

# links = soup.find_all('div')
# counter = 0
# for lin in links:
#     while counter < 1:
#         extracted_text = lin.get_text(strip=True)
#         temp_text.append(extracted_text)
#         counter += 1
# cleaned_text = f'{counter} divider. Website page document: {url} ======> {temp_text}'
# final_text.append(cleaned_text)
#
# return final_text
#
# else:
#     st.write(f'Unknown type: {response.encoding}')
