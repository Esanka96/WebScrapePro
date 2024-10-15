import re
import time
import requests
from bs4 import BeautifulSoup
import os
import shutil
import common_function
import SecondTypeUrl
import pandas as pd
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

def get_soup(url):
    global statusCode
    response = requests.get(url,headers=headers,timeout=10000,stream=True)
    statusCode = response.status_code
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")
    print()

def get_ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix

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
    oneError = 0

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_pdf(url, out_path):
    with requests.get(url,headers=headers, timeout=10000,stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def get_token(url):
    response = requests.get(url,headers=headers)
    cookie=response.cookies
    token=cookie.get("wkxt3_csrf_token").replace("-","")
    return token

def dayCheck(day):
    if day.isdigit():
        day = int(day)
        if 1 <= day <= 31:
            return day
    return ""

def monthCheck(month):
    valid_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December"]
    if month in valid_months:
        return month
    return ""

def yearCheck(year):
    if year.isdigit():
        return year
    return ""

def getPdfId(preId):
    id=re.search(r"\('(.*?)'\)",preId).group(1)
    return id

def getMonthYear(issueVolume):
    Year=issueVolume[-1].split(":")[-1].strip()
    Issue=next((item.split(":")[-1].strip() for item in issueVolume if "Issue" in item or "Número" in item),None)
    Volume=next((item.split(":")[-1].strip() for item in issueVolume if "Volume" in item),None)
    return Year,Volume,Issue

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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
Total_count=None
statusCode=None
oneError=0
whileCount=1

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
        if "=sci" in url:
            SecondTypeUrl.specificUrl(url,url_id,url_check)
        else:
            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            if url_check == 0:
                print_bordered_message("Scraping procedure will continue for ID:"+url_id)
                ini_path = os.path.join(os.getcwd(), "Info.ini")
                Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
                current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
                out_excel_file = common_function.output_excel_name(current_out)

            Ref_value = "51"

            duplicate_list = []
            error_list = []
            completed_list=[]
            data = []
            attachment = None
            pdf_count = 1

            currentSoup=get_soup("https://www.scielo.br"+get_soup(url).find("a",class_="btn active")["href"])

            try:
                issueVolume = currentSoup.find("div", class_="collapse-content issueIndent").text.strip().split(",")
                Year, Volume, Issue = getMonthYear(issueVolume)

            except:
                Year,Volume,Issue="","",""
            Month,Day="",""

            All_articles=currentSoup.find("ul",class_="articles").findAll("li",attrs={"data-date":True})

            Total_count=len(All_articles)
            print(f"Total number of articles:{Total_count}","\n")

            article_index, article_check = 0, 0
            while article_index < len(All_articles):
                Article_count = article_index+1
                pdf_link, Article_title = None, None
                try:
                    Article_link="https://www.scielo.br"+All_articles[article_index].find("ul").find("a")["href"]
                    Article_details=get_soup(Article_link)
                    Article_title=Article_details.find("h1",class_="article-title").text.strip()

                    try:
                        DOI =Article_details.find("a",class_="_doi").text.strip().rsplit("org/",1)[-1]
                    except:
                        print("Failed to find doi")
                        DOI = ""
                    Page_range=""

                    pdf_link="https://www.scielo.br"+Article_details.find("span",class_="sci-ico-filePDF").findParent().find_next_sibling("ul").find("li").find("a")["href"]

                    if article_check==0:
                        print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                    check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"📚"+ '\n')

                    else:
                        print("Wait until the PDF is downloaded")
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        download_pdf(pdf_link, output_fimeName)
                        print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

                        data.append(
                            {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": "",
                             "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                             "Year": Year,
                             "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"✅"+ '\n')

                    if not Article_link in read_content:
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')

                    article_index, article_check = article_index + 1, 0

                except Exception as error:
                    if article_check < 20:
                        article_check += 1
                    else:
                        message = f"{Article_link} : {str(error)}"
                        print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"❌"+ '\n')
                        error_list.append(message)
                        article_index, article_check = article_index + 1, 0

            try:
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                str(len(duplicate_list)),
                                                str(len(error_list)))
            except Exception as error:
                message = f"Failed to send post request : {str(error)}"
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
            time.sleep(5)
        else:
            try:
                url_index, url_check = url_index + 1, 0
                error_messages = {
                    200: "Server error: Unable to find HTML content",
                    400: "Error in the site: 400 Bad Request",
                    401: "Error in the site: 401 Unauthorized",
                    403: "Error in the site: Error 403 Forbidden",
                    404: "Error in the site: 404 Page not found!",
                    408: "Error in the site: Error 408 Request Timeout",
                    500: "Error in the site: Error 500 Internal Server Error"
                }
                Error_message = error_messages.get(statusCode)

                if Error_message ==None:
                    Error_message = "Error in the site:" + str(error)

                print(Error_message,"\n")
                error_list.append(Error_message)
                common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                     len(completed_list),
                                                     ini_path, attachment, current_date, current_time, Ref_value)

            except Exception as error:
                message = f"Failed to send email : {str(error)}"
                print(message)
                # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                #                                 len(completed_list), url_id, Ref_value, attachment, current_out)
                # error_list.append(message)