import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

abiList = []
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x06012c8cf97bead5deae237070f9587f8e7a266d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x6EbeAf8e8E946F0716E6533A6f2cefc83f60e8Ab&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xBd13e53255eF917DA7557db1B7D2d5C38a2EFe24&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xfac7bea255a6990f749363002136af6556b31e04&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8c9b261faef3b3c2e64ab5e58e04615f8c788099&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xc1caf0c19a8ac28c41fe59ba6c754e4b9bd54de9&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8bc67d00253fd60b1afcce88b78820413139f4c6&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x273f7f8e6489682df756151f5525576e322d51a3&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xdceaf1652a131F32a821468Dc03A92df0edd86Ea&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x14c4293d7e7325cec8c52cea3df37d91aa9cc7b6&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5d00d312e171be5342067c09bae883f9bcb2003b&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x7b00ae36c7485b678fe945c2dd9349eb5baf7b6b&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa6dda780878d48853fe6cd96c7c1ebeaed7bfa01&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x9b81a139E24a33B6BFDAC826Dafd383d215cF8eA&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x00fdae9174357424a78afaad98da36fd66dd9e03&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x7e789e2dd1340971de0a9bca35b14ac0939aa330&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xbfde6246df72d3ca86419628cac46a9d2b60393c&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x959e104e1a4db6317fa58f8295f586e1a978c297&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xfcad2859f3e602d4cfb9aca35465a618f9009f7b&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xecd6b4a2f82b0c9fb283a4a8a1ef5adf555f794b&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5caebd3b32e210e85ce3e9d51638b9c445481567&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5fCCE8Ab5500ed68fF5d6d75aF1071195215D97E&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x36f16a0d35b866cdd0f3c3fa39e2ba8f48b099d2&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf766b3e7073f5a6483e27de20ea6f59b30b28f87&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x0111ac7e9425c891f935c4ce54cf16db7c14b7db&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x1344ae94912516d642f61f90e2c987b61f7db8d2&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb62b330a1b1ed55feb93296f89ea7679c4e0c36c&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5fCCE8Ab5500ed68fF5d6d75aF1071195215D97E&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x960f401aed58668ef476ef02b2a2d43b83c261d8&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xfbeef911dc5821886e1dda71586d90ed28174b7d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8853b05833029e3cf8d3cbb592f9784fa43d2a79&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xB06Ece7B0D5399eA0C381985f69585FDC355C5E4&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa98ad92a642570b83b369c4eb70efefe638bc895&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xd90f5ebc01914bbd357b754956aafb199f4d1624&format=raw")
for singleAbi in abiList:
    abiData1 = requests.get(singleAbi).content
    abiData1JSON = json.loads(abiData1)
    theDeterministicHash1 = harvester.shaAnAbi(abiData1JSON)
    cleanedAndOrderedAbiText1 = harvester.cleanAndConvertAbiToText(abiData1JSON)
    data1 = {}
    data1['indexInProgress'] = "false"
    data1['epochOfLastUpdate'] = int(time.time())
    data1['abi'] = cleanedAndOrderedAbiText1
    harvester.es.index(index=harvester.abiIndex, id=theDeterministicHash1, body=data1)