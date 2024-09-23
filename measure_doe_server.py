
import psycopg
import pymongo
import subprocess



# connect to database 
db = psycopg.connect(dbname='web_performance')
cursor = db.cursor()

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

