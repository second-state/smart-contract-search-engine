#TODO
# add imports that are not already in the harvest.py
# updated the function arguments so that they include self, 

import os
import gzip

# accept an argument which is the apache access log directory
def processApache2AccessLogs(_logDir):
    for subdir, dirs, files in os.walk(_logDir):
        for file in files:
            if file.startswith("access"):
                if file.endswith(".gz"):
                    print("Extracting: " + file)
                    f = gzip.open(os.path.join(_logDir, file), 'rb')
                    fileContent = f.read()
                    f.close()
                else:
                    print("Processing: " + file)
                    f = open(os.path.join(_logDir, file), 'rb')
                    fileContent = f.read()
                    f.close()

# create a unique key which we can use for indexing

# check to see if the item is already indexed

# build the data structure and index the item

# 
_logDir = "/var/log/apache2/"
processApache2AccessLogs(_logDir)

