#TODO
# add imports that are not already in the harvest.py
# updated the function arguments so that they include self, 
# create es-ss.js function which will allow end users to query the amount of unique IP addresses for a given time period (and any other useful features such as hits per minute/hour etc.)
# create an io.py API interface so that es-ss.js can access this code (which will ultimately end up as a mode in the harvest.py)
# when adding this functionality to harvest.py be sure to add a timer so that it can be repeated over and over at a certain time interval


import os
import gzip

def processSingleApacheAccessLogLine(_line):
    split_line = _line.split()
    callingIP = split_line[0]
    one = split_line[0]
    two = split_line[1]
    three = split_line[2]
    four = split_line[3]
    five = split_line[4]
    six = split_line[5]
    seven = split_line[6]
    eight = split_line[7]
    returnStatus = split_line[8]
    dataTransfer = split_line[9]
    print(callingIP)
    print(one)
    print(two)
    print(three)
    print(four)
    print(five)
    print(six)
    print(seven)
    print(eight)
    print(returnStatus)
    print(dataTransfer)

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

