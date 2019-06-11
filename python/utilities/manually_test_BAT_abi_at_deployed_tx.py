import harvest

harvester = Harvest()

#BAT 
abiUrl = "http://api.etherscan.io/api?module=contract&action=getabi&address=0x0d8775f648430679a709e98d2b0cb6250d2887ef&format=raw"
abiData = requests.get(abiUrl).content
abiObject = json.loads(abiData)
cleanAbiString = cleanAndConvertAbiToText(abiObject)

txReceipt = web3.eth.getTransactionReceipt("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
tx = web3.eth.getTransaction("0xcceb1fd34dcc4b18defa4ff29d51a225b20af8ed179db37da72ec5d5a4e8d385")
#makerInstance = web3.eth.contract(abi=makerAbi, address=txReceipt.contractAddress)
batInstance = web3.eth.contract(abi=abiObject, address=web3.toChecksumAddress("0x0d8775f648430679a709e98d2b0cb6250d2887ef"))
functionData = harvester.fetchPureViewFunctionData(batInstance)
print(functionData)

