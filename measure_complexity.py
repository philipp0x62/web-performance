import time
import sqlite3
from datetime import datetime
from browsermobproxy import Server
import json
from selenium import webdriver
from selenium.common import exceptions
import sys


# retrieve input params
try:
    # argv[0] is the name of the calling script
    starting_point = int(sys.argv[1])
    interval = int(sys.argv[2])
except IndexError:
    print("Input params incomplete (Starting Point, Interval Length")
    sys.exit(1)

print("Start Point: ", starting_point)



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
options.add_argument("-headless")
options.add_argument('--no-sandbox')
options.add_argument("--ignore-certificate-errors")
options.add_argument("--enable-javascript")
options.add_argument(f'--proxy-server={proxy.proxy}')
options.timeouts = { 'pageLoad': 5000, 'script': 5000 } # default 300k and 30k 
driver = webdriver.Chrome(options=options)

#domain = "stackoverflow.com"
#domain = "google.com"
#website = "https://" + domain

# connect to database 
db = sqlite3.connect('web-performance2.0.db')
cursor = db.cursor()
update_cursor = db.cursor() # cannot use a cursor which is currently used for iterating, therefore second cursor needed

print("starting measurement " + str(time.time()) + "\n==========================")

# get url 
# check that there is data in the database 
#cursor.execute("SELECT _id, dns FROM websites LIMIT 100")
cursor.execute("SELECT _id, dns FROM websites WHERE _id BETWEEN ? AND ?", (starting_point, starting_point+interval-1))

for row in cursor:
    print(row)
    domain = row[1]
    website = "https://www." + domain
    try:
        proxy.new_har(website, options={'capturecaptureContent': True})
        driver.get(website)
        #time.sleep(2)
        with open("/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/har_files/"+domain, 'w') as f:
            result = json.dump(proxy.har, f)
        driver.save_screenshot('screenshots/' + domain + '.png')
        if 'error' or 'Error' in driver.page_source:
            update_cursor.execute("UPDATE websites SET has_error=TRUE WHERE dns=?",(row[0],)) 
            db.commit()
    except exceptions.WebDriverException:
        # in case domain does not provide a website
        print("exception: " + website)
        update_cursor.execute("UPDATE websites SET has_website=FALSE WHERE dns=?",(row[0],))
        db.commit()
        proxy.har # not sure if needed to reset 

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
print("==========================\n" + "completed measurement " + str(time.time()))