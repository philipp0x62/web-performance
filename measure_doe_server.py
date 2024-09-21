import os
import sqlite3
import json
import pandas as pd
import re
import pymongo
from bson.json_util import loads


f = open('/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/doeQueries/doeQueries.ipv6.doq.json')
#dns_data = loads(f.read())

print("data loaded", dns_data)

quit()



# connect to database 
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()

# read all files in har_files (should only be har files) 
files = os.listdir('doeQueries/')

# ignore hidden files e.g. .DS_Store under MacOS
files = [f for f in files if f.endswith('.json')]



for file in files:
    print("open file ", file)
#    mimeTypes = {} # contains the different mimeTypes as keys, there count of occurences, there accumulated header and body sizes
#    queried_servers = set()
#    non_origin_servers = set()
#    print('processing: ', file)
    with open('doeQueries/' + file) as f:
#f = open('/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/doeQueries/doeQueries.ipv6.doh.json')
        dns_data = json.load(f)
        print("data loaded", file)
    #data_df = pd.read_json('doeQueries/' + file, lines=True)
    #print(data_df)
#f.close()
# ObjectId\('.*'\)
#datetime.datetime\(
#000),
#data_df = pd.read_json('/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/test.json')
#print(data_df)


#"query.doequery.dnsquery.host"
#"query.doequery.dnsquery.port"
#"query.uri"
#"query.httpversion"
#"query.method"
#"query.doequery.dnsquery.sni"

