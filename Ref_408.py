import re
from bs4 import BeautifulSoup
import requests
import time
import os
import shutil
from datetime import datetime
import common_function
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
chromedriver.install()

ini_path = os.path.join(os.getcwd(), "Info.ini")
Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
temPdfOut = common_function.return_temp_outfolder(Download_Path, user_id, "Temp_Ref_408(At the end of the process, the folder will be automatically deleted)")

def get_driver_content(url):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    return soup

def get_driver_pdf(url, new_filename, download_path):
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))

    driver.get(url)
    print("Wait until the PDF is downloaded")
    time.sleep(5)

    while any(f.endswith('.crdownload') for f in os.listdir(download_path)):
        time.sleep(1)

    pdf_files = [f for f in os.listdir(download_path) if f.endswith(".pdf")]

    downloaded_file = os.path.join(download_path, pdf_files[0])
    shutil.move(downloaded_file, new_filename)
    print("PDF file has been successfully downloaded")

def login_with_uc():
    url = 'https://www.ajronline.org/'
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    login_link = "https://www.ajronline.org" + soup.find("a", class_="loginBar__username")["href"]
    driver.get(login_link)

    username_input = driver.find_element(By.ID,'ctl01_TemplateBody_WebPartManager1_gwpciNewContactSignInCommon_ciNewContactSignInCommon_signInUserName')
    username_input.send_keys('EB732976')

    password_input = driver.find_element(By.ID,'ctl01_TemplateBody_WebPartManager1_gwpciNewContactSignInCommon_ciNewContactSignInCommon_signInPassword')
    password_input.send_keys('732976')

    sign_in_button = driver.find_element(By.ID,'ctl01_TemplateBody_WebPartManager1_gwpciNewContactSignInCommon_ciNewContactSignInCommon_SubmitButton')
    sign_in_button.click()

    current_url = None
    while current_url != "https://www.ajronline.org/":
        current_url = driver.current_url
        time.sleep(1)

    currentUrl = "https://www.ajronline.org/toc/ajr/current"
    driver.get(currentUrl)
    content = driver.page_source
    currentSoup = BeautifulSoup(content, 'html.parser')
    return currentSoup

duplicate_list = []
error_list = []
completed_list = []
attachment=None
url_id=None
current_date=None
current_time=None
Ref_value="408"
ini_path=None
current_out=None

check = 0
while check < 5:
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--version_main=108')

        prefs = {
            "download.default_directory": os.path.abspath(temPdfOut),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }

        options.add_experimental_option('prefs', prefs)

        driver = uc.Chrome(options=options)
        check = 5
    except:
        if not check < 4:
            Error_message = "Error in the Chrome driver. Please update your Google Chrome version."
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
        check += 1

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,da;q=0.8',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Priority': 'u=0, i',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

try:
    with open('urlDetails.txt','r',encoding='utf-8') as file:
        url_list=file.read().split('\n')
except Exception as error:
    Error_message = "Error in the \"urlDetails.txt\" file :" + str(error)
    print(Error_message)
    error_list.append(Error_message)
    common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                         len(completed_list),
                                         ini_path, attachment, current_date, current_time, Ref_value)
    # common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list, len(completed_list),
    #                                      ini_path, attachment, current_date, current_time, Ref_value,current_out)

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
        url,url_id=url_list[url_index].split(',')
        data = []
        duplicate_list = []
        error_list = []
        completed_list = []
        pdf_count=1

        current_datetime = datetime.now()
        current_date = str(current_datetime.date())
        current_time = current_datetime.strftime("%H:%M:%S")

        if url_check==0:
            print("\n"+url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value="408"

        currentSoup= login_with_uc()

        try:
            issueYear=currentSoup.find("div",class_="current-issue__specifics").get_text(strip=True)
            Volume,Issue,Month,Year=re.search(r"Volume (\d+)Issue (\d+)(\w+) (\d{4})",issueYear).groups()
        except:
            Volume,Issue,Month,Year="","","",""

        All_articles=list(filter(lambda x:x.find("i",class_="icon-PDF inline-icon"),currentSoup.find('div',class_='table-of-content').findAll('div',class_='titled_issues')))

        Total_count = len(All_articles)
        print(f"Total number of articles:{Total_count}", "\n")

        article_index, article_check = 0, 0
        while article_index < len(All_articles):
            Article_link,Article_title=None,None
            try:
                Article_link='https://www.ajronline.org' + All_articles[article_index].find('h3',class_='issue-item__title').find('a').get('href')
                Article_title = All_articles[article_index].find('h3',class_='issue-item__title').text.strip()

                try:
                    DOI=All_articles[article_index].find('div',class_='issue-item__doi').a.text.strip().split("org/")[-1]
                except:
                    DOI=""

                pdf_link = f"https://www.ajronline.org/doi/pdf/{DOI}?download=true"

                check_value,tpa_id = common_function.check_duplicate(DOI,Article_title, url_id, Volume, Issue)
                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title+ '\n')
                else:
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    get_driver_pdf(pdf_link, output_fimeName, temPdfOut)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": "", "Month": Month, "Day": "", "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')
                    print("Original Article :", Article_title+ '\n')

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0

            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message=f"Error link - {Article_link} : {str(error)}"
                    print("Download failed :",Article_title+ '\n')
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

        try:
            common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)), str(len(duplicate_list)),
                            str(len(error_list)))
        except Exception as error:
            print(f"Failed to send post request : {str(error)}")
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
            print(f"Failed to send email : {str(error)}")
            message=f"Failed to send email : {str(error)}"
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the driver or site:" + str(error)
            print("Error in the driver or site")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            # common_function.email_body_html(current_date,current_time,duplicate_list,error_list,completed_list,len(completed_list),
            #                                 url_id,Ref_value,attachment,current_out)

            url_index, url_check = url_index + 1, 0

shutil.rmtree(temPdfOut)
driver.close()
driver.quit()




