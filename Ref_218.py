import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
import TOC_HTML
import pandas as pd
from datetime import datetime

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
            print_bordered_message("Scraping procedure will continue for ID:"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)
        TOC_name = "{}_TOC.html".format(url_id)

        Ref_value = "218"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        languageList =["https://www.swdzgcdz.com/en/article/current",
                       "https://www.swdzgcdz.com/article/current"]

        currentSoup=get_soup("https://www.swdzgcdz.com"+get_soup("https://www.swdzgcdz.com"+get_soup(url).find("ul",class_="smallUl").find("li",{"type":"english"}).
                             find("a").get("href")).find("ul",class_="nav-inner clearfix container").find("li",{"type":"current_en"}).find("a").get("href"))

        All_articles = currentSoup.find("div",{"id":"issueList"}).findAll("div",class_="article-list")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link, Article_title = None, None
            try:
                Article_title = All_articles[article_index].find("div",class_="article-list-title clearfix").find("a").text.strip()
                Article_link="https://www.swdzgcdz.com"+All_articles[article_index].find("div",class_="article-list-title clearfix").find("a").get("href")
                try:
                    volumeYear=All_articles[article_index].find("div",class_="article-list-time").find("font").text.strip().split()
                    try:
                        Year=re.sub(r'[^0-9]+','',volumeYear[0])
                    except:
                        print("Failed to find year")
                        Year=""
                    try:
                        volumeIssue=volumeYear[1].split("(")
                        try:
                            Volume=re.sub(r'[^0-9]+','',volumeIssue[0])
                        except:
                            print("Failed to find volume")
                            Volume = ""
                        try:
                            Issue=re.sub(r'[^0-9]+','',volumeIssue[1])
                        except:
                            print("Failed to find issue")
                            Issue = ""
                    except:
                        print("Failed to find issue and volume")
                        Volume,Issue="",""
                    try:
                        Page_range=volumeYear[2].rstrip(".")
                    except:
                        print("Failed to find page range")
                        Page_range=""
                except:
                    print("Failed to find year, volume, issue and page range")
                    Year,Volume,Issue,Page_range="","","",""

                try:
                    DOI=All_articles[article_index].find("div",class_="article-list-time").findAll("font")[1].find("a").text.strip()
                except:
                    print("Failed to find doi")
                    DOI = ""
                Month=""
                Day=""

                try:
                    Article_id= All_articles[article_index].find("div",
                                                                     class_="article-list-zy article-list-btn clear").find(
                        "font", class_="font3").find("a").get("onclick").split("'")[1]
                except:
                    Article_id = ""

                pdf_link=f"https://www.swdzgcdz.com/article/exportPdf?id={Article_id}&language=en"

                print(get_ordinal_suffix(pdf_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    pdf_content = requests.get(pdf_link, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    print(get_ordinal_suffix(pdf_count)+" PDF file has been successfully downloaded")

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
                    print("Original Article :", Article_title,"\n")

                if not pdf_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print("Download failed :", Article_title,"\n")
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0
        check = 0
        while check < 5:
            try:
                print("Wait until the TOC_PDF is downloaded")
                TOC_HTML.get_toc_html(current_out,TOC_name,languageList)
                check=5
                print("TOC_PDF file downloaded successfully.")
            except:
                if not check < 4:
                    message="Failed to get toc pdf"
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
        except Exception as error:
            message=f"Failed to send email : {str(error)}"
            common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                            len(completed_list), url_id, Ref_value, attachment, current_out)
            error_list.append(message)

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