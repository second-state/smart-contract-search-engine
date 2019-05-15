# Local Mode

Running this smart contract search engine in local mode can be done by simply downloading the project and opening the index.html file in your web browser.

The data for this local mode operation is provided by an open and public Elasticsearch endpoint. The open and public Elasticsearch endpoint URL must be added to the `var elasticSearchUrl` in the [secondStateJS.js file](../js/secondStateJS.js).

If running this in loca mode, please make sure that the `var publicIp = "";` in the [secondStateJS.js file](../js/secondStateJS.js) is set to a blank string, as shown here `""`.

**This (local mode) is really only intended for prototyping, development and testing.** The reason being, if the Elasticsearch endpoint is open then anyone can access, modify and delete the data. Seeings how blockchain data is completely public and open, running this search engine in local mode can facilitate rapid development and prototyping. 

On one hand, if you are using a local (single user) Elasticsearch instance (i.e. localhost endpoint as apposed to a public endpoint) then of course you can simply configure your own local firewall to secure your data. 

Once you are ready to invite the world to use your search engine please switch to global mode (because global mode provides access control). Speaking of global mode, if you would like to run the smart contract search engine in a production environment (as part of your DApp etc) please go ahead and read the documentation for [global mode](./global_mode.md)).

## Local Mode - Configuration

### DApp endpoint

You will notice that this search engine is currently configured to demonstrate the Product Giveaway DApp (which is running on the CyberMiles TestNet and MainNet). You will notice that the results page is customized for this particular DApp. Mpore specifically there is a link in the search engine results which allows an end-user to participate in the DApp. The endpoint is located in the `var playUrl` variable, which is in the [secondStateJS.js file](../js/secondStateJS.js).

If you would like assistance in uniquely customizing this search engine for your own DApp, please [contact us](https://www.secondstate.io/)

### Smart Contract Data

Every individually designed smart contract is bound to have unique data and functions. Thankfully, this search engine can dynamically call all of the public/view functions and in turn read all of the public variables. All that is required to dynamically read the smart contract variables and public functions is a link to the raw ABI.

The raw ABI url must be added to the smartContract, abi section of the [config.ini file](../python/config.ini)

```
[smartContract]
abi="https://raw.githubusercontent.com/CyberMiles/smart_contracts/master/FairPlay/v1/dapp/FairPlay.abi"
```

### Blockchain endpoint

This search engine requires a link to the blockchain RPC endpoint. This can be a local full node or a remote RPC endpoint. Below is an example of an RPC endpoint in the blockchain section of the [config.ini file](../python/config.ini).
```
[blockchain]
rpc="https://testnet-rpc.cybermiles.io:8545"
```

### Elasticsearch endpoint

At present this endpoint is required in two places (Javascript and Python files).

#### Elasticsearch endpoint - Python

Please go ahead and paste your Elasticsearch endpoint URL into the elasticSearch, endpoint section of the [config.ini file](../python/config.ini). 

**Notice** that this is just the base domain URL (no protocol and no path or query string etc.)

```
[elasticSearch]
index=fairplay
endpoint="search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com"
```
#### Elasticsearch index name - Python

Please go ahead and type the name of your Elasticsearch index into the elasticSearch, index section of the [config.ini file](../python/config.ini). **Please note** that the index name must be lowercase (Elasticsearch requirement)

#### Elasticsearch endpoint - Javascript

Please go ahead and enter your Elasticsearch endpoint URL in the `var elasticSearchUrl` variable which is located in the [secondStateJS.js file](../js/secondStateJS.js).

**Notice** that this URL contains the protocol, base domain URL, index name and a query string.

```
var elasticSearchUrl = "https://search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com/fairplay/_search/?size=100"
```

#### Elasticsearch index name - Javascript

**Notice** As mentioned directly above, the index name is entered as part of the elasticSearchUrl string.

# Harvesting / Indexing

Once you have downloaded this project and configured the above URLs it will be time to harvest the blockchain (populate the search engine). The harvesting process is automated using Cron (in combination with Python 3.6 scripts). Please see the [harvesting documentation](./harvesting.md) section for more assistance.

