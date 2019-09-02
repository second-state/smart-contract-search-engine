import json
from harvest import Harvest
harvester = Harvest()

# ERC20 ABI
erc20Abi = json.loads('''[
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

def getAbiHash(_abi):
    return str(harvester.web3.toHex(harvester.web3.sha3(text=_abi)))

# DRAFT - to be completed and tested
def compareAbiItems(_itemA, _itemB):
    return str(_itemA["type"]) < str(_itemB["type"]) or str(_itemA["type"]) == str(_itemB["type"]) and str(_itemA["name"]) < str(_itemB["name"]) or str(_itemA["name"]) == str(_itemB["name"]) and str(_itemA["inputs"]) < str(_itemB["inputs"]) or str(_itemA["inputs"]) == str(_itemB["inputs"]) and str(_itemA["outputs"]) < str(_itemB["outputs"])

# DRAFT - to be completed and tested
def sort(_abi):
    for listItem in _abi:
        for k, v in listItem.items():
            print(k)

# ERC20 Testing
#listAbiLength(erc20Abi)
#listWholeKeysAndValues(erc20Abi)
#listAbiItemNames(erc20Abi)
#listAbiItemTypes(erc20Abi)
#listAbiItemInputs(erc20Abi)
#listAbiItemOutputs(erc20Abi)
#listAbiItemPayable(erc20Abi)
#listAbiItemStateMutability(erc20Abi)
# Original ABI string
#originalAbiString = json.dumps(erc20Abi)
# Original ABI hash
#originalHash = getAbiHash(originalAbiString)
#print("Original ABI hash:\n" + str(originalHash))
# Sanitized, yet unsorted ABI string
#sanitizedAbiString = harvester.sanitizeString(originalAbiString)
#print(sanitizedAbiString)
# Sanitized, yet unsorted ABI hash
#sanitizedHash = getAbiHash(sanitizedAbiString);
#print("Sanitized ABI hash:\n" + str(sanitizedHash))
# 

# Simple Testing
abi = json.loads('''[{
    "type": "zulu",
    "name": "yankee",
    "inputs": [{
        "name": "oscar",
        "type": "uint256"
    }],
    "outputs": [{
        "name": "golf",
        "type": "uint256"
    }, {
        "name": "",
        "type": "address"
    },{
        "name": "_golf",
        "type": "address"
    },{
        "name": "yankee",
        "type": "uint256"
    }],
    "anonymous": false,
    "payable": false,
    "stateMutability": "view",
    "constant": true
},{
    "type": "zulu",
    "name": "yankee",
    "inputs": [{
        "name": "delta",
        "type": "uint256"
    }, {
        "name": "charlie",
        "type": "address"
    }],
    "outputs": [{
        "name": "zulu",
        "type": "address"
    }, {
        "name": "yankee",
        "type": "uint256"
    }],
    "anonymous": false,
    "payable": false,
    "stateMutability": "view",
    "constant": true
}, {
    "type": "alpha",
    "name": "beta",
    "inputs": [{
        "name": "alpha",
        "type": "uint256"
    }, {
        "name": "beta",
        "type": "address"
    }],
    "outputs": [{
        "name": "beta",
        "type": "address"
    }, {
        "name": "aplha",
        "type": "address"
    }],
    "anonymous": false,
    "payable": false,
    "stateMutability": "view",
    "constant": true
},{
    "type": "yankee",
    "name": "xray",
    "inputs": [{
        "name": "",
        "type": "uint256"
    },{
        "name": "",
        "type": "address"
    },{
        "name": "zulu",
        "type": "address"
    }, {
        "name": "yankee",
        "type": "uint256"
    }],
    "outputs": [{
        "name": "november",
        "type": "address"
    }],
    "anonymous": false,
    "payable": false,
    "stateMutability": "view",
    "constant": true
}]''')


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
    _json.sort(key=itemgetter("type", "name"))
    return _json

print("\Original ABI is as follows")
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

# Then we can simply sort the outer type, name, inputs, outputs by string representation (because the internal inputs and outputs will already be correct)



# Background
# https://github.com/ethereum/solidity/issues/2731
# I suggest that we sort it deterministically as follows: lexicographic sorting by the values of the following keys:

# type
# name
# inputs
# outputs
# That means the usual order will be something like:

# constructor
# event(address, address)
# event(uint, address)
# fallback
# function(address, address)
# function(uint, address)