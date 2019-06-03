**Please note that there is a convention which must be followed in the configuration.**
Please use index name underscore contract version i.e. `fairlpay_v1` as shown below. For example, do not use double underscores or more than one underscore in the string. If this convention is properly followed, the harvester will automatically create an index called "fairplay" (if it does not already exist) and it will also index all contracts which match the abi and bytecode with a version attribute of "v1".

You can add multiple abi URLs and bytecode URLs, but remember - they are in relation to specific smart contract and as such they need to be appropriately named with the convention.

- Provide one or more links to each specific RAW abi file under the abis section heading
```
[abis]
fairplay_v1 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi
fairplay_v2 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.abi
```
- Provide one or more links to each specific RAW bytecode file under the bytecode section heading
```
[bytecode]
fairplay_v1 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin
fairplay_v2 = https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.bin
```


Creating a web3 contract instance in the command line for testing

```python
import os
import re
import time
import json
import argparse
import requests
import configparser
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth 
from elasticsearch import Elasticsearch, RequestsHttpConnection

# CWD
scriptExecutionLocation = os.getcwd()

# Config
print("Reading configuration file")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(os.path.join(scriptExecutionLocation, 'config.ini'))

abiIndex = config['abiindex']['abi']
print("Abi index: %s" % abiIndex)

# Bytecode index
bytecodeIndex = config['bytecodeindex']['bytecode']
print("Bytecode index: %s" % bytecodeIndex)

# Elasticsearch endpoint
elasticSearchEndpoint = config['elasticSearch']['endpoint']
print("ElasticSearch Endpoint: %s" % elasticSearchEndpoint)

# Elasticsearch AWS region
elasticSearchAwsRegion = config['elasticSearch']['aws_region']

auth = BotoAWSRequestsAuth(aws_host=elasticSearchEndpoint, aws_region=elasticSearchAwsRegion, aws_service='es')
es = Elasticsearch(
    hosts=[{'host': elasticSearchEndpoint, 'port': 443}],
    region=elasticSearchAwsRegion,
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection
)

#v1
abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
abiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))
abiData = re.sub(r"[\s]+", " ", abiData)
abiSha = web3.toHex(web3.sha3(text=abiData))
print(abiSha)
print(abiData)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['abi'] = abiData
es.index(index=abiIndex, id=abiSha, body=data)
#v2
abiUrl = "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.abi"
abiData = re.sub(r"[\n\t]*", "", json.dumps(json.loads(requests.get(abiUrl).content)))
abiData = re.sub(r"[\s]+", " ", abiData)
abiSha = web3.toHex(web3.sha3(text=abiData))
print(abiSha)
print(abiData)
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['abi'] = abiData
es.index(index=abiIndex, id=abiSha, body=data)

#v1
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCodeSha = web3.toHex(web3.sha3(text=byteCode))
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
es.index(index=bytecodeIndex, id=byteCodeSha, body=data)
#v2
binObject = requests.get("https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v2/dapp/FairPlay.bin").content
binJSONObject = json.loads(binObject)
byteCode = "0x" + binJSONObject['object']
byteCodeSha = web3.toHex(web3.sha3(text=byteCode))
data = {}
data['indexInProgress'] = "false"
data['epochOfLastUpdate'] = int(time.time())
data['bytecode'] = byteCode
es.index(index=bytecodeIndex, id=byteCodeSha, body=data)
```

str(web3.toHex(web3.sha3(text=json.dumps(abiData))))

Remove unwanted index results
POST

https://search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com/cmtmainnet/_delete_by_query

Using the following

{
  "query": { 
    "match": {
      "functionData.owner": "0x86eEB4105814b1A590939670eBDF3b72ba078025"
    }
  }
}

{
  "query": { 
    "match": {
      "functionData.owner": "0x38B1BdA00f103C30547E5D31dbF1c1Dfc356F9F0"
    }
  }
}

{
  "query": { 
    "match": {
      "functionData.owner": "0x779CBe4355268df897927B671C9c65673DeD0Fee"
    }
  }
}


{
  "query": { 
    "match": {
      "functionData.owner": "0xAD0aec5FCa1E1FB5Ac84aB06aA813DE6B6105a27"
    }
  }
}

{
  "query": { 
    "match": {
      "functionData.owner": "0xEBfC71f4ef3Eda82B65dE04B1cf1994f28C3B9CC"
    }
  }
}


# Reference this for shell scripts and cron

## Initial harvest - Phase 1 (must commence before phase 2)

**UPDATE - now 100x faster than before** 
This harvest_all.py script has been upgraded to perform the `-m full` mode of harvesting 100x faster than it used to. Here is the logic of the code. This code logic is just for your interest; the code will just work 100x faster now if you just run the same command.
```
# -m full code gets the latest block number
latestBlockNumber = harvester.web3.eth.getBlock('latest').number
# then facilitates one hundred separate IO threads
threadsToUse = 100
# then it will work out how many blocks will be harvested per thread
blocksPerThread = int(latestBlockNumber / threadsToUse)
# the harvestAllContracts function is then called 100 separate times simultaneously using these unique block number parameters
```
The good thing about this method is that each of the threads starts at even spacings in the blockchain so there is an evenly spread amount of block harvesting going on simultaneously. The harvest_all.py can be raised above 100x by adjusting the `threadsToUse` variable. We are just using this here because the m5.large instance from AWS is comfortable at about 60% CPU. Please check your servers capacity under load using `top` and increase this number to what you see fit.

**Command line usage**
```
python3.6 harvest_all.py -h
usage: harvest_all.py [-h] [-m MODE]

Harvester < https://github.com/second-state/smart-contract-search-engine >

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  [full|topup]
```

### Recommended usage - Run once at startup!
**Run at startup**

Technically speaking (in the long term) once the project is well underway, you will just want to run all of these commands the **one** time, at startup! i.e. ensure that they are always running.

The system will take care of itself. Here is an example of how to run this once at startup.

**Phase 1 - Step 1**
Create a bash file, say, `~/startup1.sh` and make it executable with the `chmod a+x` command. Then put the following code in the file.
Please be sure to replace `https://testnet-rpc.cybermiles.ii:8545` with that of your RPC.
```bash
#!/bin/bash
while true
do
  STATUS=$(curl --max-time 30 -s -o /dev/null -w '%{http_code}' https://testnet-rpc.cybermiles.io:8545)
  if [ $STATUS -eq 200 ]; then
    cd ~/smart-contract-search-engine/python && nohup /usr/bin/python3.6 harvest_all.py -m full >/dev/null 2>&1 &
    cd ~/smart-contract-search-engine/python && nohup /usr/bin/python3.6 harvest_all.py -m topup >/dev/null 2>&1 &
    break
  else
    echo "Got $STATUS please wait"
  fi
  sleep 10
done
``` 
**Phase 1 - Step 2**
Add the following command to cron using `crontab -e` command.
```bash
@reboot ~/startup1.sh
```

## Subsequent harvest - Phase 2 (must only commence once phase 1 is well underway)
```
cd ~/smart-contract-search-engine/python

python3.6 harvest.py -h

usage: harvest.py [-h] [-m MODE]

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  [full|topup|state]
```


