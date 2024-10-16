import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
import TOC_HTML
import pandas as pd
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

def get_soup(url):
    global statusCode
    response = requests.get(url,headers=headers,stream=True)
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

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def download_pdf(url, out_path,headers):
    with requests.get(url,headers=headers,stream=True) as r:
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


headers = {

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
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
        pre_url, url_id = url_list[url_index].split(',')
        url="https://www.pgtjournal.com/EN/2096-4528/current.shtml"

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("Scraping procedure will continue for ID:"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)
        TOC_name = "{}_TOC.html".format(url_id)

        Ref_value = "3667"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1

        currentSoup=get_soup(url)

        languageList =[currentSoup,
                       get_soup("https://www.pgtjournal.com/CN/2096-4528/current.shtml")]

        try:
            volumeIssue=currentSoup.find("div",class_="nianjq").text.strip()
            pattern=r"Volume (\d+) Issue (\d+), (\d+) (\w+) (\d{4})"
            Volume,Issue,Day,Month,Year=re.search(pattern,volumeIssue).groups()
        except:
            Year,Volume,Issue,Month,Day="","","","",""

        All_articles=currentSoup.find("form",attrs={"id":"AbstractList"}).findAll("div",class_="noselectrow")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            error_variable = None
            try:
                error_variable = "article link"
                Article_link = All_articles[article_index].find("a",class_="txt_biaoti")["href"]

                error_variable = "article title"
                Article_title=All_articles[article_index].find("a",class_="txt_biaoti").text.strip()

                try:
                    Page_range = All_articles[article_index].find("span",class_="abs_njq").get_text(strip=True).split()[-1].rstrip(".")
                except:
                    Page_range=""

                try:
                    DOI=All_articles[article_index].find("div",class_="abs_njq").get_text(strip=True).rsplit("org/",1)[-1]
                except:
                    DOI=""

                error_variable = "pdf link"
                token=get_token("https://www.pgtjournal.com/EN/2096-4528/current.shtml")
                pdf_link="https://www.pgtjournal.com/EN/PDF/{0}?token={1}".format(DOI,token)

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")

                error_variable = "duplicate check"
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"📚"+ '\n')

                else:
                    print("Wait until the PDF is downloaded")
                    error_variable = "pdf download"

                    pdf_headers = {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "accept-encoding": "gzip, deflate, br, zstd",
                        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                        "cache-control": "max-age=0",
                        "connection": "keep-alive",
                        #"cookie": "Secure; JSESSIONID=59B64ADCF9D1DA53C114658E7575686D; wkxt3_csrf_token=46c10090-4854-4971-a152-075ccf3e3259; Secure",
                        "host": "www.pgtjournal.com",
                        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "sec-fetch-dest": "document",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-site": "none",
                        "sec-fetch-user": "?1",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                    }

                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    download_pdf(pdf_link, output_fimeName,pdf_headers)

                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

                    error_variable = "write excel"
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                         "Year": Year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id,"TOC":TOC_name})

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
                if article_check < 30:
                    article_check += 1
                else:
                    message = f"{Article_link} - Error in {error_variable} for {Article_title} : [{str(error)}]"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"❌"+ '\n')
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        check = 0
        while check < 5:
            try:
                print("Wait until the TOC_HTML is downloaded")
                TOC_HTML.get_toc_html(current_out,TOC_name,languageList)
                check = 5
                print("TOC_HTML file downloaded successfully.")
            except:
                if not check < 4:
                    message = "Failed to get toc pdf"
                    error_list.append(message)
                check += 1

        for attempt in range(25):
            try:
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),str(len(duplicate_list)), str(len(error_list)))
                break
            except Exception as error:
                if attempt == 24:
                    error_list.append(f"Failed to send post request : {str(error)}")

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
        if url_check < 15:
            url_check += 1
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
                common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                                len(completed_list), url_id, Ref_value, attachment, current_out)
                error_list.append(message)