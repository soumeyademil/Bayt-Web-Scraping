from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest
from datetime import date, timedelta
import pandas as pd


country = input("Enter the country : ")
field = input("Enter your field : ")

field = field.replace(' ', '-')
url = f'https://www.bayt.com/en/{country}/jobs/{field}-jobs/'
print(url)

headers = {'User-Agent':'Mozilla/5.0'}

# Fetch url using requests
request = Request(url, headers=headers)        
page = urlopen(request).read()


soup = BeautifulSoup(page, 'lxml')

result = soup.find_all('li', {'class': 'has-pointer-d'})


job_titles = []
today_date = date.today()
df = pd.DataFrame()

for element in result:
    # Get job title from <a> tag
    job_title = element.find('a').text
    # Get company name from <b> tag
    company_name = element.find('b', {'class': 'jb-company'}).text
    # Get publication date
    publish_date = element.find('div', {'class': 'jb-date col p0x t-xsmall t-mute'}).text
    # Get job location
    location = element.find('span', {'class': 'jb-loc t-mute t-nowrap'}).text

    # We need job id to collect more information about the job
    job_id = element.find('h2', {'class': 'jb-title m0 t-large'}).find('a').get('data-job-id')
    # Add job id to url
    url_job = url + f'?jobId={job_id}'
    request_job = Request(url, headers=headers)        
    page = urlopen(request_job).read()
    soup_job = BeautifulSoup(page, 'lxml')
    # Get required skills
    job_desc_titles = soup_job.find_all('h2', {'class': 'h6 p10t'})
    skills_tag = job_desc_titles[0]
    li_list = skills_tag.find_next('ul').find_all('li')
    skills_list = [li.text for li in li_list]
    print(job_desc_titles)
    # Get job type (remote, full/part time)
    job_details = job_desc_titles[1]
    job_type = job_details.find_all_next('dd')[4].text
    # Get monthly salary
    salary = job_details.find_all_next('dd')[5].text
    dict = {
        'Job ID': job_id,
        'Job Title': job_title,
        'Company Name': company_name,
        'Publication Date': publish_date,
        'Location': location,
        'URL': url_job,
        'Job Type': job_type,
        'Salary': salary,
        # 'Skills': skills_list
        }
    new_row = pd.DataFrame([dict])
    df = pd.concat([df, new_row])
    print(df)
    break

