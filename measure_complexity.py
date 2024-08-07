
import time
import sys
import sqlite3
from datetime import datetime
from browsermobproxy import Server
import json
from selenium import webdriver
from selenium.common import exceptions


server = Server("/Users/zitrusdrop/master_thesis/browsermob-proxy-2.1.4/bin/browsermob-proxy")
#server.start()
proxy = server.create_proxy()
proxy = server.create_proxy(params={"trustAllServers": "true"})


# Example for Firefox :
#options = webdriver.firefox.options.Options()
#options.add_argument(f'--proxy-server={proxy.proxy}')
#driver = webdriver.Firefox(options=options)


#options.add_argument("--proxy-server={}".format(proxy.proxy))

options = webdriver.chrome.options.Options()
options.add_argument("--ignore-certificate-errors")
options.add_argument(f'--proxy-server={proxy.proxy}')
driver = webdriver.Chrome(options=options)

#domain = "stackoverflow.com"
#domain = "google.com"
#website = "https://" + domain

# connect to database 
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()

# get url 
# check that there is data in the database 
#cursor.execute("SELECT _id, dns FROM websites LIMIT 1000")
cursor.execute("SELECT _id, dns FROM websites WHERE _id > 62 LIMIT 928")

for row in cursor:
    print(row)
    domain = row[1]
    website = "https://www." + domain
    try:
        proxy.new_har(website, options={'capturecaptureContent': True})
        driver.get(website)
        time.sleep(2)
        with open("/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/har_files/"+domain, 'w') as f:
            result = json.dump(proxy.har, f)
    except exceptions.WebDriverException:
        # in case domain does not provide a website 
        print("exception: " + website)
        proxy.har # not sure if needed to reset 
        # TODO Delete domain in database?


    #proxy.new_har(domain)
    

#print(f'ID: {id}, DNS Name {dns}')

# split to get domain for saving harfile 


#domain = "test.de"
#website = "https://www." + domain


    #print(website)
#proxy.new_har("google")
#driver.get("http://www.google.com")
#proxy.har # returns a HAR JSON blob
#proxy.new_har(website, options={'capturecaptureContent': True})
#driver.get(website)
#time.sleep(2)
#proxy.har # returns a HAR JSON blob
#proxy.har
#with open("/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/har_files/"+domain, 'w') as f:
#    result = json.dump(proxy.har, f)
#server.stop()
driver.quit()



# avoid initial redirects
#TODO query every website one time and if redirected update url in database 




db.close()