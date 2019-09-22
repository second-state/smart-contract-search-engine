#TODO
# add imports that are not already in the harvest.py
# updated the function arguments so that they include self, 
# create es-ss.js function which will allow end users to query the amount of unique IP addresses for a given time period (and any other useful features such as hits per minute/hour etc.)
# create an io.py API interface so that es-ss.js can access this code (which will ultimately end up as a mode in the harvest.py)
# when adding this functionality to harvest.py be sure to add a timer so that it can be repeated over and over at a certain time interval


import os
import gzip

# accept an argument which is the apache access log directory
def processApache2AccessLogs(_logDir):
    for subdir, dirs, files in os.walk(_logDir):
        for file in files:
            if file.startswith("access"):
                if file.endswith(".gz"):
                    print("Extracting: " + file)
                    with gzip.open(os.path.join(_logDir, file), 'rb') as f1:
                        for line in f1:
                            print(line)
                    f1.close()
                else:
                    print("Processing: " + file)
                    with open(os.path.join(_logDir, file), 'rb') as f2:
                        for line in f2:
                            print(line)
                    f2.close()

# create a unique key which we can use for indexing

# check to see if the item is already indexed

# build the data structure and index the item

# 
_logDir = "/var/log/apache2/"
processApache2AccessLogs(_logDir)

