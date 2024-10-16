import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
import pandas as pd
from datetime import datetime
from PyPDF2 import PdfReader

def get_soup(url):
    response = requests.get(url,headers=headers)
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

def get_volumeIssue(preVolumeYear,value):
    try:
        Year = re.sub(r'[^0-9]+', '', preVolumeYear[value].strip().split()[-1])
    except:
        print("Failed to find year")
        Year = ""
    try:
        Month = datetime.strptime(preVolumeYear[value].strip().split()[-2].split("(")[-1], '%b').strftime('%B')
    except:
        print("Failed to find month")
        Month = ""
    try:
        Issue = preVolumeYear[value].strip().split()[1]
    except:
        print("Failed to find issue")
        Issue=""
    try:
        Volume = preVolumeYear[0].strip().split()[1]
    except:
        print("Failed to find volume")
        Volume=""
    return Year, Month, Issue, Volume

def get_yearMonth(preVolumeYear):
    check_count=len(preVolumeYear.split(":"))
    preVolumeYear=preVolumeYear.strip().split(":")
    if check_count==2:
        Year,Month,Issue,Volume = get_volumeIssue(preVolumeYear,-1)
        return Year, Month, Issue, Volume
    elif check_count==3:
        Year, Month, Issue, Volume = get_volumeIssue(preVolumeYear, 1)
        return Year,Month,Issue,Volume
    else:
        return "","","",""

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "avmajournals.avma.org",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
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
            print_bordered_message("Scraping procedure will continue for ID:"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "263"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        modifiedUrl="https://avmajournals.avma.org/view/journals/javma/javma-overview.xml?tab_body=toc"

        currentSoup=get_soup("https://avmajournals.avma.org"+get_soup(modifiedUrl).find("div",class_="text-title c-Link-emphasize color-text my-3 py-4 border-bottom-dark").find("a",
                    class_="c-Button--link").get("href"))

        preVolumeYear=currentSoup.find("div",class_="content-box box no-border no-header vertical-margin-bottom null").find("h2",class_="typography-body").text.strip()

        try:
            Year,Month,Issue,Volume=get_yearMonth(preVolumeYear)
        except:
            print("Failed to find year, volume and other details")
            Year,Month,Issue,Volume="","","",""
        Day = ""

        All_articles=currentSoup.findAll("div",class_="type-article leaf")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("a",class_="c-Button--link").text.strip()
                Article_link="https://avmajournals.avma.org"+All_articles[article_index].find("a",class_="c-Button--link").get("href")
                try:
                    Page_range=All_articles[article_index].find("dd",class_="pagerange").find("span",class_="typography-body").text.strip()
                except:
                    print("Failed to find page range")
                    Page_range=""
                Article_details=get_soup(Article_link)
                try:
                    DOI=Article_details.find("dd",class_="doi").find("span").find("a").text.strip().rsplit("org/",1)[-1]
                    pdf_value=DOI.split("/")[-1]
                except:
                    print("Failed to find doi")
                    DOI,pdf_value="",""

                pdf_link=f"https://avmajournals.avma.org/downloadpdf/view/journals/javma/{Volume}/{Issue}/{pdf_value}.pdf"

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    pdf_content = requests.get(pdf_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
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
                    print(get_ordinal_suffix(Article_count)+" article is original article" +"\n"+"Article title:", Article_title,"\n")

                if not pdf_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"\n")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        if str(Email_Sent).lower() == "true":
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
        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        print_bordered_message("Scraping has been successfully completed for ID:" + url_id)
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the site:" + str(error)
            print(Error_message,"\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
            #                                 len(completed_list), url_id, Ref_value, attachment, current_out)

            url_index, url_check = url_index + 1, 0