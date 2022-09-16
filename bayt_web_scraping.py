from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import pandas as pd




# Entering inputs
country = input("Enter the country : ")
field = input("Enter your field : ")
field = field.replace(' ', '-')
num_pages = input("Enter number of web pages : ")
num_pages = int(num_pages)

# Get headers from browser developper tools
# headers = requests.utils.default_headers()
headers = {'User-Agent':'Mozilla/5.0'}

# Dataframe to stock all jobs information
df = pd.DataFrame()

# Iterate through all pages
for i_page in range(num_pages):
    # Compose URL using inputs
    url = f'https://www.bayt.com/en/{country}/jobs/{field}-jobs/?page={i_page+1}'
    print(url)

    # Fetch url using requests
    request = Request(url, headers=headers)        
    page = urlopen(request).read()

    soup = BeautifulSoup(page, 'lxml')
    # Find job section using <li> tag
    result = soup.find_all('li', {'class': 'has-pointer-d'})

    # Loop over job section elements
    for element in result:
        # Get job title from <a> tag
        job_title = element.find('a').text
        job_title = job_title.replace('\n', '').replace('\t', '')

        # Get company name from <b> tag
        company_name = element.find('b', {'class': 'jb-company'}).text.replace('\n', '').replace('\t', '')
        # Get publication date
        publish_date = element.find('div', {'class': 'jb-date col p0x t-xsmall t-mute'}).text.replace('\n', '').replace('\t', '')
        # Get job location
        location = element.find('span', {'class': 'jb-loc t-mute t-nowrap'}).text
        # We need job id for more information about the job
        job_id = element.find('h2', {'class': 'jb-title m0 t-large'}).find('a').get('data-job-id')
        # Add job id to url
        url_job = url + f'?jobId={job_id}'
        request_job = Request(url, headers=headers)   
        # Collect job specefic information     
        page = urlopen(request_job).read()
        soup_job = BeautifulSoup(page, 'lxml')
        # Get required skills
        job_desc_titles = soup_job.find_all('h2', {'class': 'h6 p10t'})
        i_desc = 0
        i_skill = -1
        i_detail = -1

        # Find skills and details elements
        while (i_desc < len(job_desc_titles)):
            if job_desc_titles[i_desc].text == 'Skills':
                i_skill = i_desc
            if job_desc_titles[i_desc].text == 'Job Details':
                i_detail = i_desc
            i_desc += 1
        # List of skills  
        if i_skill > -1:
            skills_tag = job_desc_titles[i_skill]
            # li_list = skills_tag.find_n('ul').find_all('li')
            li_list = skills_tag.find_next_siblings(['p', 'ul'])
            skills_list = [li.text.replace('\xa0\xa0\xa0\xa0', '') for li in li_list]
            # print(skills_list)
        else:
            skills_list = []

        # Get job details
        if i_detail > -1:
            job_details = job_desc_titles[i_detail]
            # Get job type (remote, full/part time)
            job_type = job_details.find_all_next('dd')[4].text
            # Get monthly salary
            salary = job_details.find_all_next('dd')[5].text
        else:
            job_type, salary = '', ''

        # Add information to Dataframe using dictionary
        dict = {
            'Job ID': job_id,
            'Job Title': job_title,
            'Company Name': company_name,
            'Publication Date': publish_date,
            'Location': location,
            'URL': url_job,
            'Job Type': job_type,
            'Salary': salary,
            'Skills': skills_list
            }
        new_row = pd.DataFrame([dict])
        df = pd.concat([df, new_row])

# Set Dataframe index to Job ID
df.set_index('Job ID', inplace=True)
# print(df)

# Save Dataframe to a file
# df.to_json(path_or_buf=f'{field}AT{country}.json', orient='records')
df.to_csv(f'{field}AT{country}.csv')

