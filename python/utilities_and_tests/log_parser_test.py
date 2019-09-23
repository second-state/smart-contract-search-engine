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

def processSingleApacheAccessLogLine(_line):
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
        print("timestamp:" + str(timestamp))
        print("request: " + str(request))
        print("response: " + str(responseStatus))
        print("referer: " + str(referer))
        print(str(split_line))
    # print(six)
    # print(seven)
    # print(eight)
    # print(returnStatus)
    # print(dataTransfer)
    # print(split_line)

# accept an argument which is the apache access log directory
def processApache2AccessLogs(_logDir):
    for subdir, dirs, files in os.walk(_logDir):
        for file in files:
            if file.startswith("access"):
                if file.endswith(".gz"):
                    print("Extracting: " + file)
                    with gzip.open(os.path.join(_logDir, file), 'rt') as fGz:
                        for line in fGz:
                            processSingleApacheAccessLogLine(line)
                    fGz.close()
                else:
                    print("Processing: " + file)
                    with open(os.path.join(_logDir, file), 'rt') as f:
                        for line in f:
                            processSingleApacheAccessLogLine(line)
                    f.close()

# create a unique key which we can use for indexing

# check to see if the item is already indexed

# build the data structure and index the item

# 
_logDir = "/var/log/apache2/"
processApache2AccessLogs(_logDir)

