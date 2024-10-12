import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
#from selenium.webdriver.chrome.options import Options as chromeOptions
import sys
import sqlite3
from datetime import datetime
import os

# retrieve input params
try:
    # argv[0] is the name of the calling script
    dnsproxy_address = sys.argv[1]
    proxy_pid = int(sys.argv[2])
    protocol = sys.argv[3]
    used_dns_server = sys.argv[4]
except IndexError:
    print("Input params incomplete (dns proxy adddress, dnsproxy PID")
    sys.exit(1)

# connect to database 
db = sqlite3.connect('web-performance2.db')
cursor = db.cursor()
insert_cursor = db.cursor() # otherwise the other will get deleted


# avoid initial redirects
#TODO query every website one time and if redirected update url in database 


# get pages cursor from database 
cursor.execute("SELECT _id, dns FROM websites LIMIT 1000")
#cursor.execute("SELECT _id, dns FROM websites WHERE id > 1 LIMIT 999")


# performance elements to extract
measurement_elements = (
    'protocol', 'server', 'domain', 'timestamp', 'connectEnd', 'connectStart', 'domComplete',
    'domContentLoadedEventEnd', 'domContentLoadedEventStart', 'domInteractive', 'domainLookupEnd', 'domainLookupStart',
    'duration', 'encodedBodySize', 'decodedBodySize', 'transferSize', 'fetchStart', 'loadEventEnd', 'loadEventStart',
    'requestStart', 'responseEnd', 'responseStart', 'secureConnectionStart', 'startTime', 'firstPaint',
    'firstContentfulPaint', 'nextHopProtocol', 'cacheWarming', 'error', 'redirectStart', 'redirectEnd', 'redirectCount')

script = """
            // Get performance and paint entries
            var perfEntries = performance.getEntriesByType("navigation");
            var paintEntries = performance.getEntriesByType("paint");
    
            var entry = perfEntries[0];
            var fpEntry = paintEntries[0];
            var fcpEntry = paintEntries[1];
    
            // Get the JSON and first paint + first contentful paint
            var resultJson = entry.toJSON();
            resultJson.firstPaint = 0;
            resultJson.firstContentfulPaint = 0;
            try {
                for (var i=0; i<paintEntries.length; i++) {
                    var pJson = paintEntries[i].toJSON();
                    if (pJson.name == 'first-paint') {
                        resultJson.firstPaint = pJson.startTime;
                    } else if (pJson.name == 'first-contentful-paint') {
                        resultJson.firstContentfulPaint = pJson.startTime;
                    }
                }
            } catch(e) {}
            
            return resultJson;
            """

# Chrome options
#chrome_options = chromeOptions()
#print(chrome_options)
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-dev-shm-usage')
# TODO Set DNS settings via Selenium or 
#local_state = {
#    "dns_over_https.mode": "secure",
#   "dns_over_https.templates": "https://dns.google/dns-query{?dns}",
    #"dns_over_https.templates": "https://chrome.cloudflare-dns.com/dns-query", # TODO put local dns server here
    #"dns_over_https.templates": dnsproxy_address
 #   "dns_over_https.templates": "https://127.0.0.1"
#}
#chrome_options.add_experimental_option('localState', local_state)

options = webdriver.firefox.options.Options()
options.add_argument("-headless")
options.add_argument('--no-sandbox')
options.set_preference('network.trr.mode', 3) # use only the provided resolver, see https://wiki.mozilla.org/Trusted_Recursive_Resolver
#options.set_preference('network.trr.uri', 'https://127.0.0.1')
options.set_preference('network.trr.uri', 'https://'+dnsproxy_address)
# if not working set manually exception for the used certificate in firefox 

firefox_profile = FirefoxProfile()
firefox_profile.set_preference("javascript.enabled", True)
options.profile = firefox_profile

# options.timeouts = { 'pageLoad': 5000, 'script': 5000 } # default 300k and 30k 
#driver.install_addon(addon_path_xpi) TODO might be insteresting 

def perform_page_load(page, cache_warming=0):
    #driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Firefox(options=options)
    timestamp = int(datetime.now().timestamp()) # timestamp in seconds 
    #print(timestamp)
    try:
        driver.set_page_load_timeout(10)
        driver.get(f'https://{page}')
        performance_metrics =  driver.execute_script(script)
        #print("-------PERFORMANCE--------")
        #print(performance_metrics)
        #print("-------PERFORMANCE ENDE--------")
        insert_performance(page, performance_metrics, timestamp, cache_warming=cache_warming)
        pl_status = 0
    except selenium.common.exceptions.WebDriverException as e:
        print("exception")
        insert_performance(page, {k: 0 for k in measurement_elements}, timestamp, cache_warming=cache_warming, error=str(e))
        pl_status = -1
    
    driver.quit()

    # send restart signal to dnsProxy after loading the page
   # os.system("sudo kill -SIGUSR1 %d" % proxy_pid)
    time.sleep(0.5)
    return pl_status


def insert_performance(page, performance, timestamp, cache_warming=0, error=''):
    performance['protocol'] = protocol
    performance['server'] = used_dns_server
    performance['domain'] = page
    performance['timestamp'] = timestamp
    performance['cacheWarming'] = cache_warming
    performance['error'] = error


    #print("insert to database")
    # insert into database
    insert_cursor.execute(f"""
    INSERT INTO measurements ({','.join([e for e in measurement_elements])}) VALUES ({(len(measurement_elements) - 1) * '?,'}?);
    """, tuple([performance[m_e] for m_e in measurement_elements]))
    #print("executed")
    db.commit()
    #print("committed")


for row in cursor:
    # cache warming
    print(f'{row[1]}: cache warming')
    status = perform_page_load(row[1], 1)
    #print("done")
    if status == 0:
        # performance measurement if cache warming succeeded
        #print(f'{row[1]}: measuring')
        perform_page_load(row[1])

db.close()