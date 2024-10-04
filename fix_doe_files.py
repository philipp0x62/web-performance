import re
import json
import psycopg
import pandas as pd
import subprocess


# read all files in har_files (should only be har files) 
# data source: https://port-53.info/data/open-encrypted-dns-servers/
df_doq = pd.read_json('doeQueries/doq-2024-03.json', lines=True)
df_doh = pd.read_json('doeQueries/doh3-2024-03.json', lines=True)


# merge lists 
df_doq['protocol'] ='quic'
df_doh['protocol'] ='h3'
df_resolvers = pd.concat([df_doh, df_doq])

# connect to database for storing information
db = psycopg.connect(dbname='web_performance')
cursor = db.cursor()

# loop over list and discover DoE services
insert_resolver = "INSERT INTO resolvers (host, protocol, port) VALUES (%s, %s, %s);"
insert_resolver_measurement = "INSERT INTO resolver_measurement (resolver_id, protocol, rtt, total_time, round_trips, warm_up, raw_data) VALUES (%s, %s, %s, %s, %s, %s, %s);"
get_resolver_id = "SELECT _id FROM resolvers WHERE host= %s AND protocol= %s"
# q query, time in nanoseconds 
doq_query = "go run . A @quic://?server? google.com --stats --format=json" # DoQ standard port: 853
doh_query = "go run . A @https://?server? --stats --http3 --format=json" # DoH3 standard port 443
dou_query = "go run . A @?server? --stats --format=json" # DoU standard port 53
rtt_query = "ping -c 5 ?server?" # ping via ICMP

for index, resolver in df_resolvers.iterrows():
    #print(index)
    #print("++++++++++")
    #print(resolver['domain'])

    # prepare queries 
    if not resolver['domain']:
        resolver['domain'] = resolver['ip']
    prepared_doq_query = doq_query.replace("?server?", resolver['domain'])
    prepared_doh_query = doh_query.replace("?server?", resolver['domain'])
    prepared_dou_query = dou_query.replace("?server?", resolver['domain'])
    prepared_rtt_query = rtt_query.replace("?server?", resolver['domain'])


    print(prepared_doq_query)
    print("------------------")
    # measure RTT per server 
    rtt_result = subprocess.run(prepared_rtt_query, shell=True, capture_output=True, text=True) 

    # process ping
    min_rtt, avg_rtt, max_rtt, __ =  rtt_result.stdout.split('\n')[-2].split('=')[1].split("/")
    #min_rtt = int(float(min_rtt)*1000)
    avg_rtt = int(float(avg_rtt)*1000) # in microseconds
    #max_rtt = int(float(max_rtt)*1000)
    #print(avg_rtt)

    # discover DNS services
   #doq_result = subprocess.run(prepared_doq_query.split(), shell=True, capture_output=True, text=True, cwd="../q-main").stdout.strip("\n") # using q
    doq_result = subprocess.run(prepared_doq_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
    doh_result = subprocess.run(prepared_doh_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
    dou_result = subprocess.run(prepared_dou_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q

    

    ## Insert results 
    #DoQ
    if doq_result.stdout: 
        raw_data = json.loads(doq_result.stdout)[0]
        round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'quic', 853))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'quic'))
        id = cursor.fetchone()[0]
        print("id: ", id)
        cursor.execute(insert_resolver_measurement, (id, 'quic', avg_rtt, raw_data['time'], round_trips , True, doq_result.stdout))
        db.commit()
    #DoH
    if doh_result.stdout:
        raw_data = json.loads(doh_result.stdout)[0]
        round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'h3', 443))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'h3'))
        id = cursor.fetchone()[0]

        print("id: ", id)
        cursor.execute(insert_resolver_measurement, (id, 'h3', avg_rtt, raw_data['time'], round_trips , True, doh_result.stdout))
        db.commit()
    #DoU
    if dou_result.stdout:
       # print("result:", list(dou_result.stdout), ":")
        print("result: ", bool(list(dou_result.stdout)))
        print("result: ", bool(dou_result.stdout))
       # print("bool representation: ", bool(doq_result.stdout))
       # print(len(doq_result.stdout))
       # print(len(doq_result.stdout.strip()))
       # print(bool(doq_result.stdout == '  '))
        raw_data = json.loads(dou_result.stdout)[0]
        round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'udp', 53))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'udp'))
        id = cursor.fetchone()[0]

        print("id: ", id)
        cursor.execute(insert_resolver_measurement, (id, 'udp', avg_rtt, raw_data['time'], round_trips , True, dou_result.stdout))
        db.commit()


    #print(type(doq_result.stdout))
    #print(".......error......")
    if doq_result.stderr:
        print(type(doq_result.stderr))
    #print("--------DoH-------")
    #print(doh_result.stdout)
    #print(".......error......")
    #print(doh_result.stderr)
    #print("--------DoU-------")
    #print(dou_result.stdout)
    #print(".......error......")
    #print(dou_result.stderr)
    
    #print(doh_result)
    #print("--------DoU-------")
    #print(dou_result)
    break
    #subprocess.run(["q", query]) 

quit()



# calculate round trips for QUIC and H3 (round ) (need to be queried with a warmup query)
# 1 --> 0-RTT supported 
#  2 --> Session resumption supported
# 3 --> without support of above features 




#  --http3
# --stats

# go run . @dns.google.com example.com --stats
# go run . A @quic://dns.adguard-dns.com example.com --all -v  --additional

#"query.doequery.dnsquery.host"
#"query.doequery.dnsquery.port"
#"query.uri"
#"query.httpversion"
#"query.method"
#"query.doequery.dnsquery.sni"




for file in files:
    print("process ", file)
    f = open('/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/doeQueries/doeQueries.ipv6.doh.json',"r+")
    #f = open('doeQueries/' + files[0], "w")
    with open('doeQueries/' + file, "r+") as f:
        content = f.read()
        #content = re.sub('True','true',content)
        #content = re.sub('False','false',content)
        #content = re.sub('None','null',content)
        content = re.sub(r'ObjectId\s*\(\s*\"(\S+)\"\s*\)',
                      r'{"$oid": "\1"}',
                      content)
        content = re.sub(r'Date\s*\(\s*(\S+)\s*\)',
                      r'{"$date": \1}',
                      content)
        #content = re.sub(r'ObjectId\(\'.*\'\)','""',content)
        #content = re.sub(r'datetime.datetime\(',r'"datetime.datetime(',content)
        #content = re.sub(r'000\),',r'000)",',content)
        #content = re.sub("\'",'\"',content)
        #content = re.sub(r'}\n{',r'},{',content)
        #content = re.sub(r': b.\S+', r': "",' ,content)
        f.seek(0)
        f.truncate(0)
        #f.write("["+content+"]")
        f.write(content)

        data = json.loads(content, object_hook=json_util.object_hook)
        print("it worked")
        print(json_util.dumps(data))
        quit()



