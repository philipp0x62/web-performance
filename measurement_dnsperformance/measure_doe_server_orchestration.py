
import pandas as pd
import os
import numpy as np
import math

#VARIABLES
INSTANCES = 4


# read all files in har_files (should only be har files) 
# data source: https://port-53.info/data/open-encrypted-dns-servers/
df_doq = pd.read_json('doeQueries/doq-2024-03.json', lines=True)
df_doh = pd.read_json('doeQueries/doh3-2024-03.json', lines=True)
df_doe = pd.read_json('doeQueries/Steffens_server_list.json', lines=True)


# merge lists 
df_doq['protocol'] ='quic'
df_doh['protocol'] ='h3'
df_doe['protocol'] ='unknown'
df_resolvers = pd.concat([df_doh, df_doq, df_doe])


# make resolvers in table unique to speed up the script
df_ip_only = df_resolvers.loc[df_resolvers['domain'] == '']
df_ip_only = df_ip_only.drop_duplicates(subset=['ip'])
#print(df_ip_only)
df_resolvers = df_resolvers.drop_duplicates(subset=['domain'])
df_resolvers = pd.concat([df_resolvers, df_ip_only])

print("number of unique resolvers: ", df_resolvers.shape[0])

#create for each process an own json line file.
chunks_df = np.array_split(df_resolvers, INSTANCES)

i = 0
for chunk in chunks_df:
    chunk.to_json("instances_json_data/input_instance_"+ str(i) +".json", orient="records", lines=True)
    i+=1






print("measurement completed")
