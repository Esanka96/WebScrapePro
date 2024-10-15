import re
import time
import requests
from bs4 import BeautifulSoup
import os
import common_function
from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
import random

proxies_list = [
    "185.205.199.161:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "216.10.5.126:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.96.233:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.121.110:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "67.227.127.100:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "181.177.76.122:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "185.207.97.85:3199:mariyarathna-dh3w3:IxjkW0fdJy",
    "186.179.21.77:3199:mariyarathna-dh3w3:IxjkW0fdJy",
]

formatted_proxies = [{'http': f'http://{proxy.split(":")[2]}:{proxy.split(":")[3]}@{proxy.split(":")[0]}:{proxy.split(":")[1]}'} for proxy in proxies_list]

# formatted_proxies = []
# for proxy in proxies_list:
#     ip, port, user, password = proxy.split(':')
#     formatted_proxy = f'http://{user}:{password}@{ip}:{port}'
#     formatted_proxies.append({'http': formatted_proxy, 'https': formatted_proxy})

def get_random_proxy():
    return random.choice(formatted_proxies)

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
    with requests.get(url,headers=headers, stream=True) as r:
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

def get_doi(url):
    new_session = requests.session()

    firstUrl = "https://opg.optica.org/"

    headers1 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # "Cookie": "cfid=9c3c12a2-c57b-4d87-b9f9-84d70428e4e6; cftoken=0; _gid=GA1.2.414981455.1721732994; COOKIECONSENT=yes; _ga_EGFN5DM8HB=GS1.1.1721732989.1.1.1721735296.53.0.0; _ga=GA1.2.789266793.1721732990; _gat=1",
        "Host": "opg.optica.org",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    new_session.get(firstUrl, headers=headers1)

    secondUrl = "https://opg.optica.org/jot/issue.cfm"

    headers2 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "opg.optica.org",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    new_session.get(secondUrl, headers=headers2)

    res = new_session.get(url)
    DOI =BeautifulSoup(res.content, 'html.parser').find("li", class_="article-doi").find("a").text.strip().rsplit("org/", 1)[-1]
    return DOI

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
whileCount=10

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

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": "cfid=9c3c12a2-c57b-4d87-b9f9-84d70428e4e6; cftoken=0; _gid=GA1.2.414981455.1721732994; COOKIECONSENT=yes; _ga_EGFN5DM8HB=GS1.1.1721732989.1.1.1721736558.58.0.0; _ga=GA1.2.789266793.1721732990",
            "Host": "opg.optica.org",
            "Pragma": "no-cache",
            "Referer": url,
            "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check == 0:
            print_bordered_message("Scraping procedure will continue for ID:"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "8"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1

        baseUrl=url.split("issue")[0]
        currentSoup=get_soup(url)

        try:
            issueVolume = currentSoup.find("h2",class_="heading-block-header")
            if issueVolume.find("small"):
                issueVolume.find("small").extract()
            issueVolume=issueVolume.text.strip()

            pattern=r"(\d{1,2}) (\w+) (\d{4}), Volume (\d+), Issue (\d+)"
            Day,Month,Year,Volume,Issue=re.search(pattern,issueVolume).groups()
        except:
            Volume,Year,Issue,Month,Day="","","","",""

        All_articles=currentSoup.findAll("div",class_="media-twbs")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            time.sleep(10)
            Article_count = article_index+1
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("p",class_="article-title").a.text.strip()
                Article_link = "https://opg.optica.org" +All_articles[article_index].find("p",class_="article-title").a["href"]
                article_id=Article_link.split("uri=")[-1].split("&id")[0]
                print(Article_link)

                # try:
                #     pageRange=re.sub(r'\s+',' ',All_articles[article_index].find("p",class_="article-authors").find_next_sibling("p").text.strip())
                #     Page_range=re.search(r'\), (.*?) \(',pageRange).group(1)
                #     if Page_range[-1]=="-":
                #         Page_range=Page_range.replace("-","")
                # except:
                #     Page_range=""

                try:
                    DOI = get_doi(Article_link)
                except:
                    DOI=""
                print(DOI)

                #pdf_link=baseUrl+Article_details.find("li",class_="pdf-download").a["href"]
                # pdf_link=f"{baseUrl}viewmedia.cfm?uri={article_id}&seq=0"
                #
                # headersPdf = {
                #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                #     "Accept-Encoding": "gzip, deflate, br, zstd",
                #     "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                #     "Cache-Control": "no-cache",
                #     "Connection": "keep-alive",
                #     "Cookie": "cfid=9c3c12a2-c57b-4d87-b9f9-84d70428e4e6; cftoken=0; _gid=GA1.2.414981455.1721732994; COOKIECONSENT=yes; _ga_EGFN5DM8HB=GS1.1.1721732989.1.1.1721736558.58.0.0; _ga=GA1.2.789266793.1721732990",
                #     "Host": "opg.optica.org",
                #     "Pragma": "no-cache",
                #     "Referer": url,
                #     "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
                #     "Sec-Ch-Ua-Mobile": "?0",
                #     "Sec-Ch-Ua-Platform": "\"Windows\"",
                #     "Sec-Fetch-Dest": "document",
                #     "Sec-Fetch-Mode": "navigate",
                #     "Sec-Fetch-Site": "same-origin",
                #     "Sec-Fetch-User": "?1",
                #     "Upgrade-Insecure-Requests": "1",
                #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                # }
                #
                # if article_check==0:
                #     print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                # check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                #
                # if Check_duplicate.lower() == "true" and check_value:
                #     message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                #     duplicate_list.append(message)
                #     print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"📚"+ '\n')
                #
                # else:
                #     if article_check==0:
                #         print("Wait until the PDF is downloaded")
                #     print(pdf_link)
                #
                #     output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                #     download_pdf(pdf_link, output_fimeName,headersPdf)
                #
                #     if article_check < 10:
                #         checkreadeblePdf(output_fimeName)
                #
                #     print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")
                #
                #     data.append(
                #         {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                #          "Identifier": "",
                #          "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                #          "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                #          "Year": Year,
                #          "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                #
                #     df = pd.DataFrame(data)
                #     df.to_excel(out_excel_file, index=False)
                #     pdf_count += 1
                #     scrape_message = f"{Article_link}"
                #     completed_list.append(scrape_message)
                #     print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"✅"+ '\n')
                #
                # if not Article_link in read_content:
                #     with open('completed.txt', 'a', encoding='utf-8') as write_file:
                #         write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 10:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"❌"+ '\n')
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        # try:
        #     common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
        #                                     str(len(duplicate_list)),
        #                                     str(len(error_list)))
        # except Exception as error:
        #     message = f"Failed to send post request : {str(error)}"
        #     error_list.append(message)
        #
        # try:
        #     if str(Email_Sent).lower() == "true":
        #         attachment_path = out_excel_file
        #         if os.path.isfile(attachment_path):
        #             attachment = attachment_path
        #         else:
        #             attachment = None
        #         common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
        #                                              len(completed_list), ini_path, attachment, current_date,
        #                                              current_time, Ref_value)
        # except Exception as error:
        #     message = f"Failed to send email : {str(error)}"
        #     common_function.email_body_html(current_date, current_time, duplicate_list, error_list,
        #                                     completed_list,
        #                                     len(completed_list), url_id, Ref_value, attachment, current_out)
        #     # error_list.append(message)
        #
        # sts_file_path = os.path.join(current_out, 'Completed.sts')
        # with open(sts_file_path, 'w') as sts_file:
        #     pass
        print_bordered_message("Scraping has been successfully completed for ID:" + url_id)

        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 10:
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