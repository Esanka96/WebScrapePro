import os
import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
import pandas as pd
from googletrans import Translator
import TOC_HTML

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def translate_text(text, source_language='zh-CN', target_language='en'):
    translator = Translator()
    translation = translator.translate(text, src=source_language, dest=target_language)
    return translation.text

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
Total_count=None
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails\" : " + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                         len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
    # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
    #                                 len(completed_list), url_id, Ref_value, attachment, current_out)

try:
    with open('completed.txt', 'r', encoding='utf-8') as read_file:
        read_content = read_file.read().split('\n')
except FileNotFoundError:
    with open('completed.txt', 'w', encoding='utf-8'):
        with open('completed.txt', 'r', encoding='utf-8') as read_file:
            read_content = read_file.read().split('\n')

url_index, url_check = 0, 0
while url_index < len(url_list):
    try:
        url, url_id = url_list[url_index].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check==0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        TOC_name = "{}_TOC.html".format(url_id)

        Ref_value = "34"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        current_soup=get_soup(url)
        English_link="http://zglcyj.ijournals.cn/zglcyjen/ch/"+current_soup.find("div",class_="fmB").find("a")["href"]
        Chines_link=str(English_link).replace("zglcyjen/ch","zglcyj/ch")

        languageList=[English_link,Chines_link]

        news=current_soup.find('div',class_='le')
        Year,Volume_Issue=current_soup.find('div',class_='le').text.strip().split(',')
        Volume=re.sub(r'[^0-9]+','',Volume_Issue.strip().split(' ')[0])
        Issue = re.sub(r'[^0-9]+', '', Volume_Issue.strip().split(' ')[1])

        All_articles=current_soup.find('div',class_='zyy').findAll('dl',class_='dl')

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link,Article_title=None,None
            try:
                Article_link='http://zglcyj.ijournals.cn/zglcyjen/ch/' + All_articles[article_index].find('a').get('href')
                Article_title = All_articles[article_index].find('a').text.strip()

                # if not all(ord(char) < 128 for char in Article_title[:10]):
                #     Article_title= translate_text(Article_title)
                # else:
                #     Article_title=Article_title

                try:
                    Page_range = re.search(r':(.*?)(\[Abstract\])', All_articles[article_index].findAll('dd')[2].text.strip()).group(1).strip()
                except:
                    print("Failed to find page range")
                    Page_range = ""

                Article_soup = get_soup(
                    'http://zglcyj.ijournals.cn/zglcyjen/ch/' + All_articles[article_index].find('a').get('href'))

                try:
                    DOI = Article_soup.find('span', {'id': 'DOI'}).find('a').text.strip()
                except:
                    print("Failed to find doi")
                    DOI = ""

                pdf_link = 'http://zglcyj.ijournals.cn/zglcyjen/ch/reader/' + Article_soup.find('a',
                                                                                                class_='xzqw fr').get(
                    'href')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    pdf_content = requests.get(pdf_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": "", "Day": "",
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 25:
                    article_check += 1
                else:
                    message=f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :",Article_title)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        check = 0
        while check < 5:
            try:
                print("Wait until the TOC_PDF is downloaded")
                TOC_HTML.get_toc_html(current_out,TOC_name,languageList)
                check = 5
                print("TOC_PDF file downloaded successfully.")
            except:
                if not check < 4:
                    message = "Failed to get toc pdf"
                    error_list.append(message)
                check += 1

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),
                            str(len(error_list)))
        except Exception as error:
            message=f"Failed to send post request : {str(error)}"
            error_list.append(message)

        try:
            if str(Email_Sent).lower()=="true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)
                # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                #                                 len(completed_list), url_id, Ref_value, attachment, current_out)
        except Exception as error:
            message=f"Failed to send email : {str(error)}"
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass

        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 12:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print(Error_message)
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
            #                                 len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0



