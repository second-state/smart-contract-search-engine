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




listAbiLength(erc20Abi)
listAbiItemNames(erc20Abi)
listAbiItemTypes(erc20Abi)
listAbiItemInputs(erc20Abi)
listAbiItemOutputs(erc20Abi)
listAbiItemPayable(erc20Abi)
listAbiItemStateMutability(erc20Abi)
# Original ABI string
originalAbiString = json.dumps(erc20Abi)
# Original ABI hash
originalHash = getAbiHash(originalAbiString)
print("Original ABI hash:\n" + str(originalHash))
# Sanitized, yet unsorted ABI string
sanitizedAbiString = harvester.sanitizeString(originalAbiString)
# Sanitized, yet unsorted ABI hash
sanitizedHash = getAbiHash(sanitizedAbiString);
print("Sanitized ABI hash:\n" + str(sanitizedHash))
# 


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