import re
import json
import time
import requests
from harvest import Harvest

harvester = Harvest()

abiList = []
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xB8c77482e45F1F44dE1745F52C74426C631bDD52&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x2af5d2ad76741191d15dfe7bf6ac92d4bd912ca3&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x514910771af9ca656af840dff83e8264ecf986ca&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xd850942ef8811f2a866692a623011bde52a462c1&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x6c6ee5e31d828de241282b9606c8e98ea48526e2&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x0000000000013949f288172bd7e36837bddc7211&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xe41d2489571d322189246dafa5ebde1f4699f498&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x1985365e9f78359a9B6AD760e32412f4a445E862&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa15c7ebe1f07caf6bff097d8a589fb8ac49ae5b3&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x05f4a42e251f2d52b8ed15e9fedaacfcef1fad27&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x6f259637dcd74c767781e37bc6133cd6a68aa161&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb9469430eabcbfa77005cd3ad4276ce96bd221e3&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb5a5f22694352c15b00323844ad545abb2b11028&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8e870d67f660d95d5be530380d0ec0bd388289e1&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x039b5649a59967e3e936d7471f9c3700100ee1ab&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xfa1a856cfa3409cfa145fa4e20eb270df3eb21ab&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x1602af2c782cc03f9241992e243290fccf73bb13&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x3597bfd533a99c9aa083587b074434e61eb0a258&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x3883f5e181fccaf8410fa61e12b59bad963fb645&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf1290473e210b2108a85237fbcd7b6eb42cc654f&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x17aa18a4b64a55abed7fa543f2ba4e91f2dce482&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x39bb259f66e1c59d5abef88375979b4d20d98022&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb63b606ac810a52cca15e44bb630fd42d8d1d83d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x744d70fdbe2ba4cf95131626614a1763df805b9e&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xbf2179859fc6d5bee9bf9158632dc51678a4100e&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa974c709cfb4566686553a20790685a47aceaa33&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa74476443119A942dE498590Fe1f2454d7D4aC0d&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x37f04d2c3ae075fad5483bb918491f656b12bdb6&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8e1b448ec7adfc7fa35fc2e885678bd323176e34&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb7cb1c96db6b22b0d3d9536e0108d062bd488f74&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x5d65D971895Edc438f465c17DB6992698a52318D&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xb91318f35bdb262e9423bc7c7c2a3a93dd93c92c&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x8e766f57f7d16ca50b4a0b90b88f6468a09b0439&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x7c5a0ce9267ed19b22f8cae653f198e3e8daf098&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xbf52f2ab39e26e0951d2a02b49b7702abe30406a&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa4e8c3ec456107ea67d3075bf9e3df3a75823db0&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf76d4c449498dfd0c3f5a33ded00e796eb77a8d8&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x378903a03fb2c3ac76bb52773e3ce11340377a32&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xa576b808167c9e7a4208988258fd8a8efea2fc4f&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x0f5d2fb29fb7d3cfee444a200298f468908cc942&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xe0b7927c4af23765cb51314a0e0521a9645f0e2a&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0x4946fcea7c692606e8908002e55a582af44ac121&format=raw")
abiList.append("http://api.etherscan.io/api?module=contract&action=getabi&address=0xf5dce57282a584d2746faf1593d3121fcac444dc&format=raw")

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