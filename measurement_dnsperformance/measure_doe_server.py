
import psycopg
import pymongo
import subprocess
import ipaddress


# connect to database 
client = pymongo.MongoClient("localhost", 27017)
db = psycopg.connect(dbname='web_performance')
cursor = db.cursor()

# reading data von MongoDB export
doe_db = client.doe
collection = doe_db['doq-scans']
cursor = collection.find({})

with open("Steffens_server_list.json", "a") as file:
   for scan_entry in cursor:
      try:
         ipaddress.ip_address( scan_entry['query']['doequery']['dnsquery']['host'])
         entry_ip = '{"domain": "", "ip": "?", "cert_check": "unknown", "country": "unknown", "as": "unknown"}\n'
         entry = entry_ip.replace("?", scan_entry['query']['doequery']['dnsquery']['host'])
      except ValueError:
         entry_domain = '{"domain": "?", "ip": "", "cert_check": "unknown", "country": "unknown", "as": "unknown"}\n'
         entry = entry_domain.replace("?", scan_entry['query']['doequery']['dnsquery']['host'])
      
      file.write(entry)
       

quit()

insert_statement = "INSERT INTO resolvers (dns, protocol, port) VALUES (%s, %s, %s);"

# DoQ standard port: 853
# DoH standard port 443
# DoU standard port 53


for scan_entry in cursor:
     #print(scan_entry)
     print(scan_entry['query'])
     print(scan_entry['query']['doequery']['dnsquery']['host'])
     print(scan_entry['query']['doequery']['dnsquery']['port'])

     port = scan_entry['query']['doequery']['dnsquery']['port']
     host = scan_entry['query']['doequery']['dnsquery']['host']
     
     if port == 853:
        protocol = 'quic'
     elif port == 443:
        protocol = 'http'
     elif port == 53:
        protocol = 'udp'
     else:
        protocol = 'unknown'

     #print(scan_entry['query']['uri'])
     #print(scan_entry['query']['httpversion'])
     #print(scan_entry['query']['method'])
     #print(scan_entry['query']['doequery']['dnsquery']['sni'])
     break

quit()




# q query
query = "go run . A ?server? --all -v  --additional"

# get server from database
server_list = ['dns.google.com']

# query DNS server
for server in server_list:
     subprocess.run(["q", server]) 

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

