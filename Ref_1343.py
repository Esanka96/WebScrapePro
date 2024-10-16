import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
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
        url="https://xuebaozr.sysu.edu.cn/en/home/"

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

        Ref_value = "1343"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1
        baseUrl="https://lxsj.cstam.org.cn"

        current_id = get_soup(url).find("div", attrs={"first-periods-id": True})["first-periods-id"]
        json_url = f"https://zsdz.publish.founderss.cn/rc-pub/front/front-article/getArticlesByPeriodicalIdGroupByColumn/{current_id}?showCover=false&timestamps="

        headers_json = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'zsdz.publish.founderss.cn',
            # 'Referer': 'https://zsdz.publish.founderss.cn/academic?columnId=&type=directory&index=4&parentIndex=4&date=1726756637739&activeName=146341&year=2024&page=0&bannerId&lang=en&siteIds=',
            'Sec-CH-UA': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'SiteId': '189',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }

        response = requests.get(json_url, headers=headers_json)

        currentSoup = response.json()

        All_articles=currentSoup["data"][0]["content"]

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        html_body_en = ""
        html_body_cn = ""

        first_line=f"Volume {All_articles[0]["volume"]}  Issue {All_articles[0]["issue"]}，{All_articles[0]["year"]}"
        html_body_en += f"<h2>{first_line}</h2>\n"

        first_line_cn=f"{All_articles[0]["year"]}年{All_articles[0]["volume"]}卷第{All_articles[0]["issue"]}期"
        html_body_cn += f"<h2>{first_line_cn}</h2>\n"

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            error_variable = None
            Art_index=All_articles[article_index]
            try:
                error_variable = "meta data"
                DOI = Art_index["doi"]
                Year = Art_index["year"]
                Id = Art_index["id"]
                Volume = Art_index["volume"]
                Issue = Art_index["issue"]
                Page_range = f"{Art_index["firstPageNum"]}-{Art_index["lastPageNum"]}"
                Month,Day="",""

                error_variable = "article link"
                Article_link = f"https://xuebaozr.sysu.edu.cn/thesisDetails#{DOI}&lang=en"

                error_variable = "article title"
                Article_title=Art_index["enResName"]

                error_variable = "create toc"
                html_body_en += f"<div class='article'>\n"
                html_body_en += f"<a href=href='{Article_link}' style='text-decoration:none;' color:#00f;'><h3 >{Article_title}</h3></a>\n"
                html_body_en += f"<p>{Art_index['enAuthors']}</p>\n"
                html_body_en += f"<p>DOI: <a href='https://doi.org/{DOI}'>{DOI}</a></p>\n"
                html_body_en += f"<p>Abstract：{Art_index['enSummary']}</p>\n"
                html_body_en += f"<p><HTML><L-PDF><Meta-XML><Citation><Bulk Citation></p>\n"
                html_body_en += "</div>\n"

                html_body_cn += f"<div class='article''>\n"
                html_body_cn += f"<a href='{Article_link}' style='text-decoration:none;' color:#00f;><h3 >{Art_index["resName"]}</h3></a>\n"
                html_body_cn += f"<p>{Art_index['authors']}</p>\n"
                html_body_cn += f"<p>DOI: <a href='https://doi.org/{DOI}'>{DOI}</a></p>\n"
                html_body_cn += f"<p>摘要：{Art_index['summary']}</p>\n"
                html_body_cn += f"<p><HTML><网络PDF><Meta-XML><引用本文><批量引用></p>\n"
                html_body_cn += "</div>\n"

                error_variable = "pdf link"
                pdf_link=f"https://zsdz.publish.founderss.cn/rc-pub/front/front-article/download?id={Id}&attachType=lowqualitypdf&token=&language=en"

                error_variable = "xml link"
                xml_link=f"https://zsdz.publish.founderss.cn/rc-pub/front/front-article/download?id={Id}&attachType=metaxml&token=&language=en"

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
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                    }

                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    download_pdf(pdf_link, output_fimeName,pdf_headers)

                    output_fimeName_xml = os.path.join(current_out, f"{pdf_count}.xml")
                    with open(output_fimeName_xml, "wb") as file:
                        file.write(requests.get(xml_link).content)

                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

                    error_variable = "write excel"
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                         "Year": Year,
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "XML File Name": f"{pdf_count}.xml","user_id": user_id,"TOC":TOC_name})

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
                out_html=os.path.join(current_out,TOC_name)
                with open(out_html, 'w', encoding='utf-8') as file:
                    file.write(html_body_en+html_body_cn)
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