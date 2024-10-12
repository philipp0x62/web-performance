import psycopg
import json
import tldextract 
import pprint
import os

# just manually get pages list so the domain does not need to be resolved each time
#pages = ['www.google.com', 'www.netflix.com', 'www.youtube.com', 'www.facebook.com', 'www.microsoft.com', 'twitter.com', 'www.instagram.com', 'www.baidu.com', 'www.linkedin.com', 'www.apple.com', 'www.wikipedia.org', 'www.amazon.com']


# connect to db
db = psycopg.connect(dbname='web_performance')
cursor = db.cursor()

#cursor.execute("DELETE FROM mime_types")

# read all files in har_files (should only be har files) 
files = os.listdir('har_files/')

# ignore hidden files e.g. .DS_Store under MacOS
files = [f for f in files if not f.startswith('.')]


for file in files:
    mimeTypes = {} # contains the different mimeTypes as keys, there count of occurences, there accumulated header and body sizes
    queried_servers = set()
    non_origin_servers = set()
    print('processing: ', file)
    with open('har_files/' + file) as f:
        har = json.load(f)

        
        for entry in har['log']['entries']:
            # processing mime type data 
            mimeType = entry['response']['content']['mimeType']
            if mimeType in mimeTypes:
                mimeTypes[mimeType]['occurences'] += 1
                mimeTypes[mimeType]['bytes_header_download'] += entry['response']['headersSize']
                mimeTypes[mimeType]['bytes_body_download'] += entry['response']['bodySize']
            else:
                 mimeTypes[mimeType] = {'occurences': 1, 'bytes_header_download': 0, 'bytes_body_download': 0} 
                 mimeTypes[mimeType]['bytes_header_download'] += entry['response']['headersSize']
                 mimeTypes[mimeType]['bytes_body_download'] += entry['response']['bodySize']

            # getting different servers
            #print('url:  ' + entry['request']['url'])
            #print(type(entry['request']['url']))
            website = tldextract.extract(entry['request']['url'])
            #print(website)
            #print(website.subdomain)
            #print(website.domain)
            #print(website.suffix)
            #print(website.fqdn)
            queried_servers.add(website.fqdn)
            if(website.registered_domain != file): # file is named after domain
                non_origin_servers.add(website.fqdn)

        objects_total = sum(mimeTypes[item]['occurences'] for item in mimeTypes)
        bytes_total = sum(mimeTypes[item]['bytes_header_download'] + mimeTypes[item]['bytes_body_download'] for item in mimeTypes)

        #print('objects total: ', objects_total)
        #print('bytes total: ', bytes_total)
        #print('number queried servers: ', len(queried_servers))
        #print('number non origin servers', len(non_origin_servers))
        #print('number differrent mime types: ', len(mimeTypes.keys()))
        #print('mime types dictonary \n ==================')
        #pprint.pp(mimeTypes)
        # put data in the database 
        res = cursor.execute("""UPDATE websites SET 
                             number_objects_loaded=%s, 
                             number_queried_servers=%s, 
                             number_non_origin_servers=%s, 
                             number_mime_types=%s, 
                             bytes_downladed=%s 
                             WHERE dns=%s""", (objects_total, len(queried_servers), len(non_origin_servers), len(mimeTypes.keys()), bytes_total, file))
        cursor.execute("SELECT _id FROM websites WHERE dns=%s", (file,))
        id = res.fetchone()
        keys = mimeTypes.keys()
        for mimeType in keys:
            res = cursor.execute("INSERT INTO mime_types (website_id, mime_type, occurences, bytes_body_download, bytes_header_download) VALUES(%s, %s, %s, %s, %s)", 
                                 (id[0], 
                                 mimeType, 
                                 mimeTypes[mimeType]['occurences'], 
                                 mimeTypes[mimeType]['bytes_body_download'],  
                                 mimeTypes[mimeType]['bytes_header_download']
                                 ))
        db.commit()


# close connection
db.close()
