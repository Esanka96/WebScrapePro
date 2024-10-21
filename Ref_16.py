import os
from datetime import datetime
import common_function
import pandas as pd
import url1
import url2
import url3
import url4

duplicate_list = []
error_list = []
completed_list = []
Total_count=None
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

        if url_check==0:
            print(url_id)
            ini_path = os.path.join(os.getcwd(), "Info.ini")
            Download_Path, Email_Sent, Check_duplicate, user_id = common_function.read_ini_file(ini_path)
            current_out = common_function.return_current_outfolder(Download_Path, user_id, url_id)
            out_excel_file = common_function.output_excel_name(current_out)

        Ref_value = "16"

        duplicate_list = []
        error_list = []
        completed_list=[]
        data = []
        pdf_count = 1

        if url=='https://www.phcogj.com/':
            pdf_count,data,duplicate_list,error_list,completed_list,Total_count=url1.get_url(current_out,out_excel_file,url,url_id,user_id,Download_Path,pdf_count,data,duplicate_list,error_list,completed_list,Check_duplicate)
        elif url=='https://jyoungpharm.org/':
            pdf_count,data,duplicate_list,error_list,completed_list,Total_count=url2.get_url(current_out,out_excel_file,url,url_id,user_id,Download_Path,pdf_count,data,duplicate_list,error_list,completed_list,Check_duplicate)
        elif url=='https://www.sysrevpharm.org/archive.html':
            pdf_count,data,duplicate_list,error_list,completed_list,Total_count=url3.get_url(current_out,out_excel_file,url,url_id,user_id,Download_Path,pdf_count,data,duplicate_list,error_list,completed_list,Check_duplicate)
        elif url=='https://www.jcdronline.org/archive.php':
            pdf_count,data,duplicate_list,error_list,completed_list,Total_count=url4.get_url(current_out,out_excel_file,url,url_id,user_id,Download_Path,pdf_count,data,duplicate_list,error_list,completed_list,Check_duplicate)

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
            error_list.append(message)

        sts_file_path = os.path.join(current_out, 'Completed.sts')
        with open(sts_file_path, 'w') as sts_file:
            pass
        url_index, url_check = url_index + 1, 0
    except Exception as error:
        if url_check < 15:
            url_check += 1
        else:
            Error_message = "Error in the driver :" + str(error)
            print("Error in the driver or site"+"\n")
            error_list.append(Error_message)
            common_function.attachment_for_email(url_id, duplicate_list, error_list, completed_list,
                                                 len(completed_list), ini_path, attachment, current_date,
                                                 current_time, Ref_value)

            url_index, url_check = url_index + 1, 0