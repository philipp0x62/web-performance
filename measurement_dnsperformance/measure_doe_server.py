import re
import json
import psycopg
import pandas as pd
import subprocess


# read all files in har_files (should only be har files) 
# data source: https://port-53.info/data/open-encrypted-dns-servers/
df_doq = pd.read_json('doeQueries/doq-2024-03.json', lines=True)
df_doh = pd.read_json('doeQueries/doh3-2024-03.json', lines=True)
df_doe = pd.read_json('doeQueries/doh3-2024-03.json', lines=True)


# merge lists 
df_doq['protocol'] ='quic'
df_doh['protocol'] ='h3'
df_doe['protocol'] ='unknown'
df_resolvers = pd.concat([df_doh, df_doq, df_doe])

# connect to database for storing information
db = psycopg.connect(dbname='web_performance')
cursor = db.cursor()

# loop over list and discover DoE services
insert_resolver = "INSERT INTO resolvers (host, protocol, port) VALUES (%s, %s, %s);"
insert_resolver_measurement = "INSERT INTO resolver_measurement (resolver_id, protocol, rtt, total_time, round_trips, warm_up, raw_data, session_resumption, rtt0) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
get_resolver_id = "SELECT _id FROM resolvers WHERE host= %s AND protocol= %s"
update_resolver_session_resumption = "UPDATE resolvers SET session_resumption = TRUE WHERE _id = %s"
update_resolver_rtt0 = "UPDATE resolvers SET rtt0 = TRUE WHERE _id = %s"

# q query, time in nanoseconds 
doq_query = "go run . A @quic://?server? google.com --stats --format=json" # DoQ standard port: 853
doh_query = "go run . A @https://?server? --stats --http3 --format=json" # DoH3 standard port 443
doq_query_intermediate = "go run . A @127.0.0.1 google.com --stats --format=json" # DoQ standard port: 853
doh_query_intermediate = "go run . A @127.0.0.2 --stats --format=json" # DoH3 standard port 443
dou_query = "go run . A @?server? --stats --format=json" # DoU standard port 53
rtt_query = "ping -c 3 ?server?" # ping via ICMP

# make resolvers in table unique to speed up the script
df_ip_only = df_resolvers.loc[df_resolvers['domain'] == '']
df_ip_only = df_ip_only.drop_duplicates(subset=['ip'])
#print(df_ip_only)
df_resolvers = df_resolvers.drop_duplicates(subset=['domain'])
df_resolvers = pd.concat([df_resolvers, df_ip_only])

print("number of unique resolvers: ", df_resolvers.shape[0])

for index, resolver in df_resolvers.iterrows():
    #print(index)
    #print("++++++++++")
    #print(resolver['domain'])

    #prepare RouteDNS Instances 


    # prepare queries 
    if not resolver['domain']:
        resolver['domain'] = resolver['ip']
    prepared_doq_query = doq_query.replace("?server?", resolver['domain'])
    prepared_doh_query = doh_query.replace("?server?", resolver['domain'])
    prepared_dou_query = dou_query.replace("?server?", resolver['domain'])
    prepared_rtt_query = rtt_query.replace("?server?", resolver['domain'])


    print(prepared_rtt_query)
    print("--------", index, "----------")
    # measure RTT per server 
    rtt_result = subprocess.run(prepared_rtt_query, shell=True, capture_output=True, text=True) 

    #print("stdout: ", rtt_result.stdout)
    #print("sterr: ", rtt_result.stderr)
    #print("boolean: ", rtt_result.stdout.find("Unknown host") == -1)
    #print(rtt_result.stderr.find("Unknown host"))
    # process ping
    if not (rtt_result.stderr.find("Unknown host") == -1):
        print("host does not exist, skip")
        continue # host does not exist, skip

    # prepare RouteDNS config
    sed_command_doq = "sed 's/address = " + '"domain.com:port"/address = ' + '"' + resolver['domain'] + ':853"/' + "' doq-client-template.toml > doq-client.toml"
    sed_command_doh = "sed 's/address = " + '"domain.com:port"/address = ' + '"' + resolver['domain'] + ':443"/' + "' doh-client-template.toml > doh-client.toml"

    route_dns_doq = subprocess.run(sed_command_doq, shell=True, capture_output=False, cwd="../routedns/cmd/routedns", text=True) 
    route_dns_doh = subprocess.run(sed_command_doh, shell=True, capture_output=False, cwd="../routedns/cmd/routedns", text=True) 

    # start RouteDNS instances
    #route_dns_doq = subprocess.run("nohup go run . doq-client.toml > RouteDNS_DoQ.log & && echo $!", shell=True, capture_output=True, cwd="../routedns/cmd/routedns/example-config", text=True) 
    #route_dns_doh = subprocess.run("nohup go run . doh-client.toml > RouteDNS_DoH3.log & && echo $!", shell=True, capture_output=True, cwd="../routedns/cmd/routedns/example-config", text=True) 
    #route_dns_doq_pid = int(route_dns_doq.stdout)
    #route_dns_doh_pid = int(route_dns_doh.stdout)

    # process ping further
    ping_statistics =  rtt_result.stdout.split('\n')[-2]
    ping_blocked = False
    #print(ping_statistics.find("100.0% packet loss"))
    #print(bool(ping_statistics.find("100.0% packet loss")))
    if(ping_statistics.find("100.0% packet loss") != -1):
        ping_blocked = True
        print("ping blocked")
    else:
        min_rtt, avg_rtt, max_rtt, __ =  ping_statistics.split('=')[1].split("/")
        #min_rtt = int(float(min_rtt)*1000)
        avg_rtt = int(float(avg_rtt)*1000) # in microseconds
        #max_rtt = int(float(max_rtt)*1000)
        #print(avg_rtt)

    # discover DNS services and warm up queries
    support_doq = False
    support_doh = False
    support_dou = False

   #doq_result = subprocess.run(prepared_doq_query.split(), shell=True, capture_output=True, text=True, cwd="../q-main").stdout.strip("\n") # using q
    doq_result = subprocess.run(prepared_doq_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
    doh_result = subprocess.run(prepared_doh_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
    dou_result = subprocess.run(prepared_dou_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q


    ## Insert results 
     #DoU
    dou_blocked = True
    if dou_result.stdout:
        support_dou = True
        raw_data = json.loads(dou_result.stdout)[0]

        dou_blocked = False
        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'udp', 53))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'udp'))
        dou_id = cursor.fetchone()[0]

    #DoQ
    if doq_result.stdout: 
        support_doq = True
        raw_data = json.loads(doq_result.stdout)[0]

        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'quic', 853))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'quic'))
        doq_id = cursor.fetchone()[0]
        #print("id: ", id)

    #DoH
    if doh_result.stdout:
        support_doh = True
        raw_data = json.loads(doh_result.stdout)[0]

        try:
            cursor.execute(insert_resolver, (resolver['domain'], 'h3', 443))
            db.commit()
        except psycopg.errors.UniqueViolation as e: # ignore duplicates in data sources
            db.rollback()

        cursor.execute(get_resolver_id, (resolver['domain'], 'h3'))
        doh_id = cursor.fetchone()[0]
        #print("id: ", id)
   
    # do the measurements and feature discovery
   
    # DoU
    if support_dou:
        # run same query again to have a fair comparison of the run times
        dou_result = subprocess.run(prepared_dou_query, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
        raw_data = json.loads(dou_result.stdout)[0]
        
        if ping_blocked: # DoU completes request in one RTT --> use as alternative 
            round_trips = 1
            avg_rtt = raw_data['time']/1000
        else:
            round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        print("DoU round trips: ", round_trips)

        cursor.execute(insert_resolver_measurement, (dou_id, 'udp', avg_rtt, raw_data['time'], round_trips , False, dou_result.stdout, False, False))
        db.commit()

   # DoQ
    if support_doq:
        # send to queries to the intermediate
        doq_result = subprocess.run(doq_query_intermediate, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
        raw_data = json.loads(doq_result.stdout)[0]

        if ping_blocked and dou_blocked:
            print("RTT measurement blocked")
            round_trips = -1
            avg_rtt = -1
        else:
            round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        print("DoQ round trips: ", round_trips)

        cursor.execute(insert_resolver_measurement, (doq_id, 'quic', avg_rtt, raw_data['time'], round_trips , True, doq_result.stdout, False, False))
        db.commit()

        # do second measurement to find support for session resumption and 0-RTT
        doq_result = subprocess.run(doq_query_intermediate, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
        raw_data_second = json.loads(doq_result.stdout)[0]

        if ping_blocked and dou_blocked:
            print("RTT measurement blocked")
            round_trips = -1
            avg_rtt = -1
        else:
            round_trips = round(int(int(raw_data_second['time']/1000))/avg_rtt)
        print("DoQ round trips: ", round_trips)

        session_resumption = False
        rtt0 = False

        if(round(raw_data['time'] / raw_data_second['time']) <= 3):
            # session resumption and 0-RTT are supported
            session_resumption = True
            rtt0 = True
            cursor.execute(update_resolver_session_resumption, (doq_id,))
            cursor.execute(update_resolver_rtt0, (doq_id,))
            db.commit()
        elif (round(raw_data['time'] / raw_data_second['time']) == 2):
            # session resumption is supported but not 0-RTT
            session_resumption = True
            cursor.execute(update_resolver_session_resumption, (doq_id,))
            db.commit()
        
        # else session resumption and 0-RTT are not supported, initial values are correct
        cursor.execute(insert_resolver_measurement, (doq_id, 'quic', avg_rtt, raw_data['time'], round_trips , False, doq_result.stdout, session_resumption, rtt0))
        db.commit()

   # DoH  
    if support_doh:
        doh_result = subprocess.run(doh_query_intermediate, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
        raw_data = json.loads(doh_result.stdout)[0]

        if ping_blocked and dou_blocked:
            print("RTT measurement blocked")
            round_trips = -1
            avg_rtt = -1
        else:
            round_trips = round(int(int(raw_data['time']/1000))/avg_rtt)
        print("DoH round trips: ", round_trips)

        cursor.execute(insert_resolver_measurement, (doh_id, 'h3', avg_rtt, raw_data['time'], round_trips , True, doh_result.stdout, False, False))
        db.commit()

        # do second measurement to find support for session resumption and 0-RTT
        doh_result = subprocess.run(doh_query_intermediate, shell=True, capture_output=True, text=True, cwd="../q-main") # using q
        raw_data_second = json.loads(doh_result.stdout)[0]

        if ping_blocked and dou_blocked:
            print("RTT measurement blocked")
            round_trips = -1
            avg_rtt = -1
        else:
            round_trips = round(int(int(raw_data_second['time']/1000))/avg_rtt)
        print("DoH round trips: ", round_trips)

        session_resumption = False
        rtt0 = False

        if(round(raw_data['time'] / raw_data_second['time']) <= 3):
            # session resumption and 0-RTT are supported
            session_resumption = True
            rtt0 = True
            cursor.execute(update_resolver_session_resumption, (doh_id,))
            cursor.execute(update_resolver_rtt0, (doh_id,))
            db.commit()
        elif (round(raw_data['time'] / raw_data_second['time']) == 2):
            # session resumption is supported but not 0-RTT
            session_resumption = True
            cursor.execute(update_resolver_session_resumption, (doh_id,))
            db.commit()
        
        # else session resumption and 0-RTT are not supported, initial values are correct
        cursor.execute(insert_resolver_measurement, (doh_id, 'h3', avg_rtt, raw_data['time'], round_trips , False, doh_result.stdout, session_resumption, rtt0))
        db.commit()

    # stop RouteDNS instances
    #subprocess.run("kill -7 " + route_dns_doq_pid, shell=True, capture_output=False) 
    #subprocess.run("kill -7 " + route_dns_doh_pid, shell=True, capture_output=False) 





    #print(type(doq_result.stdout))
    #print(".......error......")
    #if doq_result.stderr:
     #   print(type(doq_result.stderr))
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
    #subprocess.run(["q", query]) 

print("measurement completed")
