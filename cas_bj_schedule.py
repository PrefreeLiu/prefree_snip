import cas_bj_jira
import schedule
import time

def jira_job():
    cas_bj_jira.process_jira()

schedule.every().saturday.at("23:40").do(jira_job)
schedule.every().saturday.at("23:45").do(jira_job)

while True:
    schedule.run_pending()
    time.sleep(1)
