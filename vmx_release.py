from email.policy import default
from nis import match
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
from git import Repo

USER = ""
PASSWORD = ""
EMAIL = ""
soc = ['m9x4', 'm9y4']

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
    parser.add_argument('--date', required = True, dest = 'date', \
            help = 'input release date, format: YYYY-MM-DD')
    parser.add_argument('--sdk', required = True, dest = 'sdk', \
            help = 'input sdk version, list: android-r, android-s')
    return parser.parse_args()

class confluence_wrapper(object):
    def __init__(self, space, page_title, user, pwd):
        
        self.page_title = page_title
        self.confluence = Confluence(url="https://confluence.amlogic.com", username=user, password=pwd)
        #print ("space:%s, page_title:%s, user:%s, pwd:%s" %(space, page_title, user, pwd))
        self.page_id = self.confluence.get_page_id(space, page_title)

    def update_page(self, content):
        self.confluence.update_page(  
            self.page_id,
            self.page_title,
            content)
        print("Update Completed")

    def append_page(self, content):
        self.confluence.append_page(  
            self.page_id,
            self.page_title,
            content)
        print("Append Completed")   

if __name__ == '__main__':
    # 1. Get input args
    args = get_args()
    print ("date:%s, sdk:%s" %(args.date, args.sdk))

    # 2. Pull the git of vmx bootloader
    bootloader_repo = Repo("/home/brooks/src/vmx/bootloader")
    bootloader_repo.remotes.origin.fetch()
    bootloader_repo.git.pull()
    print(bootloader_repo.commit('master'))

    # 3. Pull the git of vmx sdk-rel
    sdk_repo = Repo("/home/brooks/src/vmx/sdk-rel")
    sdk_repo.remotes.origin.fetch()
    sdk_repo.git.pull()

    # branches = repo.remote().refs
    # for item in branches:
    #     print(item.remote_head)
    #     print(repo.commit("origin/" + item.remote_head))

    # 4. Init the confluence
    if args.sdk == 'android-r':
        cw = confluence_wrapper("SW", "VMX Android R OTT Release Version", USER, PASSWORD)
    elif args.sdk == 'android-s':
        cw = confluence_wrapper("SW", "VMX Android S OTT Release Version", USER, PASSWORD)
    else:
        print ("wrong sdk: %s" %(args.sdk))
        exit()

    # 5. Push the release date to Confluence
    head1 = '<h1>{date}</h1>'.format(date=args.date)
    cw.append_page(head1)

    # 6. Push the table header to Confluence
    table = HTMLTable(caption='')
    table.append_header_rows((
        ('Git', 'Branch', 'Commit', 'Notes'),
    ))

    # 7. Push VMX bootloader and SDK info to Confluence
    # Note: VMX bootloader git must bind to Android version, VMX sdk-rel git should not bind to Android version
    for i in soc:
        print("soc:%s" %(i))
        branch = i + "/openlinux-" + args.sdk
        table.append_data_rows((
        ('vendor/vmx/bootloader', branch, bootloader_repo.commit("origin/" + branch), "VMX " + i + " family"),
        ))
        branch = i + "-rel"
        table.append_data_rows((
        ('sdk-rel', branch, sdk_repo.commit("origin/" + branch), "VMX " + i + " family"),
        ))
 
    html = table.to_html()
    # print(html)
    cw.append_page(html)

    
    