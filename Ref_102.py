import re
import time
import shutil
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd

def get_article_title(Article_link,url):
    session = requests.session()
    session.get(Article_link)
    response = session.get(url,headers=headers)
    Article_title = BeautifulSoup(response.content, 'html.parser').find('h1',class_='fs-4 fw-bold text-notransform mb-3').text.strip()
    return Article_title

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

def get_soup(url):
    response = requests.get(url, timeout=10000,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value=None
ini_path=None
oneError=0
whileCount=5

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the urls text file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)

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
        url,url_id=url_list[url_index].split(',')
        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "102"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1
        url_value=url.split('/')[-2]

        current_soup=get_soup(url)

        try:
            Year_Month=current_soup.find('span',class_='NumFascicolo').text.strip().split('/')

            try:
                Year=re.sub(r'[^0-9]+','',Year_Month[-1].strip())
            except:
                Year=""

            try:
                Issue=re.sub(r'[^0-9]+','',Year_Month[0])
            except:
                Issue=""

        except:
            Year,Issue="",""

        All_articles=current_soup.find('article',class_='mb-5').findAll('ul',class_='lines mt-3 mb-3')

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link, Article_title = None, None
            try:
                Checked_link =All_articles[article_index].find('a').get('href')
                if "https://" in Checked_link:
                    Article_link=Checked_link
                    intermediateValue=re.search(r'php/(.*?)/article', Article_link).group(1)
                    articleIndex=Article_link.split("/")[-1]
                    correctedUrl=f"https://journals.francoangeli.it/index.php/{intermediateValue}/user/setLocale/en_US?source=%2Findex.php%2F{intermediateValue}%2Farticle%2Fview%2F{articleIndex}"
                    Article_title=BeautifulSoup(requests.get(correctedUrl).content,'html.parser').find("h1",class_='article-page__title').text.strip()
                    Article_details = get_soup(Article_link)

                    try:
                        DOI=Article_details.find("a",{"id":"pub-id::doi"}).text.strip().rsplit("org/",1)[-1]
                    except:
                        DOI=""

                    pdf_link=get_soup(Article_details.find("a",class_="article__btn pdf").get("href")).find("div",
                        class_="pdf-download-button").find("a").get("href")
                else:
                    Article_link = 'https://www.francoangeli.it' + All_articles[article_index].find('a').get('href')
                    Relevant_article_link="https://www.francoangeli.it/SetLanguage?culture=en&returnUrl=%2Friviste%2Farticolo%2F"+Article_link.split("/")[-1]
                    Article_title=get_article_title(Article_link,Relevant_article_link)
                    Article_details=get_soup(Article_link)

                    try:
                        DOI=re.search(r'DOI (.*?) Il', re.sub(r'\s+',' ',Article_details.find('p',class_='fs-7 mb-5').text.strip())).group(1)
                    except:
                        DOI=""

                    pdf_link='https://www.francoangeli.it'+Article_details.find('a',class_='btn blu h-auto mb-3').get('href')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, "", Issue)
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
                         "Volume": "", "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": "", "Month": "", "Day": "",
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 25:
                    article_check += 1
                else:
                    message = f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :", Article_title)
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
        if url_check < 12:
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






