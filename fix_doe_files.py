import os
import re

# read all files in har_files (should only be har files) 
files = os.listdir('doeQueries/')

# ignore hidden files e.g. .DS_Store under MacOS
files = [f for f in files if f.endswith('.json')]

for file in files:
    print("process ", file)
    f = open('/Users/zitrusdrop/Desktop/Master/Semester_4/Masterarbeit_HPI/Experiments/forked/web-performance/doeQueries/doeQueries.ipv6.doh.json',"r+")
    #f = open('doeQueries/' + files[0], "w")
    with open('doeQueries/' + file, "r+") as f:
        content = f.read()
        content = re.sub('True','true',content)
        content = re.sub('False','false',content)
        content = re.sub('None','null',content)
        content = re.sub(r'ObjectId\(\'.*\'\)','""',content)
        content = re.sub(r'datetime.datetime\(',r'"datetime.datetime(',content)
        content = re.sub(r'000\),',r'000)",',content)
        content = re.sub("\'",'\"',content)
        content = re.sub(r'}\n{',r'},{',content)
        content = re.sub(r': b.\S+', r': "",' ,content)
        f.seek(0)
        f.truncate(0)
        f.write("["+content+"]")
