import sys
from atlassian import Jira
from atlassian import Confluence
import xml.etree.ElementTree as ET
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser
from os.path import expanduser
from HTMLTable import (
  HTMLTable,
)

CLIENT_NUMBERS_FOR_ONE_RELEASE = 3
# VMX library licese duration is 180 days
LICENSE_DURATION = 180
#LICENSE_DURATION = 30
# Apply library 15 days in advance
APPLY_TIME_IN_ADVANCE = 15

USER = ""
PASSWORD = ""
EMAIL = ""

def get_args():
    from argparse import ArgumentParser
    global USER
    global PASSWORD
    global EMAIL
    home = expanduser("~")
    try:
        path = home + '/.vmx_user.ini'
        config = configparser.ConfigParser()
        config.read(path)
        USER = config['DEFAULT']['user']
        PASSWORD = config['DEFAULT']['pwd']
        EMAIL = config['DEFAULT']['email']
        #print("User:%s, Password:%s, email:%s" %(USER, PASSWORD, EMAIL))
    except:
        print("Please check ~/.vmx_user.ini")
        sys.exit(1)


    parser = ArgumentParser()
    parser.add_argument('--in', required = True, dest = 'inf', \
            help = 'input release history based XML format')
    return parser.parse_args()

def email_notify(mail_message):
    # print(mail_message)
    mail_server = "mail-sh.amlogic.com"
    receivers = ['jiangfei.han@amlogic.com', 'pengfei.liu@amlogic.com', 'zhihui.zhang@amlogic.com', 'yahui.han@amlogic.com', 'shenghui.geng@amlogic.com', 'yanting.zhou@amlogic.com', 'peifu.jiang@amlogic.com', 'gaojie.song@amlogic.com', 'Vladimir.Maksovic@amlogic.com']

    message = MIMEText(mail_message, 'html', 'utf-8')
    message['From'] = Header("Verimatrix Developer Group", 'utf-8')
    message['To'] = ", ".join(receivers)
     
    subject = 'Verimatrix E2E Library Expiration Reminder'
    message['Subject'] = Header(subject, 'utf-8')
     
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_server, 465)    # SMTP port 465
        smtpObj.login(USER, PASSWORD)  
        smtpObj.sendmail(EMAIL, receivers, message.as_string())
        print("Email notify success")
    except smtplib.SMTPException:
        print("Email notify failed")

def process_release_history(release, table):
    tree = ET.parse(release)
    root = tree.getroot()

    list_message = """
    """
    notify = 0
    rows = 0
    merge_row = 1
    for item in root.findall('items'):
        soc = item.find('soc').text
        eco_system = item.find('eco_system').text
        tracking_number = item.find('tracking_number').text
        release_date = item.find('release_date').text
        print("SoC:%s, Ecosystem:%s, release_date:%s" %(soc, eco_system, release_date))
        for client in item.findall('clients'):
            cl_number = client.find('cl_number').text
            type = client.find('type').text
            note = client.find('note').text
            print("\tcl_number:%s, type:%s" %(cl_number, type))
            table.append_data_rows((
            (tracking_number, soc, eco_system, release_date, cl_number, type, note),
            ))
            rows += 1

        if rows != 0 and rows % CLIENT_NUMBERS_FOR_ONE_RELEASE == 0:
            print("rows:%d" %(rows))
            # Merged the table
            table[merge_row][0].attr.rowspan = CLIENT_NUMBERS_FOR_ONE_RELEASE
            table[merge_row][1].attr.rowspan = CLIENT_NUMBERS_FOR_ONE_RELEASE
            table[merge_row][2].attr.rowspan = CLIENT_NUMBERS_FOR_ONE_RELEASE
            table[merge_row][3].attr.rowspan = CLIENT_NUMBERS_FOR_ONE_RELEASE
            merge_row += CLIENT_NUMBERS_FOR_ONE_RELEASE


        date_format = '%Y-%m-%d'
        date_obj = datetime.strptime(release_date, date_format).date()
        expiration_date = date_obj + relativedelta(days=LICENSE_DURATION)
        apply_date = date_obj + relativedelta(days=(LICENSE_DURATION - APPLY_TIME_IN_ADVANCE))
        now = date.today()

        if now >= apply_date:
            print('--------------------------------------------------------------------------------------->')
            print('The E2E library will expire in two weeks, please apply!')
            print('expiration date:', expiration_date)
            print('now:', now)
            print('dur:', now - date_obj)
            print("Tracking Number:%s, SoC:%s, Ecosystem:%s, release_date:%s" %(tracking_number, soc, eco_system, release_date))
            print("\tcl_number:%s, type:%s, note:%s" %(cl_number, type, note))
            print('---------------------------------------------------------------------------------------$')
            # Highlight the expiring libraries
            table[merge_row-CLIENT_NUMBERS_FOR_ONE_RELEASE][3].set_style({
                'background-color': '#ff0000',
            })
            infos = """
            <ul>
            <li>Tracking Number: {tracking_number}
            <ul>
            <li>SoC: {soc}</li>
            <li>Ecosystem: {eco_system}</li>
            <li>Release_date: <span style="color: #ff0000; background-color: #ffff00;">{release_date}</span></li>
            <li>Expiration date: <span style="color: #ff0000; background-color: #ffff00;">{expiration_date}</span></li>
            </ul>
            </li>
            </ul>
            """.format(tracking_number = tracking_number, soc=soc, eco_system=eco_system, release_date = release_date, expiration_date = expiration_date)

            list_message = list_message + infos
            notify = 1
    if notify == 1:
        mail_message = """
        <p>Hello Jiangfei,</p>
        <p>The following Verimatrix E2E libraries will expire in 15 days, please apply the new libraries.</p>
        {list_message}
        <p><span style="color: #000000;">For more details, please refer to confluence: https://confluence.amlogic.com/display/SW/VMX+E2E+Library+Release+History</span></p>
        <p>Thanks,</p>
        <p>Verimatrix Developer Group</p>
        """.format(list_message = list_message)
        email_notify(mail_message)


if __name__ == "__main__":
    space = "SW"
    page_title = "VMX E2E Library Release History"

    args = get_args()
    
    confluence = Confluence(url="https://confluence.amlogic.com", username=USER, password=PASSWORD)
    page_id = confluence.get_page_id(space, page_title)
    content = confluence.export_page(page_id)
    
    #Save Page
    #with open(page_title + ".pdf", "wb") as pdf_file:
    #    pdf_file.write(content)
    #    pdf_file.close()

    table = HTMLTable(caption='')
    table.append_header_rows((
        ('Tracking Number',  'SoC',  'Ecosystem', 'Release Date', 'CL Number', 'Type', 'Note'),
    ))

    process_release_history(args.inf, table)
    html = table.to_html()
    # print(html)
    confluence.update_page(  
        page_id,
        page_title,
        html)
    print("Completed")
