import re
import requests
from bs4 import BeautifulSoup
import time
import os
import shutil
from datetime import datetime
import common_function
import pandas as pd
import json

import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
#chromedriver.install()

ini_path = os.path.join(os.getcwd(), "Info.ini")
Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
temPdfOut = common_function.return_current_outfolder(Download_Path, user_id, "932188600")

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--user-agent=YOUR_USER_AGENT_STRING')
options.add_argument('--version_main=108')

prefs = {
    "download.default_directory": os.path.abspath(temPdfOut),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option('prefs', prefs)

driver = uc.Chrome(options=options)

def print_bordered_message(message):
    border_length = len(message) + 4
    border = "-" * (border_length - 2)

    print(f"+{border}+")
    print(f"| {message} |")
    print(f"+{border}+")

def get_soup(url):
    response = requests.get(url,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

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

def specific_url(url,url_id,url_check):
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())
    current_time = current_datetime.strftime("%H:%M:%S")

    if url_check == 0:
        print_bordered_message("Scraping procedure will continue for ID:"+url_id)
        ini_path = os.path.join(os.getcwd(), "Info.ini")
        Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
        current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
        out_excel_file = common_function.output_excel_name(current_out)

    Ref_value = "12"

    duplicate_list = []
    error_list = []
    completed_list=[]
    data = []
    pdf_count = 1

    Mainsoup=get_driver_content(url)
    Volume_issue=Mainsoup.find('ul',class_='journal-issue__vol').findAll('li')
    Volume=re.sub(r'[^0-9]+',"",Volume_issue[0].text.strip())
    Issue = re.sub(r'[^0-9]+', "", Volume_issue[1].text.strip())
    Year_Month=Volume_issue[-1].text.strip().split()
    Year=Year_Month[-1]
    Month=datetime.strptime(Year_Month[0], '%b').strftime('%B')

    All_articles = get_driver_content(url).find('div', class_='toc__body').findAll('div',class_='card')

    Total_count = len(All_articles)
    print(f"Total number of articles:{Total_count}", "\n")

    article_index, article_check = 0, 0
    while article_index < len(All_articles):
        Article_link,Article_title=None,None
        try:
            Article_title = All_articles[article_index].find('h3', class_='article-title').text.strip()
            Article_link = 'https://www.science.org' + All_articles[article_index].find('h3',class_='article-title').find('a').get('href')
            Article_details = get_driver_content(Article_link)
            DOI = Article_details.find('div', class_='doi').text.strip().split('DOI: ')[-1] if Article_details.find('div', class_='doi') else ""
            pdf_link=f"https://www.science.org/doi/pdf/{DOI}?download=true"

            check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
            if Check_duplicate.lower() == "true" and check_value:
                message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                duplicate_list.append(message)
                print("Duplicate Article :", Article_title,"\n")

            else:
                output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                get_driver_pdf(pdf_link, output_fimeName, temPdfOut)
                data.append(
                    {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                     "Identifier": "",
                     "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                     "Special Issue": "", "Page Range": "", "Month": Month, "Day": "",
                     "Year": Year,
                     "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                df = pd.DataFrame(data)
                df.to_excel(out_excel_file, index=False)
                pdf_count += 1
                scrape_message = f"{Article_link}"
                completed_list.append(scrape_message)
                print("Original Article :", Article_title,"\n")

            if not Article_link in read_content:
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
        common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                        str(len(duplicate_list)),
                                        str(len(error_list)))
    except Exception as error:
        message = str(error)
        error_list.append(message)

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
    Error_message = "Error in the \"urlDetails.txt\" file :" + str(error)
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
        url,url_id=url_list[url_index].split(',')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        Mainsoup=get_soup(url)

        if url=="https://www.science.org/toc/scirobotics/current":
            specific_url(url,url_id,url_check)
        else:
            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            if url_check == 0:
                print_bordered_message("Scraping procedure will continue for ID:"+url_id)
                ini_path = os.path.join(os.getcwd(), "Info.ini")
                Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
                current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
                out_excel_file = common_function.output_excel_name(current_out)

            Ref_value = "12"

            duplicate_list = []
            error_list = []
            completed_list=[]
            data = []
            pdf_count = 1
            url_value=url.split('/')[-1]

            try:
                Article_url = 'https://spj.science.org' + Mainsoup.find('div', class_='main-menu align-items-center').find('ul').findAll('li')[2].find('div',class_='dropdown-menu').find('a').get('href')
                All_articles = get_soup(Article_url).find('div', class_='toc__section').findAll('div',
                                                                                                class_='border-bottom')
            except:
                Mainsoup = get_driver_content(url)
                Article_url = 'https://spj.science.org' + \
                              Mainsoup.find('div', class_='main-menu align-items-center').find('ul').findAll('li')[
                                  2].find('div', class_='dropdown-menu').find('a').get('href')

                All_articles = get_driver_content(Article_url).find('div', class_='toc__section').findAll('div', class_='border-bottom')

            Total_count = len(All_articles)
            print(f"Total number of articles:{Total_count}", "\n")

            article_index, article_check = 0, 0
            while article_index < len(All_articles):
                Article_link,Article_title=None,None
                try:
                    Article_title = All_articles[article_index].find('h3', class_='article-title text-deep-gray').text.strip()
                    Article_link = 'https://spj.science.org' + All_articles[article_index].find('h3',class_='article-title text-deep-gray').find('a').get('href')
                    Volume = re.sub(r'[^0-9]+', '',
                                    All_articles[article_index].findAll('ul', class_='list-inline align-middle')[1].find('li').text)
                    try:
                        Article_details = get_soup(Article_link)
                        Article_ID = Article_details.find('div', class_='core-elocator').find('span').text
                    except:
                        Article_details = get_driver_content(Article_link)
                        Article_ID = Article_details.find('div', class_='core-elocator').find('span').text

                    try:
                        DOI = Article_details.find('div', class_='doi').text.strip().split('DOI: ')[-1]
                    except:
                        print("Failed to find doi")
                        DOI = ""

                    try:
                        epdf_link = 'https://spj.science.org/doi/reader/metadata/' + DOI
                        Month_Year_details = json.loads(get_soup(epdf_link).text.strip()).get("itemInfo", {}).get(
                            "metadata", {})
                        if Month_Year_details != {}:
                            Month_year = re.search(r'</span></span></a>(.*?)</span></div></div>',
                                                   Month_Year_details).group(1).split()
                            Year = Month_year[-1]
                            Month = datetime.strptime(Month_year[0], '%b').strftime('%B')
                        else:
                            Year = ""
                            Month = ""
                    except:
                        try:
                            epdf_link = 'https://spj.science.org/doi/epdf/' + DOI
                            Month_Year_details =get_driver_content(epdf_link).find("div",class_='details-entry issue-pub-date').find("span",class_="details-value").text.split()
                            Year=Month_Year_details[-1]
                            Month=datetime.strptime(Month_Year_details[0], '%b').strftime('%B')
                        except:
                            Year=""
                            Month=""

                    pdf_link = f"https://spj.science.org/doi/pdf/10.34133/{url_value}.{All_articles[article_index].find('div', class_='card-actions d-flex').find('a').get('href').split(url_value+'.')[-1]}?download=true"
                    Issue=""
                    check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", Article_title,"\n")

                    else:
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                        get_driver_pdf(pdf_link, output_fimeName, temPdfOut)
                        data.append(
                            {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                             "Identifier": Article_ID,
                             "Volume": Volume, "Issue": "", "Supplement": "", "Part": "",
                             "Special Issue": "", "Page Range": "", "Month": Month, "Day": "",
                             "Year": Year,
                             "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                        df = pd.DataFrame(data)
                        df.to_excel(out_excel_file, index=False)
                        pdf_count += 1
                        scrape_message = f"{Article_link}"
                        completed_list.append(scrape_message)
                        print("Original Article :", Article_title,"\n")

                    if not Article_link in read_content:
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
                common_function.sendCountAsPost(url_id, Ref_value, str(Total_count), str(len(completed_list)),
                                                str(len(duplicate_list)),
                                                str(len(error_list)))
            except Exception as error:
                message = str(error)
                error_list.append(message)

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
        print_bordered_message("Scraping has been successfully completed for ID:"+url_id)
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

shutil.rmtree(temPdfOut)
driver.quit()





