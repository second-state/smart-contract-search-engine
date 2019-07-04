import json
from harvest import Harvest

harvester = Harvest()

# Official ABI copied verbatim from the ETH Wiki at https://github.com/ethereum/wiki/wiki/Contract-ERC20-ABI
officialERC20Abi = '''[
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
]
'''

officialBATAbi = '''[{"constant":true,"inputs":[],"name":"batFundDeposit","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"batFund","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"tokenExchangeRate","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"finalize","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"refund","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"tokenCreationCap","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"isFinalized","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"fundingEndBlock","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"ethFundDeposit","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"createTokens","outputs":[],"payable":true,"type":"function"},{"constant":true,"inputs":[],"name":"tokenCreationMin","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"fundingStartBlock","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"type":"function"},{"inputs":[{"name":"_ethFundDeposit","type":"address"},{"name":"_batFundDeposit","type":"address"},{"name":"_fundingStartBlock","type":"uint256"},{"name":"_fundingEndBlock","type":"uint256"}],"payable":false,"type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"LogRefund","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"CreateBAT","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]'''

#ERC20 
officialAbiJSON = json.loads(officialERC20Abi)
theDeterministicHash = harvester.shaAnAbi(officialAbiJSON)
cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(officialAbiJSON)
erc20Hashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedAbiText))
print("\nThe original ABI is as follows:")
print(officialAbiJSON)
print("\nThe cleaned and ordered ABI is as follows:")
print(cleanedAndOrderedAbiText)
print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicHash)
print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
print(erc20Hashes)

#BAT
officialBATAbiJSON = json.loads(officialBATAbi)
theDeterministicBATHash = harvester.shaAnAbi(officialBATAbiJSON)
cleanedAndOrderedBATAbiText = harvester.cleanAndConvertAbiToText(officialBATAbiJSON)
batHashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedBATAbiText))
print("\nThe original ABI is as follows:")
print(officialBATAbiJSON)
print("\nThe cleaned and ordered ABI is as follows:")
print(cleanedAndOrderedBATAbiText)
print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicBATHash)
print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
print(batHashes)


transferABI = '''[{"constant":true,"inputs":[],"name":"proxyType","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[],"name":"implementation","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_masterCopy","type":"address"},{"name":"initializer","type":"bytes"},{"name":"funder","type":"address"},{"name":"paymentToken","type":"address"},{"name":"payment","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'''
#ERC20 
transferABIJSON = json.loads(transferABI)
theDeterministicHash = harvester.shaAnAbi(transferABIJSON)
cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(transferABIJSON)
erc20Hashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedAbiText))
print("\nThe original ABI is as follows:")
print(transferABIJSON)
print("\nThe cleaned and ordered ABI is as follows:")
print(cleanedAndOrderedAbiText)
print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicHash)
print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
print(erc20Hashes)



transferABI = '''[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'''
#ERC20 
transferABIJSON = json.loads(transferABI)
theDeterministicHash = harvester.shaAnAbi(transferABIJSON)
cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(transferABIJSON)
erc20Hashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedAbiText))
print("\nThe original ABI is as follows:")
print(transferABIJSON)
print("\nThe cleaned and ordered ABI is as follows:")
print(cleanedAndOrderedAbiText)
print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicHash)
print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
print(erc20Hashes)


transferABI = '''[{"constant":true,"inputs":[],"name":"proxyType","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[],"name":"implementation","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_masterCopy","type":"address"},{"name":"initializer","type":"bytes"},{"name":"funder","type":"address"},{"name":"paymentToken","type":"address"},{"name":"payment","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'''

transferABIJSON = json.loads(transferABI)
theDeterministicHash = harvester.shaAnAbi(transferABIJSON)
cleanedAndOrderedAbiText = harvester.cleanAndConvertAbiToText(transferABIJSON)
erc20Hashes = harvester.createUniqueAbiComparisons(json.loads(cleanedAndOrderedAbiText))
print("\nThe original ABI is as follows:")
print(transferABIJSON)
print("\nThe cleaned and ordered ABI is as follows:")
print(cleanedAndOrderedAbiText)
print("\nThe Sha3 of this ABI is as follows:")
print(theDeterministicHash)
print("\nThe unique function hashes for this official ERC20 ABI are as follows:")
print(erc20Hashes)






