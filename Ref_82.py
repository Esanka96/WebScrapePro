from datetime import datetime
import pandas as pd
import os
import re
import requests
import time
from bs4 import BeautifulSoup
import common_function
import random
import cloudscraper


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


def get_random_proxy():
    return random.choice(formatted_proxies)

def resolveCloudFlare():
    scraper.proxies.update(get_random_proxy())
    firstUrl = "https://www.utpjournals.press/"

    headers1 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Arch": "\"x86\"",
        "Sec-Ch-Ua-Bitness": "\"64\"",
        "Sec-Ch-Ua-Full-Version": "\"126.0.6478.127\"",
        "Sec-Ch-Ua-Full-Version-List": "\"Not/A)Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"126.0.6478.127\", \"Google Chrome\";v=\"126.0.6478.127\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Model": "\"\"",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Ch-Ua-Platform-Version": "\"15.0.0\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    scraper.get(firstUrl, headers=headers1)

    secondUrl = "https://www.utpjournals.press/journal/jcfs"

    headers2 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Arch": "\"x86\"",
        "Sec-Ch-Ua-Bitness": "\"64\"",
        "Sec-Ch-Ua-Full-Version": "\"126.0.6478.127\"",
        "Sec-Ch-Ua-Full-Version-List": "\"Not/A)Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"126.0.6478.127\", \"Google Chrome\";v=\"126.0.6478.127\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Model": "\"\"",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Ch-Ua-Platform-Version": "\"15.0.0\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    scraper.get(secondUrl, headers=headers2)

def month_check(month,nor_month):
    Month_list = ['spring', 'fall', 'autumn', 'autumne', 'winter', 'augusto', 'avril', 'juin', 'junio', 'marzo',
                  'oktober', 'summer', 'dezember', 'abril', 'mayo', 'mars', 'décembre', 'septembre','dece','janvier',
                  'février','octobre','novembre']
    if month in Month_list:
        month_mapping = {
            'spring': 'March', 'fall': 'September', 'autumn': 'September', 'autumne': 'September', 'winter': 'December',
            'augusto': 'August', 'avril': 'April','novembre': 'November',
            'juin': 'June', 'junio': 'June', 'marzo': 'March', 'oktober': 'October', 'summer': 'June',
            'dezember': 'December','janvier': 'January','février': 'February','octobre': 'October',
            'abril': 'April', 'mayo': 'May', 'mars': 'March', 'décembre': 'December', 'septembre': 'September','dece': 'December'
        }
        return month_mapping.get(month)
    else:
        return nor_month

def check_month(details):
    if len(details)==3:
        Volume=re.sub(r'[^0-9]+','',details[0])
        Issue = re.sub(r'[^0-9]+', '', re.split(r'[\\-]', details[1])[0])
        Year=re.sub(r'[^0-9]+', '', details[2])
        if "|" in details[2]:
            pre_month=re.sub(r'[^a-zA-Z]+', '', details[2].split('|')[0])
            Year=Year if re.sub(r'[^0-9]+', '', details[2].split('|')[0]) =="" else re.sub(r'[^0-9]+', '', details[2].split('|')[0])
        elif "/" in details[2]:
            pre_month = re.sub(r'[^a-zA-Z]+', '', details[2].split('/')[0])
            Year=Year if re.sub(r'[^0-9]+', '', details[2].split('/')[0]) =="" else re.sub(r'[^0-9]+', '', details[2].split('/')[0])
        else:
            pre_month = re.sub(r'[^a-zA-Z]+', '', details[2])
        Month=month_check(pre_month.lower(),pre_month)
        return Volume,Issue,Month,Year
    else:
        Volume = re.sub(r'[^0-9]+', '', details[0])
        Year = re.sub(r'[^0-9]+', '', details[1])
        if "|" in details[1]:
            pre_month=re.sub(r'[^a-zA-Z]+', '', details[1].split('|')[0])
        elif "/" in details[1]:
            pre_month = re.sub(r'[^a-zA-Z]+', '', details[1].split('/')[0])
        else:
            pre_month = re.sub(r'[^a-zA-Z]+', '', details[1])
        Month=month_check(pre_month.lower(),pre_month)
        return Volume,"",Month,Year


duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value="82"
ini_path=None
Total_count=None
statusCode=None


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

        Ref_value = "82"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment=None
        pdf_count = 1
        url_value=url.split('/')[-2]

        scraper = cloudscraper.create_scraper()
        resolveCloudFlare()

        current_soup = BeautifulSoup(scraper.get(url).content, 'html.parser')
        All_articles=current_soup.find('div',class_='tocContent').findAll('table',class_='articleEntry')
        Volume,Issue,Month,Year=check_month(re.sub(r'\s+','',current_soup.find('h3',class_='tocListHeader').text.strip()).split(','))

        Total_count = len(All_articles)
        print(f"Total number of articles:{Total_count}", "\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            time.sleep(10)
            Article_link,Article_title=None,None
            try:
                try:
                    Pre_link='https://www.utpjournals.press'+All_articles[article_index].find('a',class_='ref nowrap').get('href')
                    DOI = str(Pre_link).rsplit('abs/', 1)[-1] if not "full" in Pre_link else str(Pre_link).rsplit('full/', 1)[-1]
                except:
                    DOI = ""
                Article_link ='https://www.utpjournals.press/doi/abs/'+DOI+'?journalCode='+url_value
                Article_title = All_articles[article_index].find('a',class_='ref nowrap').text.strip()
                try:
                    Page_range=All_articles[article_index].find('span',class_='articlePageRange').text.strip().rsplit('p. ',1)[-1]
                except:
                    Page_range = ""

                pdf_link = f"https://www.utpjournals.press/doi/pdf/{DOI}?download=true"


                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title+"\n")

                else:
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    pdf_content = scraper.get(pdf_link).content
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)

                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": "",
                         "Year": Year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})

                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title+"\n")

                if not pdf_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message=f"{Article_link} : {str(error)}"
                    print("Download failed :",Article_title+"\n")
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
        except Exception as error:
            message=f"Failed to send email : {str(error)}"
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
                url_index, url_check = url_index + 1, 0
                error_messages = {
                    200: "Error in the site: Full HTML content could not be found",
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






