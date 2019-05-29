# Usage

The search engine can be used, by end users, via their web browser. It can also provide data to users and machines via the public facing API.

## API usage

** Curl **
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

** Javascript **
```javascript
_data = {
    "query": {
        "match_all": {}
    }
}
var _dataString = JSON.stringify(_data);
$.ajax({
    url: "http://54.252.157.165/api/data2",
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
![return data example](images/javascript_api_response.png)

