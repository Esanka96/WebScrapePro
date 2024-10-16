import re
import time

import requests
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime
import common_function
import pandas as pd
from PyPDF2 import PdfReader
from tenacity import retry, stop_after_attempt, wait_fixed

def read_pdf(pdf_path):
    file_path = pdf_path
    reader = PdfReader(file_path)
    last_page_index = len(reader.pages) - 1
    text=re.sub(r'\s+'," ",reader.pages[0].extract_text()).split()[:35]
    ISSN_index=text.index("E-ISSN:")+2
    first_page_text = text[ISSN_index]
    pageRange=str(first_page_text)+"-"+str(int(first_page_text)+last_page_index)
    return pageRange

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_pdf(url, out_path):
    with requests.get(url,headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

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

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "121"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1
        url_value=url.split('/')[-3]


        current_soup=get_soup(get_soup(url).find("table",class_="Newsletter_Content").find("table").find("tbody").find("tr").findAll("p")[1].find("a").get("href"))
        current_issue=current_soup.find("table",{"width":"603"}).find("td",{"width":"603"}).find("p")
        currentLink="https://www.jatit.org"+current_issue.find("a").get("href")

        volumeIssue=re.sub(r'\s+', ' ',current_issue.text.strip())
        if "New" in volumeIssue:
            volumeIssue=volumeIssue.replace(" (New)","")
        DOI=""
        try:
            try:
                Day=volumeIssue.split("th")[0]
            except:
                print("Failed to find the day","\n")
                Day=""

            try:
                monthYear=volumeIssue.split("th")[-1].split("|")[0].strip().split()
                Year=monthYear[-1]
                Month=monthYear[0]
            except:
                print("Failed to find month and year","\n")
                Month,Year="",""

            try:
                preVolumeIssue=volumeIssue.split("th")[-1].split("|")[-1].strip().split()
                Volume=re.sub(r'[^0-9]+',"",preVolumeIssue[0])
                Issue=re.sub(r'[^0-9]+',"",preVolumeIssue[-1])
            except:
                print("Failed to find volume and issue","\n")
                Volume,Issue="",""

        except:
            print("Failed to find Date and Volume","\n")
            Day,Month,Year,Volume,Issue="","","","",""

        lastSoup=get_soup(currentLink)

        try:
            All_articles = lastSoup.find("table",class_="Newsletter_Content").findAll("td",class_="auto-style4")[0].findAll("table")
        except:
            All_articles = lastSoup.find("table", class_="Newsletter_Content").findAll("td", class_="auto-style4")[
                1].findAll("table")

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            pdf_link, Article_title = None, None
            try:
                Article_title= re.sub(r'\s+'," ",All_articles[article_index].find("tbody").findAll("td")[1].text.strip())
                pdf_link=All_articles[article_index].find("tbody").find("a").get("href")

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{pdf_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    pdf_content = requests.get(pdf_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)

                    try:
                        Page_range=read_pdf(output_fimeName)
                    except:
                        print("Failed to read pdf file Therefore No page range","\n")
                        Page_range=""

                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{pdf_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title,"\n")

                if not pdf_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(pdf_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"Error link - {pdf_link} : {str(error)}"
                    print("Download failed :", Article_title,"\n")
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
            print(message)
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                            len(completed_list), url_id, Ref_value, attachment, current_out)
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
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