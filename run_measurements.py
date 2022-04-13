import re
import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.chrome.options import Options as chromeOptions
import sys
from tranco import Tranco
import sqlite3
from datetime import datetime
import hashlib
import uuid
import os

dnsproxy_dir = "/home/ubuntu/dnsproxy/"
# download top list

# t = Tranco(cache=True, cache_dir='.tranco')
# tranco_list = t.list(date='2022-02-24')
# pages = tranco_list.top(13)
# avoid initial redirects (not necessary for twitter)
# pages = [f'www.{page}' for page in pages]
# pages[pages.index('www.twitter.com')] = 'twitter.com'
# pages.remove('www.qq.com')

# just manually get pages list so the domain does not need to be resolved each time
pages = ['www.google.com', 'www.netflix.com', 'www.youtube.com', 'www.facebook.com', 'www.microsoft.com', 'twitter.com',
         'www.instagram.com', 'www.baidu.com', 'www.linkedin.com', 'www.apple.com', 'www.wikipedia.org',
         'www.amazon.com']

# performance elements to extract
measurement_elements = (
    'id', 'protocol', 'server', 'domain', 'vantagePoint', 'timestamp', 'connectEnd', 'connectStart', 'domComplete',
    'domContentLoadedEventEnd', 'domContentLoadedEventStart', 'domInteractive', 'domainLookupEnd', 'domainLookupStart',
    'duration', 'encodedBodySize', 'decodedBodySize', 'transferSize', 'fetchStart', 'loadEventEnd', 'loadEventStart',
    'requestStart', 'responseEnd', 'responseStart', 'secureConnectionStart', 'startTime', 'firstPaint',
    'firstContentfulPaint', 'nextHopProtocol', 'cacheWarming', 'error', 'redirectStart', 'redirectEnd', 'redirectCount')

# create db
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()

# retrieve input params
try:
    protocol = sys.argv[1]
    server = sys.argv[2]
    proxyPID = int(sys.argv[3])
except IndexError:
    print("Input params incomplete (protocol, server, dnsproxyPID) - set dnsproxyPID to 0 if you don't use dnsproxy")
    sys.exit(1)

if len(sys.argv) > 4:
    browser = sys.argv[4]
else:
    browser = 'firefox'

if len(sys.argv) > 5:
    vp_dict = {'compute-1': 'US East', 'ap-northeast-3': 'Asia Pacific Northeast', 'af-south-1': 'Africa South',
               'eu-central-1': 'Europe Central', 'ap-southeast-2': 'Asia Pacific Southeast', 'us-west-1': 'US West',
               'sa-east-1': 'South America East'}
    vantage_point = vp_dict.get(sys.argv[5], '')
else:
    vantage_point = ''

# Chrome options
chrome_options = chromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
# Firefox options
firefox_options = firefoxOptions()
firefox_options.add_argument('--headless')


def create_driver():
    if browser == 'chrome':
        return webdriver.Chrome(options=chrome_options)
    else:
        return webdriver.Firefox(options=firefox_options)


def get_page_performance_metrics(driver, page):
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
    try:
        driver.set_page_load_timeout(10)
        driver.get(f'https://{page}')
        return driver.execute_script(script)
    except selenium.common.exceptions.WebDriverException as e:
        return {'error': str(e)}


def perform_page_load(page, cache_warming=0):
    driver = create_driver()
    timestamp = datetime.now()
    performance_metrics = get_page_performance_metrics(driver, page)
    driver.quit()
    # insert page into database
    if 'error' not in performance_metrics:
        insert_performance(page, performance_metrics, timestamp, cache_warming=cache_warming)
        pl_status = 0
    else:
        insert_performance(page, {k: 0 for k in measurement_elements}, timestamp, cache_warming=cache_warming,
                           error=performance_metrics['error'])
        pl_status = -1
    # send restart signal to dnsProxy after loading the page
    if proxyPID != 0:
        os.system("sudo kill -SIGUSR1 %d" % proxyPID)
        time.sleep(0.5)
    return pl_status



def create_measurements_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id string,
            protocol string,
            server string,
            domain string,
            vantagePoint string,
            timestamp datetime,
            connectEnd integer,
            connectStart integer,
            domComplete integer,
            domContentLoadedEventEnd integer,
            domContentLoadedEventStart integer,
            domInteractive integer,
            domainLookupEnd integer,
            domainLookupStart integer,
            duration integer,
            encodedBodySize integer,
            decodedBodySize integer,
            transferSize integer,
            fetchStart integer,
            loadEventEnd integer,
            loadEventStart integer,
            requestStart integer,
            responseEnd integer,
            responseStart integer,
            secureConnectionStart integer,
            startTime integer,
            firstPaint integer,
            firstContentfulPaint integer,
            nextHopProtocol string,
            cacheWarming integer,
            error string,
            redirectStart integer,
            redirectEnd integer,
            redirectCount integer,
            PRIMARY KEY (id)
        );
        """)
    db.commit()


def create_lookups_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS lookups (
                measurement_id string,
                domain string,
                elapsed numeric,
                status string,
                answer string,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            );
            """)
    db.commit()


def create_qlogs_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS qlogs (
                measurement_id string,
                qlog string,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            );
            """)
    db.commit()


def insert_performance(page, performance, timestamp, cache_warming=0, error=''):
    performance['protocol'] = protocol
    performance['server'] = server
    performance['domain'] = page
    performance['timestamp'] = timestamp
    performance['cacheWarming'] = cache_warming
    performance['error'] = error
    performance['vantagePoint'] = vantage_point
    # generate unique ID
    sha = hashlib.md5()
    sha_input = ('' + protocol + server + page + str(cache_warming) + vantage_point + timestamp.strftime("%H:%d"))
    sha.update(sha_input.encode())
    uid = uuid.UUID(sha.hexdigest())
    performance['id'] = str(uid)

    # insert into database
    cursor.execute(f"""
    INSERT INTO measurements VALUES ({(len(measurement_elements) - 1) * '?,'}?);
    """, tuple([performance[m_e] for m_e in measurement_elements]))
    db.commit()

    if protocol == 'quic':
        insert_qlogs(str(uid))
    # insert all domain lookups into second table
    if error == '' and proxyPID != 0:
        insert_lookups(str(uid))


def insert_qlogs(uid):
    with open(f"{dnsproxy_dir}qlogs.txt", "r") as qlogs:
        log = qlogs.read()
        cursor.execute("""
            INSERT INTO qlogs VALUES (?,?);
            """, (uid, log))
        db.commit()
    # remove the qlogs after dumping it into the db
    with open(f"{dnsproxy_dir}qlogs.txt", "w") as qlogs:
        qlogs.write('')


def insert_lookup(uid, domain, elapsed, status, answer):
    cursor.execute("""
    INSERT INTO lookups VALUES (?,?,?,?,?);
    """, (uid, domain, elapsed, status, answer))
    db.commit()


def insert_lookups(uid):
    with open("dnsproxy.log", "r") as logs:
        lines = logs.readlines()
        currently_parsing = ''
        domain = ''
        elapsed = 0.0
        status = ''
        answer = ''

        for line in lines:
            # upon success
            if 'successfully finished exchange' in line:
                if 'tranco-list.eu.' not in line:
                    currently_parsing = 'success'
                    domain = re.search('exchange of ;(.*)IN', line).group(1).rstrip()
                    elapsed = re.search('Elapsed (.*)ms', line)
                    factor = 1.0
                    if elapsed is None:
                        elapsed = re.search('Elapsed (.*)µs', line)
                        factor = 1.0 / 1000.0
                    if elapsed is None:
                        elapsed = re.search('Elapsed (.*)s', line)
                        factor = 1000.0
                    elapsed = float(elapsed.group(1)) * factor
            # upon failure
            elif 'failed to exchange' in line:
                currently_parsing = 'failure'
                domain = re.search('failed to exchange ;(.*)IN', line).group(1).rstrip()
                answer = re.search('Cause: (.*)', line).group(1).rstrip()
                elapsed = re.search('in (.*)ms\\.', line)
                factor = 1.0
                if elapsed is None:
                    elapsed = re.search('in (.*)µs\\.', line)
                    factor = 1.0 / 1000.0
                if elapsed is None:
                    elapsed = re.search('in (.*)s\\.', line)
                    factor = 1000.0
                elapsed = float(elapsed.group(1)) * factor
            elif currently_parsing == '':
                pass
            elif ', status: ' in line:
                status = re.search(', status: (.*),', line).group(1)
                # if failure the parsing stops here, else we wait for the answer section
                if currently_parsing == 'failure':
                    insert_lookup(uid, domain, elapsed, status, answer)
                    currently_parsing = ''
            elif ';; ANSWER SECTION:' in line:
                currently_parsing = 'answer'
                answer = ''
            elif currently_parsing == 'answer':
                # in this case we finished parsing the answer section
                if line.rstrip() == '':
                    insert_lookup(uid, domain, elapsed, status, answer)
                    currently_parsing = ''
                else:
                    answer += ','.join(line.split())
                    answer += '|'
    # remove the log after parsing it
    with open("dnsproxy.log", "w") as logs:
        logs.write('')


create_measurements_table()
create_lookups_table()
create_qlogs_table()
for p in pages:
    # cache warming
    print(f'{p}: cache warming')
    status = perform_page_load(p, 1)
    if status == 0:
        # performance measurement if cache warming succeeded
        print(f'{p}: measuring')
        perform_page_load(p)

db.close()
