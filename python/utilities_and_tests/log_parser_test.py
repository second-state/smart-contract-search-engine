#TODO
# add imports that are not already in the harvest.py
# updated the function arguments so that they include self, 
# create es-ss.js function which will allow end users to query the amount of unique IP addresses for a given time period (and any other useful features such as hits per minute/hour etc.)
# create an io.py API interface so that es-ss.js can access this code (which will ultimately end up as a mode in the harvest.py)
# when adding this functionality to harvest.py be sure to add a timer so that it can be repeated over and over at a certain time interval


import os
import gzip
import math
from datetime import datetime

def processSingleApacheAccessLogLine(self, _line):
    split_line = _line.split()
    # IP
    callingIP = split_line[0]
    # Time
    try:
        time = str.join(" ",(split_line[3], split_line[4]))
        time = time.replace("[", "")
        time = time.replace("]", "")
        d = datetime.strptime(time, "%d/%b/%Y:%H:%M:%S %z")
        timestamp = math.floor(d.timestamp())
    except:
        timestamp = 0
    # Request
    try:
        request = str(split_line[5])
        request = request.replace("\"", "")
    except:
        request = ""
    # Response status code
    try:
        responseStatus = str(split_line[8])
    except:
        responseStatus = ""
    # Referer
    try:
        referer = str(split_line[10])
        referer = referer.replace("\"", "")
    except:
        referer = ""
    if timestamp > 0:
        uniqueHash = str(self.web3.toHex(self.web3.sha3(text=str(split_line))))
        if self.hasLogBeenIndexed(self.logAnalyticsIndex, uniqueHash) != True:
            data = {}
            data["timestamp"] = timestamp
            data["request"] = request
            data["responseStatus"] = responseStatus
            data["referer"] = referer
            data["uniqueHash"] = uniqueHash
            indexingResult = self.loadDataIntoElastic(self.logAnalyticsIndex, uniqueHash, json.dumps(data))

# accept an argument which is the apache access log directory



# check to see if the item is already indexed

# build the data structure and index the item

# 
_logDir = "/var/log/apache2/"
processApache2AccessLogs(_logDir)

