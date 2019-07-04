import json
import requests
from harvest import Harvest
harvester = Harvest()

source = '''{
                    "TxHash": "0x233e6634b6e713fae69799305794cb679c9a3a89181a3f391d5971df5beaf7d6",
                    "abiShaList": [
                        "0x50d9155267cb10b61afba8628bdc6181de9af836918d7987c2c421512256ab82"
                    ],
                    "blockNumber": 4964970,
                    "creator": "0xb156929f55c48265607fd87b9e2d6fcceee6726a",
                    "contractAddress": "0xA362e5Bc203AEA01C398B74aA6e36d144E96712f",
                    "functionDataList": {
                        "0": [
                            {
                                "functionDataId": "0x3a851ba992dd5464cc247cb21fb0a92a11dd417fc2a028fcbede22ef693efc6d",
                                "functionData": {
                                    "name": "Arcblock Token",
                                    "totalSupply": "1000000000000000000000000000",
                                    "decimals": "18",
                                    "symbol": "ABT"
                                },
                                "uniqueAbiAndAddressHash": "0x54040994221542e1ce9fdfc9c7396d02de07a2b7df065865b8a404a5498c6fef"
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