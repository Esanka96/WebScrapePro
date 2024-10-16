import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

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
            print_bordered_message("Scraping procedure will continue for ID:"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "134"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1
        url_value=url.split("/")[3]

        if url=="http://xuebao.jlu.edu.cn/gxb/CN/1671-5497/home.shtml":
            url=url.replace("home","current").replace("CN", "EN")

        currentSoup=get_soup(url)
        try:
            volumeYear=currentSoup.find("div",class_="nianjq").text.strip().split()
            try:
                Issue=volumeYear[-1]
            except:
                print("Failed to find issue")
                Issue=""
            try:
                Volume=volumeYear[-3]
            except:
                print("Failed to find volume")
                Volume=""
            try:
                Year=re.sub(r'[^0-9]+','',volumeYear[2])
            except:
                print("Failed to find year")
                Year=""

            if url=="http://xuebao.jlu.edu.cn/yxb/EN/1671-587X/current.shtml":
                try:
                    Month=volumeYear[1]
                except:
                    print("Failed to find month")
                    Month=""
                try:
                    Day=volumeYear[0]
                except:
                    print("Failed to find day")
                    Day=""
            else:
                Month,Day="",""
        except:
            print("Failed to find volume, year and other details")
            Issue,Volume,Year,Month,Day="","","","",""

        All_articles = currentSoup.find("div",class_="articles margin-15").find("form",{"id":"AbstractList"}).findAll("div",class_="noselectrow")

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("a",class_="txt_biaoti").text.strip()
                Article_link=All_articles[article_index].find("a",class_="txt_biaoti").get("href")
                Article_id=All_articles[article_index].get("id").replace("art","")

                try:
                    pageRangeDoi=re.sub(r'\s+','',All_articles[article_index].find("span",class_="abs_njq").text.strip())
                    try:
                        DOI=pageRangeDoi.rsplit("DOI:",1)[-1]
                    except:
                        print("Failed to find doi")
                        DOI = ""
                    try:
                        Page_range=re.search(r'\):(.*?).DOI',pageRangeDoi).group(1)
                    except:
                        print("Failed to find page range")
                        Page_range = ""
                except:
                    print("Failed to find page range and doi")
                    Page_range,DOI="",""

                pdf_link=f"http://xuebao.jlu.edu.cn/{url_value}/EN/article/downloadArticleFile.do?attachType=PDF&id={Article_id}"

                if article_check == 0:
                    print("Article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title,"\n")

                else:
                    print("Wait until the PDF is downloaded")
                    # pdf_content = requests.get(pdf_link, headers=headers).content
                    # output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    # with open(output_fimeName, 'wb') as file:
                    #     file.write(pdf_content)

                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    download_pdf(pdf_link, output_fimeName)
                    print(get_ordinal_suffix(pdf_count)+" PDF file has been successfully downloaded")

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