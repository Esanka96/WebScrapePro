import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import common_function
import pandas as pd
import id_915617128
import id_911675177


def month_check(month):
    Month_list = ['spring', 'fall', 'autumn', 'autumne', 'winter', 'augusto', 'avril', 'juin', 'junio', 'marzo',
                  'oktober', 'summer', 'dezember', 'abril', 'mayo', 'mars', 'décembre', 'septembre','dece','janvier',
                  'février','octobre','novembre','enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                      'septiembre', 'setiembre', 'octubre', 'noviembre', 'diciembre']

    if month in Month_list:
        month_mapping = {
            'spring': 'March', 'fall': 'September', 'autumn': 'September', 'autumne': 'September', 'winter': 'December',
            'augusto': 'August', 'avril': 'April','novembre': 'November',
            'juin': 'June', 'junio': 'June', 'marzo': 'March', 'oktober': 'October', 'summer': 'June',
            'dezember': 'December','janvier': 'January','février': 'February','octobre': 'October',
            'abril': 'April', 'mayo': 'May', 'mars': 'March', 'décembre': 'December', 'septembre': 'September','dece': 'December',
            'enero': 'January', 'febrero': 'February', 'julio': 'July',
            'agosto': 'August', 'septiembre': 'September', 'setiembre': 'September',
            'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
        }
        return month_mapping.get(month)
    else:
        return month

def get_soup(url):
    response = requests.get(url,timeout=10000,headers=headers)
    soup= BeautifulSoup(response.content, 'html.parser')
    return soup

def get_volume(Volume_year,url):
    Volume=re.sub(r'[^0-9]','',re.search(r'Vol. (.*?) Núm', Volume_year).group(1)) if not url=="https://recyt.fecyt.es/index.php/IHE/issue/archive" \
        else re.sub(r'[^0-9]','',re.search(r'Vol. (.*?) núm', Volume_year).group(1))
    Year=re.search(r' \((.*?)\)', Volume_year).group(1)
    if "," in Year:
        Month=month_check(Year.split(",")[0].lower())
        Year=Year.split(",")[1].strip()
    else:
        Month=""
    Issue=re.sub(r'[^0-9]','',re.search(r'Núm. (.*?) \(', Volume_year).group(1)) if not url=="https://recyt.fecyt.es/index.php/IHE/issue/archive" \
        else re.sub(r'[^0-9]','',re.search(r'núm. (.*?) \(', Volume_year).group(1))
    return Volume,Year,Issue,Month

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
        duplicate_list = []
        error_list = []
        completed_list = []
        data = []
        attachment = None

        url,url_id=url_list[url_index].split(',')
        if url=="https://recyt.fecyt.es/index.php/pixel/issue/archive":
            id_915617128.specific_url(url,url_id,url_check)
        elif url=="https://recyt.fecyt.es/index.php/AEDIP/issue/archive":
            id_911675177.specific_url(url,url_id,url_check)
        else:
            current_datetime = datetime.now()
            current_date = str(current_datetime.date())
            current_time = current_datetime.strftime("%H:%M:%S")

            if url_check == 0:
                print(url_id)
                ini_path = os.path.join(os.getcwd(), "Info.ini")
                Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
                current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
                out_excel_file = common_function.output_excel_name(current_out)

            Ref_value = "84"

            pdf_count = 1
            url_value=url.split('/')[-3]

            current_soup=get_soup(get_soup(url).find('ul',class_='issues_archive').find('li').find('a',class_='title').get('href'))

            Article_names=get_soup(f"https://recyt.fecyt.es/index.php/{url_value}/user/setLocale/en_US?source=%2Findex.php%2F{url_value}%2Fissue%2Fview%2F"
                  +get_soup(url).find('ul',class_='issues_archive').find('li').find('a',class_='title').get('href').split("/")[-1])

            All_article_titles = [sin_li for sin_ul in Article_names.find('div', class_='sections').findAll('ul',
                                                                                                     class_='cmp_article_list articles')
                            for sin_li in sin_ul.findAll('div', class_='obj_article_summary')]

            Volume_year = current_soup.find('div', class_='page page_issue').find('h1').text.strip().split(':')[0].split()
            if len(Volume_year)>3:
                Volume,Year,Issue,Month=get_volume(current_soup.find('div', class_='page page_issue').find('h1').text.strip().split(':')[0],url)
            else:
                if Volume_year[0]=="Núm.":
                    Volume,Issue="",re.sub(r'[^0-9]','',Volume_year[1])
                else:
                    Volume,Issue=re.sub(r'[^0-9]','',Volume_year[1]),""
                Year = re.sub(r'[^0-9]', '', Volume_year[2])
                Month=""
            All_articles = [sin_li for sin_ul in current_soup.find('div', class_='sections').findAll('ul',class_='cmp_article_list articles') for sin_li in sin_ul.findAll('div',class_='obj_article_summary')]

            Total_count = len(All_articles)

            article_index, article_check = 0, 0
            while article_index < len(All_articles):
                Article_link, Article_title = None, None
                try:
                    Article_link = All_articles[article_index].find('a').get('href')
                    Article_title=re.sub(r'\s+',' ',All_article_titles[article_index].find('h3',class_='title').text.strip())
                    if "«" or "»" in Article_title:
                        Article_title = Article_title.replace("«", "").replace("»", "")

                    try:
                        Page_range=All_articles[article_index].find('div',class_='pages').text.strip()
                    except:
                        Page_range = ""

                    Article_details=get_soup(Article_link)

                    try:
                        DOI=Article_details.find('section',class_='item doi').find('span').text.strip().rsplit('org/',1)[-1] if Article_details.find('section',class_='item doi') else ""
                    except:
                        DOI = ""

                    if url=='https://recyt.fecyt.es/index.php/JSHR/issue/archive':
                        pdf_link=Article_details.find('a',class_='obj_galley_link pdf').get('href')
                    else:
                        pdf_link=get_soup(Article_details.find('a',class_='obj_galley_link pdf').get('href')).find('a',class_='download').get('href')

                    check_value, tpa_id = common_function.check_duplicate(DOI, Article_title, url_id, Volume, Issue)
                    if Check_duplicate.lower() == "true" and check_value:
                        message = f"{Article_link} - duplicate record with TPAID : {tpa_id}"
                        duplicate_list.append(message)
                        print("Duplicate Article :", Article_title)

                    else:
                        pdf_content = requests.get(pdf_link, timeout=10000,headers=headers).content
                        output_fimeName = os.path.join(current_out, f"{pdf_count}.pdf")
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
                        print("Original Article :", Article_title)

                    if not Article_link in read_content:
                        with open('completed.txt', 'a', encoding='utf-8') as write_file:
                            write_file.write(Article_link + '\n')

                    article_index, article_check = article_index + 1, 0

                except Exception as error:
                    if article_check < 20:
                        article_check += 1
                    else:
                        message = f"Error link - {Article_link} : {str(error)}"
                        print("Download failed :", Article_title)
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
                    # common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                    #                                 len(completed_list), url_id, Ref_value, attachment, current_out)
            except Exception as error:
                message = f"Failed to send email : {str(error)}"
                common_function.email_body_html(current_date, current_time, duplicate_list, error_list, completed_list,
                                                len(completed_list), url_id, Ref_value, attachment, current_out)
                error_list.append(message)

            sts_file_path = os.path.join(current_out, 'Completed.sts')
            with open(sts_file_path, 'w') as sts_file:
                pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 10:
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




