var publicIp = "https://testnet.cmt.search.secondstate.io";

class ESSS {
    // Search Engine Base URL (Please include protocol. Please do not include trailing slash)
    // Example: https://search-engine.com
    constructor(_searchEngineBaseUrl) {
        this.searchEngineBaseUrl = _searchEngineBaseUrl;
        console.log("Search Engine Base URL set to: " + this.searchEngineBaseUrl);
        this.indexStatus = {};
    }

    setIndexStatusToTrue(_transactionHash) {
        this.indexStatus[_transactionHash] = true;
    }

    setIndexStatusToFalse(_transactionHash) {
        this.indexStatus[_transactionHash] = false;
    }

    getIndexStatus(_transactionHash) {
        return this.indexStatus[_transactionHash];
    }

    queryAccessLogsUsingDsl(_query) {
        var url = this.searchEngineBaseUrl + "/api/es_access_search";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(_query));
        });
    }

    queryTxUsingDsl(_query) {
        var url = this.searchEngineBaseUrl + "/api/es_tx_search";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(_query));
        });
    }

    queryUsingDsl(_query) {
        var url = this.searchEngineBaseUrl + "/api/es_search";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(_query));
        });
    }

    expressHarvestAnAbi(_abiHash, _blockFloor) {
        var url = this.searchEngineBaseUrl + "/api/express_harvest_an_abi";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["abiHash"] = _abiHash;
            data["blockFloor"] = _blockFloor;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(data));
        });
    }

    updateStateOfContractAddress(_abi, _address) {
        var url = this.searchEngineBaseUrl + "/api/update_state_of_contract_address";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["abi"] = _abi;
            data["address"] = _address;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(data));
        });
    }

    updateQualityScore(_contractAddress, _qualityScore) {
        var url = this.searchEngineBaseUrl + "/api/es_update_quality";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["contractAddress"] = _contractAddress;
            data["qualityScore"] = _qualityScore;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify(data));
        });
    }

    getMostRecentIndexedBlockNumber() {
        var url = this.searchEngineBaseUrl + "/api/most_recent_indexed_block_number";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();

            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var blockNumber = jsonResponse["aggregations"]["most_recent_block"]["value"]
                        resolve(blockNumber);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify());
        });
    }

    getBlockInterval() {
        var url = this.searchEngineBaseUrl + "/api/get_block_interval";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify());
        });
    }

    getAbiCount() {
        var url = this.searchEngineBaseUrl + "/api/es_get_abi_count";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var abiCount = jsonResponse["hits"]["total"]
                        resolve(abiCount);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify());
        });
    }

    getAllCount() {
        var url = this.searchEngineBaseUrl + "/api/es_get_all_count";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var allCount = jsonResponse["hits"]["total"]
                        resolve(allCount);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify());
        });
    }


    getContractCount() {
        var url = this.searchEngineBaseUrl + "/api/es_get_contract_count";
        return new Promise(function(resolve, reject) {

            var xhr = new XMLHttpRequest();

            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var allCount = jsonResponse["hits"]["total"]
                        resolve(allCount);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.send(JSON.stringify());
        });
    }

    confirmDeployment(_transactionHash) {
        let url = this.searchEngineBaseUrl + "/api/confirm_deployment";
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["hash"] = _transactionHash;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }

    describeUsingTx(_transactionHash) {
        let url = this.searchEngineBaseUrl + "/api/describe_using_tx";
        return new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["hash"] = _transactionHash;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var allRecord = JSON.stringify(jsonResponse["hits"]["hits"][0]["_source"]);
                        resolve(allRecord);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }

    submitAbi(_abi, _transactionHash) {
        var url = this.searchEngineBaseUrl + "/api/submit_abi";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["abi"] = _abi;
            data["hash"] = _transactionHash;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }

    submitManyAbis(_abis, _transactionHash) {
        var url = this.searchEngineBaseUrl + "/api/submit_many_abis";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = {};
            data["abis"] = _abis;
            data["hash"] = _transactionHash;
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }


    shaAbi(_abi) {
        var url = this.searchEngineBaseUrl + "/api/sha_an_abi";
        return new Promise(function(resolve, reject) {
            //data
            var data = {};
            data["abi"] = _abi;
            var xhr = new XMLHttpRequest();

            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }

    sortAbi(_abi) {
        var url = this.searchEngineBaseUrl + "/api/sort_an_abi";
        return new Promise(function(resolve, reject) {
            //data
            var data = {};
            data["abi"] = _abi;
            var xhr = new XMLHttpRequest();

            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(data));
        });
    }

    searchUsingAddress(_address) {
        var url = this.searchEngineBaseUrl + "/api/es_search";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = '{"query":{"bool":{"must":[{"match":{"contractAddress":"' + _address + '"}}]}}}'
            //execution
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var jsonResponse = JSON.parse(xhr.responseText);
                        var allRecord = JSON.stringify(jsonResponse[0]);
                        resolve(allRecord);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(data);
        });
    }

    searchUsingAbi(_abiHash) {
        var url = this.searchEngineBaseUrl + "/api/es_search";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var data = '{"query":{"bool":{"must":[{"match":{"abiShaList":"' + _abiHash + '"}}]}}}'
            //execution
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(data);
        });
    }

    searchUsingKeywords(_keywords) {
        var url = this.searchEngineBaseUrl + "/api/es_search";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var listOfKeywords = _keywords["keywords"];
            var string = "";
            var i;
            for (i = 0; i < listOfKeywords.length; i++) {
                if (string.length == 0) {
                    string = string + '"' + listOfKeywords[i];
                } else {
                    string = string + "," + listOfKeywords[i];
                }
            }
            string = string + '"'
            var data = '{"query":{"query_string":{"query":' + string + '}}}';
            console.log(data);
            //execution
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(JSON.parse(data)));
        });
    }

    searchUsingKeywordsAndAbi(_abiHash, _keywords) {
        var url = this.searchEngineBaseUrl + "/api/es_search";
        return new Promise(function(resolve, reject) {
            // request initialisation
            var xhr = new XMLHttpRequest();

            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            //data
            var listOfKeywords = _keywords["keywords"];
            var string = "";
            var i;
            for (i = 0; i < listOfKeywords.length; i++) {
                if (string.length == 0) {
                    string = string + '"' + listOfKeywords[i];
                } else {
                    string = string + "," + listOfKeywords[i];
                }
            }
            string = string + '"'
            var data = '{"query":{"bool":{"must":[{"match":{"abiShaList":"' + _abiHash + '"}},{"query_string":{"query":' + string + '}}]}}}';
            console.log(data);
            //execution
            xhr.onload = function(e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        resolve(xhr.responseText);
                    }
                }
            };
            xhr.onerror = reject;
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify(JSON.parse(data)));
        });
    }
}

var esss = new ESSS(publicIp);

$(document).ready(function() {
    var now = Math.floor(Date.now() / 1000)
    var week = Math.floor((Date.now() - (7 * 24 * 60 * 60 * 1000)) / 1000)
    var q = {
        "query": {
            "bool": {
                "must": [{
                        "match": {
                            "responseStatus": "200"
                        }
                    },
                    {
                        "range": {
                            "timestamp": {
                                "gte": week,
                                "lt": now
                            }
                        }
                    }
                ]
            }
        }
    }
    esss.queryAccessLogsUsingDsl(q)
        .then(function(result) {
            var uniqueList = []
            var a = JSON.parse(result);
            for (i = 0; i < a.length; i++) {
                if (uniqueList.indexOf(a[i]["_source"]["callingIp"]) == -1) {
                    uniqueList.push(a[i]["_source"]["callingIp"])
                }
            }
            var g = new JustGage({
                id: "uniqueVisitorsThisWeek",
                value: uniqueList.length,
                min: 0,
                max: Math.floor((uniqueList.length / 3) * 4),
                title: "Unique Visitors (this week)"
            });
            console.log("Unique IP Addresses: " + uniqueList.length);
        })
        .catch(function() {
            console.log("Error");
        });
});

$(document).ready(function() {
    var now = Math.floor(Date.now() / 1000)
    var week = Math.floor((Date.now() - (7 * 24 * 60 * 60 * 1000)) / 1000)
    var q2 = {
        "_source": "uniqueHash"
    }
    esss.queryAccessLogsUsingDsl(q2)
        .then(function(result) {
            var uniqueList2 = []
            var a = JSON.parse(result);
            for (i = 0; i < a.length; i++) {
                if (uniqueList2.indexOf(a[i]["_source"]["uniqueHash"]) == -1) {
                    uniqueList2.push(a[i]["_source"]["uniqueHash"])
                }
            }
            var g = new JustGage({
                id: "totalHits",
                value: uniqueList2.length,
                min: 0,
                max: Math.floor((uniqueList2.length / 3) * 4),
                title: "Total Hits (to date)"
            });
            console.log("Total hits: " + uniqueList2.length);
        })
        .catch(function() {
            console.log("Error");
        });
});

$(document).ready(function() {
    var now = Math.floor(Date.now() / 1000)
    var week = Math.floor((Date.now() - (7 * 24 * 60 * 60 * 1000)) / 1000)
    var q3 = {
        "_source": "callingIp"
    }
    esss.queryAccessLogsUsingDsl(q3)
        .then(function(result) {
            var uniqueList3 = []
            var a = JSON.parse(result);
            for (i = 0; i < a.length; i++) {
                if (uniqueList3.indexOf(a[i]["_source"]["callingIp"]) == -1) {
                    uniqueList3.push(a[i]["_source"]["callingIp"])
                }
            }
            var g = new JustGage({
                id: "uniqueVisitors",
                value: uniqueList3.length,
                min: 0,
                max: Math.floor((uniqueList3.length / 3) * 4),
                title: "Unique Visitors (to date)"
            });
            console.log("Unique visitors: " + uniqueList3.length);
        })
        .catch(function() {
            console.log("Error");
        });
});

$(document).ready(function() {
    esss.getAbiCount()
        .then(function(result) {
            var g = new JustGage({
                id: "gaugeAbisUploaded",
                value: result,
                min: 0,
                max: Math.floor((result / 3) * 4),
                title: "Unique ABIs uploaded"
            });
            console.log("Unique ABIs uploaded: " + result);
        })
        .catch(function() {
            console.log("Error");
        });
});

$(document).ready(function() {
    esss.getAllCount()
        .then(function(result) {
            var g = new JustGage({
                id: "gaugeContractsIndexed",
                value: result,
                min: 0,
                max: Math.floor((result / 3) * 4),
                title: "Contracts indexed"
            });
            console.log("Contracts indexed: " + result);
        })
        .catch(function() {
            console.log("Error");
        });
});

$(document).ready(function() {
    esss.getAllCount()
        .then(function(resultAll) {
            esss.getContractCount()
                .then(function(result) {
                    var g = new JustGage({
                        id: "gaugeContractsThatAdhereToAbis",
                        value: result,
                        min: 0,
                        max: resultAll,
                        title: "Contracts adhering to ABIs"
                    });
                    console.log("Contracts adhering to ABIs: " + result);
                })
                .catch(function() {
                    console.log("Error");
                });
        })
        .catch(function() {
            console.log("Error");
        });
});