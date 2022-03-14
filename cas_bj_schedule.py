import cas_bj_jira
import schedule
import time

def jira_job():
    cas_bj_jira.process_jira()

schedule.every().monday.at("10:30").do(jira_job)
schedule.every().monday.at("10:55").do(jira_job)

while True:
    schedule.run_pending()
    time.sleep(60)
