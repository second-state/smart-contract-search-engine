import re
import json
import requests
from harvest import Harvest
harvester = Harvest()

# RAW text of ABIs for sorting and hashing
abiUrls = []
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/erc20abi.txt")
abiUrls.append("https://raw.githubusercontent.com/tpmccallum/test_endpoint2/master/erc20Abi2.txt")

def listAbiLength(_abi):
    print("The ABI has " + str(len(_abi)) + " items.")
    print("\n")

# List outputs
def listWholeKeysAndValues(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            print(str(k) + ": " + str(v))
        print("\n")
    print("\n")

# List types
def listAbiItemTypes(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "type":
                print(str(k) + ": " + str(v))
    print("\n")

# List names
def listAbiItemNames(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "name":
                print(str(k) + ": " + str(v))
    print("\n")

# List inputs
def listAbiItemInputs(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "inputs":
                print(str(k) + ": " + str(v))
    print("\n")

# List outputs
def listAbiItemOutputs(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "outputs":
                print(str(k) + ": " + str(v))
    print("\n")

# List payable
def listAbiItemPayable(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "payable":
                print(str(k) + ": " + str(v))
    print("\n")

# List stateMutability
def listAbiItemStateMutability(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            if str(k) == "stateMutability":
                print(str(k) + ": " + str(v))
    print("\n")

# Compare two items and return a bool
def compareItems(a, b):
    try:
        if str(a['type']) > str(b['type']):
            return True
        if str(a['name']) > str(b['name']):
            return True
    except:
        # Caters for cases where the name is not present i.e. a fallback function
        if str(a['type']) > str(b['type']):
            return True
    return False

# Sort a given json object
def sort(_json):
    for passnum in range(len(_json)-1,0,-1):
        for item in range(len(_json) - 1):
            if compareItems(_json[item], _json[item+1]) == True:
                temp = _json[item]
                _json[item] = _json[item+1]
                _json[item+1] = temp
    return _json

# Compare two items and return a bool
def compareKeys(a, b):
    if str(a) > str(b):
        return True
    return False

# Sort a given json object
def sortABIKeys(_json):
    for listItem in _json:
        for passnum in range(len(listItem)-1,0,-1):
            for item in range(len(listItem) - 1):
                if compareKeys(_json[item], _json[item+1]) == True:
                    temp = _json[item]
                    _json[item] = _json[item+1]
                    _json[item+1] = temp
    return _json

def sortInternalListsInJsonObject(_json):
    for listItem in _json:
        for k, v in listItem.items():
            print("Processing " + str(v))
            # Qualify the value as a list of JSON objects
            if type(v) not in (str, bool, int):
                # Qualify list as needing sorting (contains more than one item)
                if len(v) > 1:
                    # Qualify the sortable data is JSON
                    if type(v[0]) is dict:
                        print("Processing " + str(v))
                        sort(v)
                else:
                    print("Not enough items in the list to sort, moving on")
            else:
                print(str(v) + " is not a list, moving on ...")
    return _json

def sortingReport(_abi):
    for listItem in _abi:
        typeOuter = ""
        nameOuter = ""
        inputs = ""
        outputs = ""
        for k, v in listItem.items():
            if str(k) == "type":
                typeOuter = str(v)
            if str(k) == "name":
                nameOuter = str(v)
            if type(v) not in (str, bool, int):
                if len(v) >=1:
                    if type(v[0]) is dict:
                        if str(k) == "inputs":
                            inputs = str(v)
                        if str(k) == "outputs":
                            outputs = str(v)

        print("Type: " + typeOuter)
        print("Name: " + nameOuter)
        print("Inputs" + inputs)
        print("Outputs" + outputs)
        print("\n")

# Test the sorting and hashing of all ABIs in the abiUrls list (please add any new oddly ordered ABIs to that list so that we can ensure this code is robust)
outputHashes = []
for singleAbiUrl in abiUrls:
    singleAbiString = requests.get(singleAbiUrl).content
    singleAbiJSON = json.loads(singleAbiString)
    abiWithSortedInternals = sortInternalListsInJsonObject(singleAbiJSON)
    abiWithSortedKeys = sortABIKeys(abiWithSortedInternals)
    abiFullySorted = sort(abiWithSortedKeys)
    sanitizedString = harvester.sanitizeString(json.dumps(abiFullySorted))
    print("ABI")
    print(sanitizedString)
    hashOfAbi = harvester.createHashFromString(sanitizedString)
    outputHashes.append(hashOfAbi)

print("Output hashes are as follows, these should all be exactly the same")
for singleHash in outputHashes:
    print(singleHash)




