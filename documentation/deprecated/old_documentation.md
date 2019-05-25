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
