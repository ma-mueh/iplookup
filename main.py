import csv
from ipaddress import ip_address, ip_interface, ip_network
from pathlib import Path
import argparse
import re

# Define Argument Parser for script file arguments
parser = argparse.ArgumentParser(description="CSV Network Finder", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--ip", help="IP Address to check for")
args = parser.parse_args()

# Define CSV file location
csvpath = Path(r"C:\Users\BGP_TABLE_20210212.CSV")

# Define global variables
csvreader = ""
nwlist = []
lookupip = args.ip.split(",")
resultsdict = {}

def readcsv():
    # Read CSV and add content to a variable
    with open(csvpath, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for line in csvreader:
            nwlist.append(line)
    for index, line in enumerate(nwlist):
        nwlist[index][1] = re.sub("[\[\]]","", re.sub("\:", " ", line[1])).lstrip().rstrip()


def inputvalidation():
    # Validate entered IP address
    for ip in lookupip:
        try:
            ip_address(ip)
            lookupip[lookupip.index(ip)] = ip_address(ip)
            # legal
        except:
            print("{ip} Not a valid IP address, try again".format(ip=ip))


def networklookup():
    readcsv()
    inputvalidation()
    # Convert Strings in nwlist to network objects
    for row in nwlist: row[0] = ip_network(row[0])
    # Do the actual crosscheck
    for address in lookupip:
        resultsdict[address] = []
        for nw in nwlist:
            if address in nw[0]:
                resultsdict[address].append(nw)
    
    if resultsdict != {}:
        for key, value in resultsdict.items():
            print("{ip} is in this VRF:".format(ip=key))
            print(" ")
            for entry in value:
                print("VRF {vrf}, subnet {nw}".format(vrf=entry[1], nw=entry[0]))
            print("======================")
    else:
        for ip in lookupip:
            print("{ip} is not in the BGP table".format(ip=ip))

networklookup()
