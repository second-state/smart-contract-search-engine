import re
import json
from harvest import Harvest
harvester = Harvest()

# ERC20 ABI
abi = json.loads('''[
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": true,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]''')

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

print("\nOriginal ABI is as follows")
print("-START-")
print(abi)
print("-END-\n")
# Print current order of inputs
print("Unsorted inputs")
listAbiItemInputs(abi)
# Print current order of outputs
print("Unsorted outputs")
listAbiItemOutputs(abi)
# Need to internally sort the input and output lists of each item first
# Order internal lists (inputs and outputs by the value component of the "name" key)
abiWithSortedInternals = sortInternalListsInJsonObject(abi)
# Print newly ordered inputs
print("Sorted inputs")
listAbiItemInputs(abiWithSortedInternals)
# Print newly ordered outputs
print("Sorted outputs")
listAbiItemOutputs(abiWithSortedInternals)
# Sort outer items by type, then name
sortedAbi = sort(abiWithSortedInternals)
print("Top level sort complete")
listWholeKeysAndValues(sortedAbi)
print("\nSorted ABI is as follows")
print("-START-")
print(json.dumps(sortedAbi))
print("-END-\n")
print("Breakdown of sorting")
sortingReport(sortedAbi)
# Sanitize string i.e. no additional characters aside from the keys, values and mandatory structural JSON characters like []{},; etc.
sanitizedString = harvester.sanitizeString(json.dumps(sortedAbi))
# Create hash
hashOfAbi = harvester.createHashFromString(sanitizedString)
print(hashOfAbi)



