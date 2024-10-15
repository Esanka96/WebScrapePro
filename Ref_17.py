import time

import requests
from bs4 import BeautifulSoup
import os
import re
import common_function
from datetime import datetime
import pandas as pd
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
import random

chromedriver.install()

def first_drive(url,request_cookies):
    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def use_drive(url,request_cookies):
    driver.get(url)
    for cookie_name, cookie_value in request_cookies.items():
        driver.add_cookie({"name": cookie_name, "value": cookie_value})

    driver.get(url)
    content = driver.page_source
    uc_soup = BeautifulSoup(content, 'html.parser')
    return uc_soup

def get_pdf_link(pdf_link):
    driver.get(pdf_link)
    time.sleep(2)
    for i in range(30):
        current_url = driver.current_url
        if current_url != pdf_link:
            return current_url
        time.sleep(1)

request_cookies={
    'GeoScienceWorldMachineID': '638475566012738969',
    'fpestid': 'f6tdgLTO5-uu-D79o3BwgcCJ8LIF5rYe6uzYtjoq9QujxAeEBDCLFb5WQ0DZ1DA7wo7mWA',
    '_ga': 'GA1.1.1487530923.1711959819',
    '_gid': 'GA1.3.569889817.1711959819',
    '_cc_id': '23c309b2b916c241c5354943d7a590ab',
    'panoramaId_expiry': '1712564622863',
    'panoramaId': '0a62239d6889f74214825d16dbaf185ca02cf678ef814ebd2813a55b670875f8',
    'panoramaIdType': 'panoDevice',
    '_hjSessionUser_2619384': 'eyJpZCI6ImM4ZTc4YjNmLTIzYmItNTkyMi1iZDcwLWY5YzFmNWMyMzQyZSIsImNyZWF0ZWQiOjE3MTE5NTk4MjU0NzYsImV4aXN0aW5nIjp0cnVlfQ==',
    'hubspotutk': '31fbd733f95a4abb67792c123cf2d8b4',
    'GDPR_24_.geoscienceworld.org': 'true',
    'TheDonBot': 'D47BD6096350C06E91E5E85FFD4A95DF',
    'GSW_SessionId': 'gyjp0c2zr4to30bzz5irddko',
    '_gat_UA-28112735-4': '1',
    '_gat_UA-28112735-1': '1',
    '_gat_UA-50143594-1': '1',
    '_gat_UA-28112735-5': '1',
    '_gat_UA-76340245-2': '1',
    '_gat_UA-1008571-9': '1',
    '_gat_UA-1008571-10': '1',
    '_gat_UA-1008571-11': '1',
    '_gat_UA-1008571-12': '1',
    '_gat_UA-1008571-15': '1',
    '_gat_UA-1008571-16': '1',
    '_gat_UA-1008571-17': '1',
    '_gat_UA-1008571-18': '1',
    '_ga_YVB7JQBY6Z': 'GS1.1.1711999347.5.0.1711999347.0.0.0',
    '_hjSession_2619384': 'eyJpZCI6IjNmMWM2NWVkLTY4OTEtNDliOS1hNDFhLTVkYTNkNGI5M2Q0NyIsImMiOjE3MTE5OTkzNDc5MDEsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=',
    '_ga_11RK1D9N56': 'GS1.3.1711999348.5.0.1711999348.0.0.0',
    '_ga_MKZCHDYBTN': 'GS1.3.1711999348.5.0.1711999348.0.0.0',
    '_ga_781B8JFM4R': 'GS1.3.1711999348.5.0.1711999348.0.0.0',
    '_ga_KZ8XM8M5S3': 'GS1.3.1711999348.5.0.1711999348.0.0.0',
    '_ga_5FBFHZKYCW': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '_ga_YY6XD0X474': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '_ga_RBDZFVMYBJ': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '_ga_LK2NSTY4C0': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '_ga_2ZJXB7SCK6': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '_ga_HP48M3E3R7': 'GS1.3.1711999349.5.0.1711999349.0.0.0',
    '__hstc': '147277928.31fbd733f95a4abb67792c123cf2d8b4.1711959837613.1711973459982.1711999352182.5',
    '__hssrc': '1',
    '__hssc': '147277928.1.1711999352182'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value="17"
ini_path=None

check = 0
while check < 10:
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={user_agent}')

        driver = uc.Chrome(options=options)

        check = 10
    except:
        if not check < 9:
            message = "Error in the Chrome driver. Please update your Google Chrome version."
            error_list.append(message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        check += 1

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the urlDetails text file :" + str(error)
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

p, q = 0, 0
while p < len(url_list):
    try:
        url,url_id=url_list[p].split(',')

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        Ref_value = "17"

        if q == 0:
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)
            print(url_id)

        data = []
        duplicate_list = []
        error_list = []
        completed_list=[]
        pdf_count=1
        attachment = None

        try:
            soup = first_drive(url,request_cookies)
            Volume = re.sub(r'[^0-9]+', "", soup.find('span', class_='volume issue').text.strip().split(',')[0])
        except:
            soup = use_drive(url,request_cookies)
            Volume = re.sub(r'[^0-9]+', "", soup.find('span', class_='volume issue').text.strip().split(',')[0])

        Issue = re.sub(r'[^0-9]+', "", soup.find('span', class_='volume issue').text.strip().split(',')[1])
        # Month,Year = soup.find('div', class_='ii-pub-date').text.strip().split(' ')
        All_articles = soup.find('div',class_='section-container').findAll('div', class_='al-article-item-wrap al-normal')

        Total_count = len(All_articles)

        i, j = 0, 0
        while i < len(All_articles):
            Article_link,Article_title=None,None
            try:
                Article_title = All_articles[i].find('h5', class_='item-title').find('a').text.strip()
                Article_link = "https://pubs.geoscienceworld.org" + All_articles[i].find('h5', class_='item-title').find('a').get('href')

                try:
                    Article_details = first_drive("https://pubs.geoscienceworld.org" + All_articles[i].find('h5', class_='item-title').find('a').get('href'),request_cookies)
                except:
                    Article_details = use_drive(
                        "https://pubs.geoscienceworld.org" + All_articles[i].find('h5', class_='item-title').find(
                            'a').get('href'), request_cookies)

                try:
                    try:
                        Page_range = Article_details.find('div', class_='ww-citation-primary').get_text(strip=True).split()[-1].rstrip(".")
                    except:
                        Page_range=""
                    try:
                        DOI = Article_details.find('div', class_='citation-doi').get_text(strip=True).rsplit('doi.org/', 1)[-1]
                    except:
                        DOI=""
                except:
                    Page_range,DOI="",""

                pdf_link_check=Article_details.find('ul',class_='debug js-toolbar toolbar')
                pdf_link='https://pubs.geoscienceworld.org'+pdf_link_check.find('li', class_='item-pdf').find('a').get('href')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)
                else:
                    updatedLink=get_pdf_link(pdf_link)
                    pdf_content = requests.get(updatedLink, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "", "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": "", "Day": "", "Year": "",
                         "URL": Article_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                i, j = i + 1, 0
            except Exception as error:
                if j < 5:
                    j += 1
                else:
                    message=f"{Article_link} : 'NoneType' object has no attribute 'text'"
                    print("Download failed :",Article_title)
                    error_list.append(message)
                    i, j = i + 1, 0

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
        p, q = p + 1, 0
    except Exception as error:
        if q < 5:
            q += 1
        else:
            Error_message = "Error in the driver :" + str(error)
            print("Error in the driver or site")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            p, q = p + 1, 0

driver.close()
driver.quit()









