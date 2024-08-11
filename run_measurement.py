import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chromeOptions
import sys
import sqlite3
from datetime import datetime
import os

# retrieve input params
try:
    dnsproxy_address = sys.argv[0]
    proxy_pid = int(sys.argv[1])
    protocol = sys.argv[2]
    used_dns_server = sys.argv[3]
except IndexError:
    print("Input params incomplete (dns proxy adddress, dnsproxy PID")
    sys.exit(1)


# connect to database 
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()


# avoid initial redirects
#TODO query every website one time and if redirected update url in database 


# get pages cursor from database 
cursor.execute("SELECT _id, dns FROM websites LIMIT 10")


# performance elements to extract
measurement_elements = (
    'id', 'protocol', 'server', 'domain', 'vantagePoint', 'timestamp', 'connectEnd', 'connectStart', 'domComplete',
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
chrome_options = chromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
# TODO Set DNS settings via Selenium or 
local_state = {
    "dns_over_https.mode": "secure",
#   "dns_over_https.templates": "https://dns.google/dns-query{?dns}",
    "dns_over_https.templates": "https://chrome.cloudflare-dns.com/dns-query", # TODO put local dns server here
}
chrome_options.add_experimental_option('localState', local_state)

def perform_page_load(page, cache_warming=0):
    driver = webdriver.Chrome(options=chrome_options)
    timestamp = datetime.now()
    try:
        driver.set_page_load_timeout(10)
        driver.get(f'https://{page}')
        performance_metrics =  driver.execute_script(script)
        insert_performance(page, performance_metrics, timestamp, cache_warming=cache_warming)
        pl_status = 0
    except selenium.common.exceptions.WebDriverException as e:
        insert_performance(page, {k: 0 for k in measurement_elements}, timestamp, cache_warming=cache_warming,
                           error=str(e))
        pl_status = -1
    
    driver.quit()

    # send restart signal to dnsProxy after loading the page
    os.system("sudo kill -SIGUSR1 %d" % proxy_pid)
    time.sleep(0.5)
    return pl_status


def insert_performance(page, performance, timestamp, cache_warming=0, error=''):
    performance['protocol'] = protocol
    performance['server'] = used_dns_server
    performance['domain'] = page
    performance['timestamp'] = timestamp
    performance['cacheWarming'] = cache_warming
    performance['error'] = error

    # insert into database
    cursor.execute(f"""
    INSERT INTO measurements VALUES ({(len(measurement_elements) - 1) * '?,'}?);
    """, tuple([performance[m_e] for m_e in measurement_elements]))
    db.commit()


for row in cursor:
    # cache warming
    print(f'{row[1]}: cache warming')
    status = perform_page_load(row[1], 1)
    if status == 0:
        # performance measurement if cache warming succeeded
        print(f'{row[1]}: measuring')
        perform_page_load(row[1])

db.close()