### Introduction
This repository features scripts to perform Web performance tests using different DNS protocols.
### Installation
- Download and start modified DNS Proxy: https://github.com/Lucapaulo/dnsproxy
- Install Python 3.X requirements: `pip install -r requirements.txt`
- Modify hardcoded filepaths inside `run_measurements.sh`
- Place upstream resolver(s) in `servers.txt` as list of IPv4 addresses
### How To
The script `run_measurements.sh` takes as input a list of resolvers in `servers.txt`. It calls the
Python script `run_measurements.py` to measure page load metrics for every resolver in `servers.txt`,
every DNS protocol listed in `run_measurements.sh` and every domain in the `pages` list inside the 
Python script.