from ipaddress import ip_address, ip_network
from operator import itemgetter
from datetime import date
from pathlib import Path
import argparse
import urllib.request
import csv
import re


# Define Argument Parser for script file arguments
parser = argparse.ArgumentParser(description="CSV Network Finder", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--ip", help="IP Address to check for")
args = parser.parse_args()

# Define CSV file location
today = date.today()
csvurl = "http://10.0.0.1/FUSION_RT/FUSION_BGP_TABLE_"+ today.strftime("%Y%m%d") + ".CSV"
csvfilename = "FUSION_BGP_TABLE_" + today.strftime("%Y%m%d") + ".CSV"
csvpath = urllib.request.urlretrieve(csvurl, filename=csvfilename)
#csvpath = requests.get("http://10.0.0.1/FUSION_RT/FUSION_BGP_TABLE_" + today.strftime("%Y%m%d") + ".CSV")


def readcsv(csvpath):
    # Read CSV and convert list of lists to dictionary
    with open(csvpath, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        bgpdict = {ip_network(x[0]): re.sub("[\[\]]", "", re.sub("\:", " ", x[1])).lstrip().rstrip() for x in csvreader}
    return bgpdict


def inputvalidation(argumentstring):
    # Validate entered IP address
    ip_list = []
    for ip in argumentstring.split(','):
        try:
            ip_list.append(ip_address(ip))
        except:
            print("{ip} Not a valid IP address, ignoring...\n======================".format(ip=ip))
    return ip_list


def networklookup(bgpdict, lookupip):
    output = []
    resultsdict = {}
    
    # Do the actual crosscheck
    for ip in lookupip:
        resultsdict[ip] = []
        for network, name in bgpdict.items():
            if ip in network:
                resultsdict[ip].append((name, network))

    output.append("============================================")
    output.append("Most exact matches for your addresses:")
    output.append("============================================")

    for key in resultsdict:
        most_exact = max(resultsdict[key], key=itemgetter(1))[0]
        output.append("The most exact VRF for " + str(key) + " is " + most_exact)

    output.append(" ")
    output.append("============================================")
    output.append("List of all matches:")
    output.append("============================================")

    for key, value in resultsdict.items():
        if len(value) > 0:
            output.append("{ip} is in this VRF:".format(ip=key))
            for name, network in value:
                output.append("      VRF {vrf}, subnet {nw}".format(vrf=name, nw=network))
            output.append("---------------------")
        else:
            output.append("{ip} is not in the BGP table".format(ip=ip))
 
    return output


print('\n'.join(networklookup(readcsv(csvpath), inputvalidation(args.ip))))
