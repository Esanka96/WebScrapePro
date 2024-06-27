import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
import seperate_parameters
from datetime import datetime
import pandas as pd
from PyPDF2 import PdfReader

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def get_current_issue(list):
    count=0
    publication_statuses = ['Preprint','Advance publication','Issue in print','Issue in progress','A head of print','Early Access',
        'Internet prepublication','Prepublication','Online First issue','Early view','Advance Publishing','Advance Access','Ahead of Print',
        'Early Release Articles',"12th East-West Philosopher's Conference \"Trauma and Healing\" to appear in Philosophy East and West 73-3"]

    for i,sin_item in enumerate(list):
        if not sin_item.text.strip() in publication_statuses:
            count=i
            break
    return count

def read_text_file(file_name):
    with open(file_name,'r',encoding='utf-8') as file:
        file_content=file.read().split(',')
        url=file_content[0].strip()
        url_id=file_content[1].strip()
        return url,url_id

def read_pdf(pdf_path):
    try:
        file_path = pdf_path
        reader = PdfReader(file_path)
        first_page_text = reader.pages[1].extract_text().split('\n')
        relevant_line=first_page_text[-3]+first_page_text[-2]
        if 'doi.org/' in relevant_line:
            DOI=relevant_line.rsplit('doi.org/',1)[-1].rstrip(' .')
        else:
            DOI=""
    except:
        DOI=""
    return DOI

def get_session():
    logi_url='https://muse.jhu.edu/account/'
    new_session=requests.session()
    session_login=new_session.get(logi_url)
    login_post ='https://muse.jhu.edu/account/login'

    payload={'account_user_name': 'scopus1',
    'account_password': '1779290'}

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,da;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'muse.jhu.edu',
        'Origin': 'https://muse.jhu.edu',
        'Referer': 'https://muse.jhu.edu/account/',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    response=new_session.post(login_post,data=payload,headers=headers)
    return new_session

headers={'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

new_session=get_session()

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None


with open('urlDetails.txt','r',encoding='utf-8') as file:
    url_list=file.read().split('\n')

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
        if url_index%20==0 and url_index>0:
            new_session=get_session()
        url,url_id=url_list[url_index].split(',')
        data = []
        duplicate_list = []
        error_list = []
        completed_list = []
        print(url_id)
        pdf_count=1
        Ref_value = "5"

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

        All_issue_list=get_soup(url).find('div',{'id':'available_issues_list_text'}).findAll('h3')
        issue_link='https://muse.jhu.edu'+get_soup(url).find('div',{'id':'available_issues_list_text'}).findAll('ol')[get_current_issue(All_issue_list)].find('li').find('a').get('href')
        Volume_issue=get_soup(issue_link).find('div', class_='card_text').find('li').text.strip().split(',')
        Volume,Issue,Part,Year,Month=seperate_parameters.all_details(Volume_issue)
        all_articles=get_soup(issue_link).find('div', class_='cards_wrap vertical_list').findAll('div', class_='card row small-30 no_image')

        Total_count=len(all_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(all_articles):
            Article_link,Article_name = None,None
            try:
                Article_name=all_articles[article_index].find('li', class_='title').find('a').text.strip()
                Article_link = 'https://muse.jhu.edu'+all_articles[article_index].find('li', class_='title').find('a').get('href')

                Page_range = all_articles[article_index].find('li', class_='pg').text.strip().rsplit('p. ', 1)[-1].rstrip('.') if all_articles[article_index].find(
                    'li', class_='pg') else ""
                DOI = all_articles[article_index].find('li', class_='doi').text.strip().rsplit('doi.org/', 1)[-1].rstrip('.') if all_articles[article_index].find(
                    'li', class_='doi') else ""
                pdf_link='https://muse.jhu.edu'+all_articles[article_index].find('ul', class_='action_btns').findAll('li')[1].find('a').get('href')
                check_value,tpa_id = common_function.check_duplicate(DOI,Article_name, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_name)

                else:
                    pdf_content = new_session.get(pdf_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    if DOI=="":
                        DOI=read_pdf(output_fimeName)
                    data.append(
                        {"Title": Article_name, "DOI": DOI, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": Part,
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": "", "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_name)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message=f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :",Article_name)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

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
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the driver :" + str(error)
            print("Error in the driver or site")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
            #                                 len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0

