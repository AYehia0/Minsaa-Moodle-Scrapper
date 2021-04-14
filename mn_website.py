import re
import json
import os
import time
import requests
from bs4 import BeautifulSoup

login_url = "https://menofia.education/login/index.php"
course_url_index = "https://menofia.education/course/view.php?id="
scraped_data = {}

def download_data(data_type, content_url, session):

    dir = data_type

    if not os.path.exists(dir):
        os.mkdir(dir)

    s = session.get(content_url)
    path = f"{dir}/{s.url.split('/')[-1]}"

    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(s.content)

def get_content(content_url, session):
    
    dir = content_url.split('/')[4] 
    
    # a pdf 
    if dir == 'resource':
        # just download
        download_data(dir, content_url, session)

    # a quiz
    if dir == 'quiz':

        request_html = session.get(content_url).text 
        soup = BeautifulSoup(request_html, 'html.parser')

        main = soup.find('div' , {'role':'main'})

        #getting quiz info
        quiz_info = main.find('div', class_='quizinfo').text

        #getting quiz img
        quiz_img = main.find('img')['src']
        print(quiz_img)

        # Saving the img
        download_data(dir, quiz_img, session)

    if dir == 'assign' :
        pass


user_name = os.environ.get('SSID')
password = os.environ.get('PASS')

s = requests.Session()

page = s.get(login_url)

pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
token = re.findall(pattern, page.text)
token = re.findall("\w{32}", token[0])

cookie = page.cookies.get_dict()

data = {
    'username' : user_name,
    'password' : password,
    'anchor' : "",
    'logintoken' : token[0]
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}

time.sleep(1)

resp = s.post(login_url, data=data, headers=headers)

soup = BeautifulSoup(resp.text, 'lxml')

courses = soup.find('div', class_='courses frontpage-course-list-enrolled')

course_urls = [] 

for course in courses.find_all('div', class_='card'):
    course_urls.append(f"{course_url_index}{course['data-courseid']}")


for subject in course_urls:

    subject_content = []
    first_id = s.get(subject)

    soup2 = BeautifulSoup(first_id.text, 'html.parser')

    try:
        topic = soup2.find('ul', class_='topics')
        all_topics = topic.find_all('a', class_='aalink')

        for content in all_topics:
            content_url = content['href']

            #downloading
            get_content(content_url, s)
            subject_content.append(content_url)

        #adding data
        scraped_data[subject] = subject_content
    
    except:
        print("No contents yet")



print(scraped_data)
