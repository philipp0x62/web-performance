
import psycopg
import pymong
import ipaddress

print("Creating JSON lines file out of Steffen's database export")

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
       
print("json file created")