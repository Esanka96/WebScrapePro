import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import common_function
import pandas as pd
import undetected_chromedriver as uc
import chromedriver_autoinstaller as chromedriver
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

request_cookies = {
    'Allen_PressMachineID': '638639838630405808',
    '_gcl_au': '1.1.474727157.1728387067',
    'fpestid': 'ftkT9BVrq_LD4G4xiyDaxoZFJ5I-SX60VKs3ciqF-ilpD2p04rmqU1fvKYnYHFepOADeBA',
    '_cc_id': '48ae4fd426831174cbe1b6d758464d38',
    'panoramaId_expiry': '1728991867742',
    'panoramaId': '6fb61fdb0187a1543f77a90b9d13185ca02c9457c9a2a0dd2cf7784f801d9265',
    'panoramaIdType': 'panoDevice',
    '_gid': 'GA1.2.608788093.1728387068',
    'hubspotutk': 'bd4f16bd8adeb7fe30ad769c9bd6577f',
    'ALLEN_SessionId': 'x3ewicnv4jdk33s1q5ujzyca',
    '__cf_bm': '.K1ag3CCDJg8m6mtAFVjKRDnhUb5BR8OYfHIwOg_I5s-1728405918-1.0.1.1-Q067AvrzLXRDUsZpVLdd3XLVBfsejEx4t2zwAofg0h38geHEAcG2bBIzPfFBOJ5Xo2eDcvOsRmfff8apMowaog',
    '__gads': 'ID=e077b4f3621bb612:T=1728387067:RT=1728405920:S=ALNI_MYZAoLqS1shDXs-q9L7aPqQnNimBg',
    '__gpi': 'UID=00000f3a3cfaa6ba:T=1728387067:RT=1728405920:S=ALNI_MZkFBlG_-OqXqLckN2qxYGH1kWqcA',
    '__eoi': 'ID=8f72760562e88976:T=1728387067:RT=1728405920:S=AA-Afjbk_0tuLaVFyTR3yTs1-D1r',
    'cf_clearance': 'ucsvr0Tm9e669St5kVuNBol0FaWKeiOrMJ0d_yxm1mA-1728405921-1.2.1.1-XSesci50Syf1X0Wsgo4pb4Qld5UC1OlQXAxKhWuWOc3TqTea3SUj.7gPP7hZ2CehluEFd_VtzCRLmZqzlWu..ZkgEBiEM_FzgDLfOHlSTA8LG04TcjhKsZuB1yVSX4IHKPlILvqQbC_oyGxoqDzjChdbTdgsYA4YiEjJD8jIywpGSKK7sI8rh6s7XJmbZBsWQZUnwePUpOwsurtTvYSXAgvpmY99c8psstPTVDHOmtgzy_XEI_kgRjdr26ZjiVlVu2jxzikFXmZDIE2uPjyGalQAYPD6gdpo323hf9Dn6ajXnC2K.Wv7GC52OdAn39z9F4a0HT8VBl31zNdU6xGKEvBPypCbXYHjSofxxIGVzbenbZGwvBCPid74rkLprDH3ppSvFK4Ll_sblLh9qwCWrg',
    '_ga_EMWX2WZGRN': 'GS1.1.1728405921.2.0.1728405921.60.0.0',
    '_ga': 'GA1.2.1202702530.1728387068',
    '__hstc': '82353225.bd4f16bd8adeb7fe30ad769c9bd6577f.1728387070660.1728387070660.1728405923206.2',
    '__hssrc': '1',
    '__hssc': '82353225.1.1728405923206'
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
Ref_value="447"
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
    print(error)

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

        Ref_value = "447"

        if url_check == 0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        attachment = None
        pdf_count = 1
        baseUrl="https://meridian.allenpress.com"

        try:
            current_soup=first_drive(url,request_cookies)
            preVolume,preIssue=current_soup.find('div',class_='volume-issue__wrap').text.strip().split(', ')
        except:
            current_soup=use_drive(url,request_cookies)
            preVolume,preIssue=current_soup.find('div',class_='volume-issue__wrap').text.strip().split(', ')


        Volume=preVolume.split()[1]
        Issue=preIssue.split()[1]
        Day,Month,Year=current_soup.find('div',class_='ii-pub-date').text.strip().split()

        All_articles=current_soup.find('div',class_='section-container').findAll('div',class_='al-article-item-wrap al-normal')

        Total_count = len(All_articles)

        article_index, article_check = 0, 0
        while article_index < len(All_articles):

            Article_link,Article_title=None,None
            try:
                Article_link=baseUrl+All_articles[article_index].find('h5',class_='item-title').find('a').get('href')
                Article_title = All_articles[article_index].find('h5',class_='item-title').text.strip()

                try:
                    Article_details=first_drive(Article_link,request_cookies)
                    pdf_link=baseUrl+Article_details.find('a',class_='article-pdfLink').get('href')
                except:
                    Article_details = use_drive(Article_link, request_cookies)
                    pdf_link = baseUrl + Article_details.find('a',class_='article-pdfLink').get('href')
                DOI = Article_details.find('div', class_='citation-doi').text.strip().rsplit('doi.org/', 1)[-1]
                Page_range = Article_details.find('div', class_='ww-citation-primary').text.strip().rsplit('): ', 1)[-1].rstrip('.')

                check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)

                if Check_duplicate.lower() == "true" and check_value:
                    message = f"{pdf_link} - duplicate record with TPAID : {tpa_id}"
                    duplicate_list.append(message)
                    print("Duplicate Article :", Article_title)

                else:
                    updatedLink=get_pdf_link(pdf_link)
                    pdf_content = requests.get(updatedLink, headers=headers).content
                    output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
                    with open(output_fimeName, 'wb') as file:
                        file.write(pdf_content)
                    data.append(
                        {"Title": Article_title, "DOI": DOI, "Publisher Item Type": "", "ItemID": "",
                         "Identifier": "",
                         "Volume": Volume, "Issue": Issue, "Supplement": "", "Part": "",
                         "Special Issue": "", "Page Range": Page_range, "Month": Month, "Day": Day,
                         "Year": Year,
                         "URL": pdf_link, "SOURCE File Name": f"{pdf_count}.pdf", "user_id": user_id})
                    df = pd.DataFrame(data)
                    df.to_excel(out_excel_file, index=False)
                    pdf_count += 1
                    scrape_message = f"{Article_link}"
                    completed_list.append(scrape_message)
                    print("Original Article :", Article_title)

                if not Article_link in read_content:
                    with open('completed.txt', 'a', encoding='utf-8') as write_file:
                        write_file.write(Article_link + '\n')

                article_index, article_check = article_index + 1, 0
            except Exception as error:
                if article_check < 4:
                    article_check += 1
                else:
                    message=f"{Article_link} : 'NoneType' object has no attribute 'text'"
                    print("Download failed :",Article_title)
                    error_list.append(message)
                    article_index, article_check = article_index + 1, 0

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
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 4:
            url_check += 1
        else:
            Error_message = "Error in the driver :" + str(error)
            print("Error in the driver or site")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list),
                                                 ini_path, attachment, current_date, current_time, Ref_value)
            url_index, url_check = url_index + 1, 0

driver.close()
driver.quit()






