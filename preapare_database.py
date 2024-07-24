import sqlite3
import requests
import csv

# just manually get pages list so the domain does not need to be resolved each time
#pages = ['www.google.com', 'www.netflix.com', 'www.youtube.com', 'www.facebook.com', 'www.microsoft.com', 'twitter.com', 'www.instagram.com', 'www.baidu.com', 'www.linkedin.com', 'www.apple.com', 'www.wikipedia.org', 'www.amazon.com']


# connect to db
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()

# get tranco list file
content = requests.get('https://tranco-list.eu/download/J939Y/full').content.decode('utf-8')
data = list(csv.reader(content.splitlines(), delimiter=','))

#print(data[0])

# insert into database
#pages = [(1, 'www.google.com')]

insert_statement = "INSERT INTO websites (_id, dns) VALUES (?, ?);"
cursor.executemany(insert_statement, data)
#cursor.executemany(insert_statement, pages)

db.commit()

# check that there is data in the database 
res = cursor.execute("SELECT _id, dns FROM websites LIMIT 10")

id, dns = res.fetchone()

print(f'ID: {id}, DNS Name {dns}')

id, dns = res.fetchone()

print(f'ID: {id}, DNS Name {dns}')

# close connection
db.close()
