import json
import requests
from harvest import Harvest
harvester = Harvest()

source = '''{
                    "TxHash": "0x1dded4fa50021418bb53d4533d646101459420f223e236cfa18c497a3cc5f4fa",
                    "abiShaList": [],
                    "blockNumber": 3585676,
                    "creator": "0x6f2069eef02e84785fdbb16cd83ba3c9420c93e5",
                    "contractAddress": "0x980d755258aD3Ead9a16f6fCa0140f14059aCDd4",
                    "functionDataList": {
                        "0": [
                            {
                                "functionDataId": "0xb48d38f93eaa084033fc5970bf96e559c33c4cdc07d889ab00b4d63f9590739d",
                                "functionData": {},
                                "uniqueAbiAndAddressHash": "0x8756f8658e008294b2d0c08f2f9adcfe45ba7d558c2d6e924e6e29e2e072788b"
                            }
                        ]
                    },
                    "requiresUpdating": "yes",
                    "quality": "50",
                    "indexInProgress": "false"
                }'''
sourceJSON = json.loads(source)


#transferABI = '''[{"constant":true,"inputs":[],"name":"proxyType","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[],"name":"implementation","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_masterCopy","type":"address"},{"name":"initializer","type":"bytes"},{"name":"funder","type":"address"},{"name":"paymentToken","type":"address"},{"name":"payment","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"}]'''


transferABI = '''[{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'''


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


harvester.abiCompatabilityUpdate(transferABIJSON, sourceJSON)