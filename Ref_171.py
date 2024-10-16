import re
import requests
from bs4 import BeautifulSoup
import os
import common_function
import TOC_HTML
import pandas as pd
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
import random
import time

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

def getPdfWithProxies(url):
    pdf_content = BeautifulSoup(requests.get(url, headers=headers).content,"html.parser")
    return pdf_content

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

# def download_pdf(pdf_link, out_path):
#     pdf_content = requests.get(pdf_link, headers=headers,timeout=250).content
#     with open(out_path, 'wb') as file:
#         file.write(pdf_content)

def download_pdf(url, out_path):
    with requests.get(url, headers=headers) as r:
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

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    #"Cookie": "ASP.NET_SessionId=lp45qdmcbdr3e3jrp1g0vked",
    "Host": "lyspkj.ijournal.cn",
    "Referer": "http://lyspkj.ijournal.cn/lyspkjen/issue/browser",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

headersChines = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    #"Cookie": "The_Company_of_BiologistsMachineID=638505741362209925; fpestid=8vNK_m__2BcaJLTA_nWIiDKhF8UZAz5411b5OSXAbKBA5WO0Gz3iRVl-458ZIf1htrWnNg; __stripe_mid=c3b18f06-03d3-4a03-a426-802ba209e20d0f4d57; _cc_id=cafdec109ff312a1c2e42977d4df533a; OptanonAlertBoxClosed=2024-05-06T06:35:45.512Z; COB_SessionId=3gxogrz20cyxvbveji01rojo; __cf_bm=.Lxulmwnwcor39pg3W1w86VU_gAxeD2EEcPNb4yV.gg-1719374137-1.0.1.1-fjtBoItry6MJ.UK4GR6bnwjGhP2cqOGL3kbCNCc23K.IQdq4Uh7aV9BywjP6R0NKkMObrN92FrB94nuqTxjZ5w; cf_clearance=uvU1fsoJMUW5Ywy8sMbhXFUV29blLuRJUAKS_DR9R_s-1719374140-1.0.1.1-YAVqb.MCUhJltJa1RgTJsEhzMRcrDjF2nHYJ_TWvyEUfKja.2FgWpknLhU3hBiou1WjbiWR9SVaNct0JWAPIOw; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Jun+26+2024+09%3A26%3A32+GMT%2B0530+(India+Standard+Time)&version=202403.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=5436df06-d8f6-414a-be74-4477e0f35dc5&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0002%3A1%2CC0001%3A1&geolocation=LK%3B1&AwaitingReconsent=false; _ga_YXBDEHVL2V=GS1.1.1719374193.5.0.1719374193.0.0.0; __gads=ID=d7dc8a1f0e6edb6c:T=1714977341:RT=1719374141:S=ALNI_MYX1uR5YvG39Rjt7HFvLdZa2dEObw; __gpi=UID=00000e0d984f80c4:T=1714977341:RT=1719374141:S=ALNI_MZpJvMIjHlpqvLv1kBYEUZpJOFIig; __eoi=ID=b571390403ad6f60:T=1714977341:RT=1719374141:S=AA-AfjaErBnPrUkhX2htosl2_2aL; panoramaId_expiry=1719978942096; panoramaId=53f6b4c4b73d554d5c6a325e0eb416d53938eadfba7b839999e0a28806200879; panoramaIdType=panoIndiv; _ga=GA1.2.468755934.1714977344; _gid=GA1.2.1587264678.1719374194; _gat_UA-57233518-6=1",
    "Priority": "u=0, i",
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


valid_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
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

        Ref_value = "171"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        currentSoup=get_soup(url)
        engUrl="http://lyspkj.ijournal.cn/"+currentSoup.find("div",class_="slideBox_nr").find("a").get("href")
        chUrl=engUrl.replace("lyspkjen","lyspkj")

        chinesContent = getPdfWithProxies(chUrl)
        engContent = getPdfWithProxies(engUrl)
        languageList = [engContent, chinesContent]

        lastSoup=get_soup(engUrl)

        try:
            volumeYear=currentSoup.find("div",class_="slideBox_nr").find("a").text.strip().split()

            try:
                Volume = re.sub(r'[^0-9]+','',volumeYear[1])
            except:
                print("Failed to find volume")
                Volume = ""
            try:
                Issue = volumeYear[-2]
            except:
                print("Failed to find issue")
                Issue = ""
            try:
                Year = re.sub(r'[^0-9]+','',volumeYear[-1])
            except:
                print("Failed to find year")
                Year = ""
            Month=""
            Day=""

        except:
            print("Failed to find volume, issue, year and other details")
            Volume,Issue,Year,Month,Day="","","","",""

        All_articles=lastSoup.find("div",class_="article_list_tool_bar_container").findAll("div",class_="article_list")

        Total_count=len(All_articles)
        print(f"Total number of articles:{Total_count}","\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_count = article_index+1
            Article_link, Article_title = None, None
            try:
                Article_title=All_articles[article_index].find("div",class_="article_list_title").find("a").text.strip()
                Article_link="http://lyspkj.ijournal.cn/"+All_articles[article_index].find("div",class_="article_list_title").find("a").get("href")
                try:
                    Page_range=re.sub(r'\s+'," ",All_articles[article_index].find("div",class_="article_list_time").text.strip()).split(":")[-1].rstrip(".")
                except:
                    print("Failed to find page range")
                    Page_range = ""

                DOI = ""

                pdf_link="http://lyspkj.ijournal.cn/"+All_articles[article_index].find("font",class_="pdf_url").find("a").get("href")

                if article_check==0:
                    print(get_ordinal_suffix(Article_count) + " article details have been scraped")
                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print(get_ordinal_suffix(Article_count)+" article is duplicated article" +"\n"+"Article title:", Article_title,"📚"+ '\n')

                else:
                    print("Wait until the PDF is downloaded")

                    # output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    # download_pdf(pdf_link, output_fimeName)

                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    pdf_content = requests.get(pdf_link,headers=headers).content
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)

                    print(get_ordinal_suffix(Article_count) + " PDF file has been successfully downloaded")

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
                if article_check < 1:
                    article_check += 1
                else:
                    message = f"{Article_link} : {str(error)}"
                    print(get_ordinal_suffix(Article_count)+" article could not be downloaded due to an error"+"\n"+"Article title:", Article_title,"❌"+ '\n')
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