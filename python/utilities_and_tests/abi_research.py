import json
from operator import itemgetter

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

def sortInternalListsInJsonObject(_json):
    for listItem in _json:
        for k, v in listItem.items():
            if type(v) not in (str, bool, int) and len(v) > 1:
                if type(v[0]) is dict:
                    v.sort(key=itemgetter("name", "type"))
                else:
                    v.sort()
    return _json

def sortTopLevelInJsonObject(_json):
    _json.sort(key=lambda x: x.get('type'), x.get('name'))
    #_json.sort(key=itemgetter("type", "name"))
    return _json

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
sortedAbi = sortTopLevelInJsonObject(abiWithSortedInternals)
print("Top level sort complete")
listWholeKeysAndValues(sortedAbi)
print("\nSorted ABI is as follows")
print("-START-")
print(sortedAbi)
print("-END-\n")