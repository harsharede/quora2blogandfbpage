# -*- coding: UTF-8 -*-
from selenium import webdriver
import time,string,os
import json, webbrowser, getopt, os.path, sys
import httplib2
from oauth2client import client
from apiclient.discovery import build
from oauth2client.file import Storage
import facebook

options = webdriver.ChromeOptions()
options.add_argument("Path to your chrome profile") #Path to your chrome profile
driver = webdriver.Chrome(executable_path="Path to chromedriver.exe", chrome_options=options) #Path to chromedriver.exe


def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    resp = graph.get_object('me/accounts')
    page_access_token = None
    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
    graph = facebook.GraphAPI(page_access_token)
    return graph


def post2fb(name, link, caption, description, picture):
    cfg = {
        "page_id": "fb_page_id",
        "access_token": "Access token"
    }
    page_token = 'page access token'
    attach = {
        "name": name,
        "link": link,
        "caption": caption,
        "description": description,
        "picture": picture,
        "page_token": str(page_token)
    }

    api = get_api(cfg)
    msg = ""
    status = api.put_wall_post(msg, attachment=attach)

#Get question from a quora page

driver.get('https://www.quora.com/topic/Python-programming-language-1')
src_updated = driver.page_source
src = ""

while src != src_updated:
    src = src_updated
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)
    src_updated = driver.page_source


html_source = driver.page_source
driver.quit()
html_source = html_source.encode('ascii', 'ignore')
html_source = '"""'+ str(html_source) + '"""'
html_source = html_source.split("question_link", )

questions = []

for i in html_source:
    if "target=" in i:
        i = i.split("target=", )
        i = i[0][7:]
        if "/" == i[1:2]:
            i = i[1:len(i)-2]
            questions.append(i)

#Get answer for each question and formatting.

qandas= {}
fcurans = ''
tempcurans = ''
count = 0
print "getting ans......."
for i in questions:
    count = count+1
    if count < 11:
        fcurans = ''
        curans = ''
        options = webdriver.ChromeOptions()
        options.add_argument("Path to your chrome profile")  # Path to your chrome profile
        driver = webdriver.Chrome(executable_path="path to chromedriver.exe",chrome_options=options)
        questionlink = 'https://www.quora.com/topic/Python-programming-language-1' + i
        print " "
        print "###############################################################################################################################################################################################################################################################################"
        print questionlink
        driver.get(questionlink)
        html_source = driver.page_source
        driver.quit()
        html_source = html_source.encode('ascii', 'ignore')
        html_source = '"""' + str(html_source) + '"""'
        #print "html:",html_source
        curans = html_source
        # print "Formating.........................."
        # print " "
        ansstart = curans.find("ExpandedQText ExpandedAnswer")
        curans = curans[ansstart:]
        curans = curans[curans.find("qtext_para") + len("qtext_para") + 2:]
        curans = curans[:curans.find("ContentFooter AnswerFooter") - 40]
        question = i[1:]
        qandas[question]= curans
        print curans
        post_count = curans.count("qtext_image_wrapper")
        print "Images count:",str(curans.count("qtext_image_wrapper"))
        if curans.count("qtext_image_wrapper") !=0:
            for i in range(curans.count("qtext_image_wrapper")+1):
                tempcurans = curans[:curans.find("qtext_image_wrapper") - 12]
                # print tempcurans
                remaincurans = curans[curans.find("qtext_image_wrapper") + len("qtext_image_wrapper"):]
                remaincurans = remaincurans[remaincurans.find("master_src"):]
                # print remaincurans
                imglink = remaincurans[:remaincurans.find("master_w=")]
                if i < 1:
                    fbpicture = imglink[imglink.find("master_src=")+len("master_src="):]
                    fbpicture = string.replace(fbpicture, '"','')
                print fbpicture
                imglink = string.replace(imglink, 'master_src=', '<img src=')

                # print imglink
                remaincurans = remaincurans[remaincurans.find("</div>") + len("</div>"):]
                # print remaincurans
                # print tempcurans
                curans = remaincurans
                fcurans = fcurans + tempcurans + imglink + ">"
        else:
            print "no images found"
            fcurans = curans+'<br><br><br><a href="https://www.quora.com/'+question+'">Source: quora</a>'


        blogId = 1234567890  # Put your blog ID here

        isDraft = False  # Don't change this unless you are prepared to modify the script
        postfile = 'autotest.txt'
        title = 'Default Title'  # Change this to the default title you prefer
        labels ='python, Django, flask' #tags
        # If there is no userkey authenticate with Google and save the key.
        if (os.path.exists('userkey') == False):
            flow = client.flow_from_clientsecrets('client_id.json',
                                                  scope='https://www.googleapis.com/auth/blogger',
                                                  redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                                                  )

            auth_uri = flow.step1_get_authorize_url()
            webbrowser.open_new(auth_uri)
            auth_code = raw_input('Enter the auth code: ')
            credentials = flow.step2_exchange(auth_code)
            http_auth = credentials.authorize(httplib2.Http())

            # Store the credentials
            storage = Storage('userkey')
            storage.put(credentials)

        # If the userkey already exists use it.
        else:
            storage = Storage('userkey')
            credentials = storage.get()
            http_auth = credentials.authorize(httplib2.Http())

        # Initialize the blogger service and get the blog
        blogger_service = build('blogger', 'v3', http=http_auth)


        f = fcurans

        labels_list = labels.split(',')

        # build body object
        body = {
            "content": fcurans,
            "title": question,
            "labels": labels_list
        }

        fpath = "C:\\quora2blogandfbpage\\qandas\\posted.txt"
        with open(fpath, 'r') as f:
            lineArr = f.read().split("`")
            print lineArr

        # Insert the post
        if question not in lineArr:
            post = blogger_service.posts().insert(blogId=blogId, body=body, isDraft=isDraft).execute()
            f = open(fpath, "a+")
            f.write(question + "`")
            f.close

            print("Title: %s" % post['title'])
            print("Is Draft: %s" % isDraft)
            if (isDraft == False):
                print("URL: %s" % post['url'])
            print("Labels: %s" % post['labels'])

            name = post['title']
            link = post['url']
            caption = post['title']
            description = ''
            picture = fbpicture

            if post_count !=0:
                post2fb(name, link, caption, description, picture)
            time.sleep(3600)
        else:
            count = count - 1
            print "Already Posted: ",question

    else:
        sys.exit()

