from jira import JIRA
import sys
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

def email_notify(mail_message):
    home = expanduser("~")
    try:
        path = home + '/.vmx_user.ini'
        config = configparser.ConfigParser()
        config.read(path)
        USER = config['DEFAULT']['user']
        PASSWORD = config['DEFAULT']['pwd']
        EMAIL = config['DEFAULT']['email']
    except:
        print("Please check ~/.vmx_user.ini")
        sys.exit(1)
    # print(mail_message)
    mail_server = "mail-sh.amlogic.com"
    receivers = ['pengfei.liu@amlogic.com', 'zhongwei.zhao@amlogic.com', 'jiangfei.han@amlogic.com', 'peifu.jiang@amlogic.com']

    message = MIMEText(mail_message, 'html', 'utf-8')
    message['From'] = Header("Security-CAS-Certification Jira", 'utf-8')
    message['To'] = ", ".join(receivers)
     
    subject = 'Security CAS Certification Team Jira Reminder'
    message['Subject'] = Header(subject, 'utf-8')
     
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_server, 465)    # SMTP port 465
        smtpObj.login(USER, PASSWORD)  
        smtpObj.sendmail(EMAIL, receivers, message.as_string())
        print("Email notify success")
    except smtplib.SMTPException:
        print("Email notify failed")
        print("User:%s, Password:%s, email:%s" %(USER, PASSWORD, EMAIL))

def process_jira():
    notify = 0
    auth_jira = JIRA('https://jira.amlogic.com', auth=(USER, PASSWORD))
    mail_info = """
    <p>Hello Guys,</p>
    <h2><span style="color: #ff0000; background-color: #ffff00;"><strong>Please process the following Jira ASAP.</strong></span></h2>
    <table style="border-collapse: collapse; width: 95.9484%; height: 36px;" border="1">
    <tbody>
    <tr style="height: 18px;">
    <td style="width: 16.6667%; height: 18px;">Key</td>
    <td style="width: 16.6667%; height: 18px;">Priority</td>
    <td style="width: 16.6667%; height: 18px;">Assignee</td>
    <td style="width: 16.6667%; height: 18px;">Status</td>
    <td style="width: 16.6667%; height: 18px;">Finish Date</td>
    <td style="width: 16.6667%; height: 18px;">Due Date</td>
    <td style="width: 16.6667%; height: 18px;">Summary</td>
    </tr>
    """
    row_info = """
    init
    """
    #for issue in auth_jira.search_issues('reporter = currentUser() order by created desc', maxResults=3):
    for issue in auth_jira.search_issues('project in (SWPL, "RD Security Project", "OTT projects", "TV Projects") AND status not in (Closed) AND priority in (Highest, High) AND assignee in (pengfei.liu, zhongwei.zhao, jiangfei.han) ORDER BY assignee ASC, priority DESC, cf[10700] DESC'):

        date_format = '%Y-%m-%d'
        if format(issue.fields.customfield_11614) != 'None':
            date_obj = datetime.strptime(format(issue.fields.customfield_11614), date_format).date()
        now = date.today()

        if format(issue.fields.status) == 'OPEN' or format(issue.fields.customfield_11614) == 'None':
            print('{} , {}, {}, {} the status is OPEN'.format(issue.key, issue.fields.assignee, issue.fields.summary, issue.fields.customfield_11614))
            row_info = """
            <tr style="height: 18px;">
            <td style="width: 16.6667%; height: 18px;">{key}</td>
            <td style="width: 16.6667%; height: 18px;">{priority}</td>
            <td style="width: 16.6667%; height: 18px;"><strong><span style="color: #ff0000; background-color: #ffff00;">{assignee}</td>
            """.format(key=format(issue.key), priority=format(issue.fields.priority), assignee=format(issue.fields.assignee))
            if format(issue.fields.status) == 'OPEN':
                row_info += """
                <td style="width: 16.6667%; height: 18px;"><strong><span style="color: #ff0000; background-color: #ffff00;">{status}</td>
                """.format(status=format(issue.fields.status))
            else:
                row_info += """
                <td style="width: 16.6667%; height: 18px;">{status}</td>
                """.format(status=format(issue.fields.status))
            if format(issue.fields.customfield_11614) == 'None':
                row_info += """
                <td style="width: 16.6667%; height: 18px;"><strong><span style="color: #ff0000; background-color: #ffff00;">{finish}</td>
                """.format(finish=format(issue.fields.customfield_11614))
            else:
                row_info += """
                <td style="width: 16.6667%; height: 18px;">{finish}</td>
                """.format(finish=format(issue.fields.customfield_11614))
            
            row_info += """
            <td style="width: 16.6667%; height: 18px;">{due}</td>
            <td style="width: 16.6667%; height: 18px;">{summary}</td>
            </tr>
            """.format(due=format(issue.fields.duedate), summary=format(issue.fields.summary))
            mail_info += row_info
            notify += 1
        elif date_obj <= now:
            row_info = """
            <tr style="height: 18px;">
            <td style="width: 16.6667%; height: 18px;">{key}</td>
            <td style="width: 16.6667%; height: 18px;">{priority}</td>
            <td style="width: 16.6667%; height: 18px;"><strong><span style="color: #ff0000; background-color: #ffff00;">{assignee}</td>
            <td style="width: 16.6667%; height: 18px;">{status}</td>
            <td style="width: 16.6667%; height: 18px;"><strong><span style="color: #ff0000; background-color: #ffff00;">{finish}</td>
            <td style="width: 16.6667%; height: 18px;">{due}</td>
            <td style="width: 16.6667%; height: 18px;">{summary}</td>
            </tr>
            """.format(key=format(issue.key), priority=format(issue.fields.priority), assignee=format(issue.fields.assignee), status=format(issue.fields.status),
                    finish=format(issue.fields.customfield_11614), due=format(issue.fields.duedate), summary=format(issue.fields.summary))
            mail_info += row_info
            notify += 1
        else:
            print('{} , {}, {}, {}, {}, due:{}'.format(issue.key, issue.fields.assignee, issue.fields.summary, issue.fields.customfield_11614, issue.fields.status, issue.fields.duedate))

    mail_info += """
    </tbody>
    </table>
    <p>&nbsp;</p>
    <p>Dashboard: <a href="https://jira.amlogic.com/secure/Dashboard.jspa?selectPageId=14620">Security CAS Certification Team Dashboard Link</a></p>
    <p>&nbsp;</p>
    <p>Thanks,</p>
    <p>Security CAS Certification Team</p>
    """
    print(mail_info)
    if notify > 0:
        email_notify(mail_info)
        notify = 0

if __name__ == "__main__":
    args = get_args()
    process_jira()
