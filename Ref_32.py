import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
import pandas as pd

def get_soup(url):
    response = requests.get(url,timeout=10000,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def emailCompleted(Email_Sent,out_excel_file,url_id,duplicate_list,error_list,completed_list,ini_path,attachment,current_date,current_time,Ref_value,current_out):
    global oneError
    try:
        if str(Email_Sent).lower() == "true":
            attachment_path = out_excel_file
            if os.path.isfile(attachment_path):
                attachment = attachment_path
            else:
                attachment = None
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list), ini_path, attachment, current_date,
                                                 current_time, Ref_value)
    except Exception as error:
        message = f"Failed to send email : {str(error)}"
        common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
                                        completed_list,
                                        len(completed_list), url_id, Ref_value, attachment, current_out)
        #error_list.append(message)

    sts_file_path = os.path.join(current_out, 'Completed.sts')
    with open(sts_file_path, 'w') as sts_file:
        pass
    print_bordered_message("Scraping has been successfully completed for ID:" + url_id)
    oneError=0

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
oneError=0

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

        Ref_value = "32"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1

        current_soup=get_soup(url)

        Month,preMonth=current_soup.find('div',class_='journal_details').findAll('span',class_='bold')[0].text.strip().split('-')
        Year=preMonth.split()[-1]
        preV,Volume,preIss,Issue=current_soup.find('div',class_='journal_details').findAll('span',class_='bold')[1].text.strip().split(' ')

        All_articles=current_soup.find('div',class_='content_journal').findAll('div',class_='content_journalblock')

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link,Article_title = None,None
            try:
                Article_title = All_articles[article_index].find('h2').find('span').text.strip()
                Article_link = 'https://www.spandidos-publications.com'+All_articles[article_index].find('h2').find('a').get('href')
                Article_page=get_soup(Article_link)
                try:
                    DOI = Article_page.find('span',{'id':'doi'}).text.strip().rsplit('doi.org/',1)[-1]
                except:
                    print("Failed to find doi")
                    DOI = ""
                pdf_link = 'https://www.spandidos-publications.com'+Article_page.find('a',{'id':'downloadPDFURL'}).get('href')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    scrape_message = f"{Article_link}"
                    pdf_content = requests.get(pdf_link, timeout=10000,headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": "", "Month": Month, "Day": "",
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    completed_list.append(Article_link)
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 20:
                    article_check += 1
                else:
                    message=f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :",Article_title)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),
                            str(len(error_list)))
        except Exception as error:
            message=f"Failed to send post request : {str(error)}"
            error_list.append(message)

        try:
            if str(Email_Sent).lower() == "true":
                attachment_path = out_excel_file
                if os.path.isfile(attachment_path):
                    attachment = attachment_path
                else:
                    attachment = None
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list), ini_path, attachment, current_date,
                                                     current_time, Ref_value)
        except Exception as error:
            message = f"Failed to send email : {str(error)}"
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
                                            completed_list,
                                            len(completed_list), url_id, Ref_value, attachment, current_out)
            # error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        print_bordered_message("Scraping has been successfully completed for ID:" + url_id)

        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 10:
            url_check += 1
        else:
            try:
                Error_message = "Error in the site:" + str(error)
                print(Error_message,"\n")
                error_list.append(Error_message)
                url_index, url_check = url_index + 1, 0
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list),
                                                     ini_path, attachment, current_date, current_time, Ref_value)
                # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                #                                 len(completed_list), url_id, Ref_value, attachment, current_out)


            except Exception as error:
                message = f"Failed to send email : {str(error)}"
                print(message)
                common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                                len(completed_list), url_id, Ref_value, attachment, current_out)
                error_list.append(message)


