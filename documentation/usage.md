# Usage

The search engine can be used, by end users, via their web browser. It can also provide data to users and machines via the public facing API.

## API usage - using curl at the command line

```bash
curl -X GET "https://cmt-testnet.search.secondstate.io/api/es_search" -H 'Content-Type: application/json' -d' {"query": {"match": {"contractAddress": "0x909350a510BCf568e66019E21F1598D8282be26C"}}}'
```
Returns
```bash
{
  "1": {
    "_id": "0xa8bf1574123db27eadaceeccfd93f101bf4293d41c3238106183c93c60a060e8", 
    "_index": "cmttestnet", 
    "_score": null, 
    "_source": {
      "TxHash": "0xc855e2ceafadbdfa2348329e43536a36eb775c433df6250bb7b779ab23712fb2", 
      "abiSha3": "0x462e4b9caf0a0f1355cf55d46b7f6da2b3812eec59c230e23f743b77dac4491c", 
      "abiURL": "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi", 
      "blockNumber": 1819563, 
      "byteCodeURL": "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin", 
      "contractAddress": "0x909350a510BCf568e66019E21F1598D8282be26C", 
      "dappVersion": "v1", 
      "functionData": {
        "desc": "##### Description\n\nTest SSL\n\n", 
        "image_url": "https://res.cloudinary.com/dgvnn4efo/image/upload/v1559129560/ygd6wnjmi79bm5iih9cn.jpg", 
        "info": {
          "0": 0, 
          "1": "Test SSL", 
          "2": "##### Description\n\nTest SSL\n\n", 
          "3": "https://res.cloudinary.com/dgvnn4efo/image/upload/v1559129560/ygd6wnjmi79bm5iih9cn.jpg", 
          "4": 1, 
          "5": 1559216220
        }, 
        "number_of_winners": 1, 
        "owner": "0xEBfC71f4ef3Eda82B65dE04B1cf1994f28C3B9CC", 
        "player_addrs": {
          "0": "0xEBfC71f4ef3Eda82B65dE04B1cf1994f28C3B9CC"
        }, 
        "status": 0, 
        "title": "Test SSL"
      }, 
      "functionDataId": "0xf62ed1a6bf6a9f0309f094cf116255ae01d275a51e4c7dcc06e301e599a76dc0", 
      "requiresUpdating": "yes", 
      "status": 0
    }, 
    "_type": "_doc", 
    "sort": [
      0
    ]
  }
}

```

## API usage - using Javascript/JQuery AJAX via browser or console
```javascript
_data = {
    "query": {
        "match_all": {}
    }
}
var _dataString = JSON.stringify(_data);
$.ajax({
    url: "https://cmt-testnet.search.secondstate.io/api/es_search",
    type: "POST",
    data: _dataString,
    dataType: "json",
    contentType: "application/json",
    success: function(response) {
        console.log(response);
    },
    error: function(xhr) {
        console.log("Get items failed");
    }
});
```
Returns
```javascript
_id: "0xa8bf1574123db27eadaceeccfd93f101bf4293d41c3238106183c93c60a060e8"
_index: "cmttestnet"
_score: null
_source:
TxHash: "0xc855e2ceafadbdfa2348329e43536a36eb775c433df6250bb7b779ab23712fb2"
abiSha3: "0x462e4b9caf0a0f1355cf55d46b7f6da2b3812eec59c230e23f743b77dac4491c"
abiURL: "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
blockNumber: 1819563
byteCodeURL: "https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.bin"
contractAddress: "0x909350a510BCf568e66019E21F1598D8282be26C"
dappVersion: "v1"
functionData:
desc: "##### Description↵↵Test SSL↵↵"
image_url: "https://res.cloudinary.com/dgvnn4efo/image/upload/v1559129560/ygd6wnjmi79bm5iih9cn.jpg"
info:
0: 0
1: "Test SSL"
2: "##### Description↵↵Test SSL↵↵"
3: "https://res.cloudinary.com/dgvnn4efo/image/upload/v1559129560/ygd6wnjmi79bm5iih9cn.jpg"
4: 1
5: 1559216220
__proto__: Object
number_of_winners: 1
owner: "0xEBfC71f4ef3Eda82B65dE04B1cf1994f28C3B9CC"
player_addrs:
0: "0xEBfC71f4ef3Eda82B65dE04B1cf1994f28C3B9CC"
__proto__: Object
status: 0
title: "Test SSL"
```

The above examples demonstrate how to query the `api/es_search` endpoint. The great thing about the `api/es_search` endpoint is that it is 100% Elasticsearch (DSL Query) compatible. Please see the official Elasticsearch documentation for more information about:
- [Match all Queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-all-query.html), 
- [Full text queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html), 
- [Exists query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html), 
- [Wildcard query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-wildcard-query.html) 
- and many more [query examples](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html).

# Contract Instance Versioning

A frontend application can calculate and define a label for a particlar version of a contract instance. For example there may be a smart contract initiative like the [FairPlay](https://github.com/CyberMiles/smart_contracts/tree/master/FairPlay) "Product Giveaway" which gets upgraded with new features i.e. the [version 1](https://github.com/CyberMiles/smart_contracts/tree/master/FairPlay/v1) smart contract still exists but the business expands the Product Giveaway's functionality (with new features) and calls this [version 2](https://github.com/CyberMiles/smart_contracts/tree/master/FairPlay/v2). It is important that the end users know which version they are seeing in the search results.

The smart contract search engine provide a very flexible mechanism for smart contract versioning. 
This is how it work. 
The smart contract search engine:
- creates a deterministic hash of the each known ABI (sorting the keys inside the ABI for absolute determinism) 
- goes through every block, every transaction and every known ABI and maintains a list of the deteministic ABI hashes (as a list data field, inside every indexed smart contract instance)
- creates a deterministic hash of each known Bytecode 
- goees through every block every transaction and every known Bytecode and maintains a field inside every smart contract instance

At any given time, each smart contract instance (which is indexed) has a list of ABI hashes and a single Bytecode hash. This allows end users to search the search engine for contracts of a particular genre i.e. return all of the ERC20 compatible contracts etc. Of course some smart contract instances might be compatible with multiple ABI standards; this is why there is a list of ABI hashes as apposed to just one ABI has per contract instance.

DApp developers can:
- use any combination of ABI hashes (and the single bytecode hash) to uniquely identify a given contract
- create the deterministic hashes themselves and build their frontend application regardless of what is or isn't in the search engine at that point in time
- Use simple code, like the following Javascript example, to dynamically set the contract version in the frontend display of the DApp.

```Javascript
// The ABI of their smart contract
abi1Sha3 = "0x462e4b9caf0a0f1355cf55d46b7f6da2b3812eec59c230e23f743b77dac4491c";
// The ABI of another smaller smart contract which is also available internally
abi2Sha3 = "0x2222222222222222222222222222222222222222222222222222222222222222";
// Another example of a smaller contract i.e. the overall large smart contract might have internal ERC20 or ERC721 functionality
abi3Sha3 = "0x3333333333333333333333333333333333333333333333333333333333333333";
// Bytecode hash (which is also able to be deterministically generated by the frontend developer ahead of time)
bytecodeSha3 = "0x1234567890123456789012345678901234567890123456789012345678901234567";
// Once the data is returned to the frontend, this simple and fast code can be used to set the version number for display
if (_responseData.includes(abi1Sha3) && _responseData.includes(abi2Sha3) && _responseData.includes(abi3Sha3) && _responseData.includes(bytecodeSha3)){
    version = "v1"
}
```
