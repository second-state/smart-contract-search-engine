// CONFIG START
// STATIC
//
// Local single user vs global multiuser
//var publicIp = ""; // This must be an empty string, unless you are hosting this on a public server
var publicIp = "https://ethereum-classic.search.secondstate.io"; // If you are hosting this on a public server, this must be the IP address or Base Domain (including the protocol i.e. http://mysite.com or http://123.456.7.8)

// Check blockchain network and accounts
// This is used to confirm that the user"s chrome extension is set to the correct network i.e. testnet/mainnet The search engine will only ever be deployed for a single blockchain network
var searchEngineNetwork = "1";

var currentNetwork = "";
var currentAccount = "";

// DYNAMIC
// Set up endpoints based on the above config
var esIndexName = "";
var blockExplorer = "";

if (searchEngineNetwork == "1") {
    blockExplorer = "https://gastracker.io/";
    esIndexName = "ethclassiccommonindex";
}

//var elasticSearchUrl = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/" + esIndexName + "/_search/?size=100";
var elasticSearchUrl = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/" + esIndexName + "/_search";
// CONFIG END

// CODE START
// Check network
function checkNetwork() {
    if (this.searchEngineNetwork != this.currentNetwork) {
        alert("Please download \nhttps://metamask.io/ \nand/or\n select the correct network in your correctly installed MetaMask Chrome extension!");
    }
}

$(document).ready(function() {
    
    var contracts = "";
    var contractsWithAbis = "";

    $(".overview").empty();

    var overviewRow = jQuery("<div/>", {
        class: "row",
    });
    overviewRow.appendTo(".overview");

    var overviewDetails = jQuery("<div/>", {
        class: "col-sm-12"
    });
    overviewDetails.appendTo(overviewRow);

    var overviewText = jQuery("<div/>", {
        text: "This demonstration, of the Ethereum Classic has:",
        class: "centeredText",
    });
    overviewText.appendTo(overviewDetails);

    var dlOverview = jQuery("<dl/>", {});
    dlOverview.appendTo(overviewDetails);

    $.ajax({
        url: publicIp + "/api/es_get_abi_count",
        type: "post",
        //data: {},
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            abiAmount = response["hits"]["total"];
            console.log("Fetched contract amount: " + abiAmount);
            abis = jQuery("<dt/>", {
                text: " - " + abiAmount.toLocaleString() + " unique ABIs uploaded",
                class: "centeredText",
            });
            abis.appendTo(dlOverview);
        },
        error: function(xhr) {
            console.log("Get amount failed");
        }
    });


    $.ajax({
        url: publicIp + "/api/es_get_all_count",
        type: "post",
        //data: {},
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            contractAmount = response["hits"]["total"];
            console.log("Fetched contract amount: " + contractAmount);
            contracts = jQuery("<dt/>", {
                text: " - " + contractAmount.toLocaleString() + " contracts indexed",
                class: "centeredText",
            });
            contracts.appendTo(dlOverview);
        },
        error: function(xhr) {
            console.log("Get amount failed");
        }
    });

    $.ajax({
        url: publicIp + "/api/es_get_contract_count",
        type: "post",
        //data: {},
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            contractsWithAbisAmount = response["hits"]["total"];
            console.log("Fetched contracts with ABI amount: " + contractsWithAbisAmount);
            contractsWithAbis = jQuery("<dt/>", {
                text: " - " + contractsWithAbisAmount.toLocaleString() + " contracts which adhere to ABIs",
                class: "centeredText",
            });
            contractsWithAbis.appendTo(dlOverview);
        },
        error: function(xhr) {
            console.log("Get amount failed");
        }
    });

});


$(document).ready(function() {
    window.addEventListener("load", function() {
        if (typeof web3 !== "undefined") {
            web3 = new Web3(web3.currentProvider);
            console.log("Connected to web3 - Success!")
            web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            web3.version.getNetwork((err, theNetwork) => {
                this.currentNetwork = theNetwork
            });
        } else {
            // set the provider you want from Web3.providers
            console.log("Was unable to connect to web3. Trying localhost ...")
            web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
        }
    })
});

$(document).ready(function() {
    $("#ICreated").click(function() {
        async function setUpAndProgress() {
            var originalState = $("#pb.progress-bar").clone();
            $("#pbc").show()
            $("#collapseAdvancedSearch").removeClass("show");
            this.currentAccount = "";
            $(".results").empty();
            $("#pb.progress-bar").attr("style", "width:25%");
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr("style", "width:100%");
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            checkNetwork();
            var dFunctionDataOwner = {};
            dFunctionDataOwner["functionData.owner"] = this.currentAccount;
            var dMatchFunctionDataOwner = {};
            dMatchFunctionDataOwner["match"] = dFunctionDataOwner;
            var dMust = {};
            dMust["must"] = dMatchFunctionDataOwner;
            var dBool = {};
            dBool["bool"] = dMust;
            var dQuery = {};
            dQuery["query"] = dBool;
            $("#pbc").hide("slow");
            var jsonString = JSON.stringify(dQuery);
            // If this is a public website then we need to call ES using Flask
            if (publicIp) {
                var itemArray = getItemsUsingDataViaFlask(jsonString);
            } else {
                var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            }

            $("#pb.progress-bar").replaceWith(originalState.clone());
        }
        setUpAndProgress();
    });
});

$(document).ready(function() {
    $("#IParticipated").click(function() {
        async function setUpAndProgress() {
            var originalState = $("#pb.progress-bar").clone();
            $("#pbc").show()
            $("#collapseAdvancedSearch").removeClass("show");
            this.currentAccount = "";
            $(".results").empty();
            $("#pb.progress-bar").attr("style", "width:25%");
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr("style", "width:100%");
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            checkNetwork();
            lShould = [];
            for (i = 0; i < 50; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = "functionData.player_addrs." + i;
                dPTemp[fString] = this.currentAccount;
                dPTemp2["match"] = dPTemp;
                lShould.push(dPTemp2);
            }
            var dMust = {};
            dMust["should"] = lShould;
            var dBool = {};
            dBool["bool"] = dMust;
            var dQuery = {};
            dQuery["query"] = dBool;
            $("#pbc").hide("slow");
            var jsonString = JSON.stringify(dQuery);

            // If this is a public website then we need to call ES using Flask
            if (publicIp) {
                var itemArray = getItemsUsingDataViaFlask(jsonString);
            } else {
                var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            }

            $("#pb.progress-bar").replaceWith(originalState.clone());
        }
        setUpAndProgress();
    });
});

$(document).ready(function() {
    $("#IWon").click(function() {
        async function setUpAndProgress() {
            var originalState = $("#pb.progress-bar").clone();
            $("#pbc").show()
            $("#collapseAdvancedSearch").removeClass("show");
            this.currentAccount = "";
            $(".results").empty();
            $("#pb.progress-bar").attr("style", "width:25%");
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr("style", "width:100%");
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            checkNetwork();
            lShould = [];
            for (i = 0; i < 50; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = "functionData.winner_addrs." + i;
                dPTemp[fString] = this.currentAccount;
                dPTemp2["match"] = dPTemp;
                lShould.push(dPTemp2);
            }
            var dMust = {};
            dMust["should"] = lShould;
            var dBool = {};
            dBool["bool"] = dMust;
            var dQuery = {};
            dQuery["query"] = dBool;
            $("#pbc").hide("slow");
            var jsonString = JSON.stringify(dQuery);
            // If this is a public website then we need to call ES using Flask
            if (publicIp) {
                var itemArray = getItemsUsingDataViaFlask(jsonString);
            } else {
                var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            }

            $("#pb.progress-bar").replaceWith(originalState.clone());
        }
        setUpAndProgress();
    });
});

$(document).ready(function() {
    $("#searchTextButton").click(function() {
        $(".results").empty()
        var theText = $("#searchTextInput").val();
        if ($.trim(theText.length) > "0") {
            iQuery = {};
            iQuery["query"] = theText;
            iQueryString = {};
            iQueryString["query_string"] = iQuery;
            oQuery = {};
            oQuery["query"] = iQueryString;
            jsonString = JSON.stringify(oQuery);
            getItemsUsingDataViaFlask(jsonString);
        } else {
            getQuickItemsViaFlask(elasticSearchUrl);
        }
    });
});

$(document).ready(function() {
    $("#searchAddressButton").click(function() {
        $(".results").empty()
        var theAddress = $("#searchAddressInput").val();
        if ($.trim(theAddress.length) > "0") {
            query = '{"query":{"bool":{"must":[{"match":{"contractAddress":"' + theAddress + '"}}]}}}';
            getItemsUsingDataViaFlask(query);
        } else {
            getQuickItemsViaFlask(elasticSearchUrl);
        }
    });
});

$(document).ready(function() {
    $("#searchABIButton").click(function() {
        console.log("Searching using an ABI");
        var theAbi = $("#abiInput2").val();
        console.log(theAbi);
        if ($.trim(theAbi.length) > "0") {
            esss.shaAbi(theAbi).then((shaResult) => {
                var sha = JSON.parse(shaResult).abiSha3;
                console.log(sha);
                esss.searchUsingAbi(sha).then((searchResult) => {
                    console.log(searchResult);
                    var items = JSON.parse(searchResult);
                    renderItems(items);
                });
            });
        } else {
            console.log("Error searching with ABI");
        }
    });
});



$(document).ready(function() {
    $("#indexContractButton").click(function() {
        $(".results").empty()
        var abiLoadUrl = publicIp + "/api/submit_abi";
        var theAbi = $("#abiInput").val();
        var theHash = $("#hashInput").val();
        console.log(theAbi)
        console.log(theHash)
        var hashLength = $.trim(theHash.length)
        if (hashLength == 66) {
            data = {};
            data["abi"] = theAbi;
            data["hash"] = theHash;
            dataString = JSON.stringify(data);
            $.ajax({
                url: abiLoadUrl,
                type: "POST",
                data: dataString,
                dataType: "json",
                contentType: "application/json",
                success: function(response) {
                    console.log(response);
                    $(".abi").empty();
                    var row = jQuery("<div/>", {
                        class: "row",
                    });
                    row.appendTo(".abi");

                    var details = jQuery("<div/>", {
                        class: "col-sm-12",
                        text: "Congratulations, we have indexed the smart contract and its assocated ABI!",
                    });
                    details.appendTo(row);
                },
                error: function(xhr) {
                    console.log("Index failed");
                }
            });
            //Index using Transaction Hash
        } else {
            if (hashLength == 42) {
                console.log("We can upload the ABI and your contract will appear after some time")
                console.log("If you use a transaction hash (instead of an address) your contract will be permanently indexed in real time.")
                //Index using Address
            }
        }

    });
});


function shaAnAbi(_data) {
    theUrlForData1 = publicIp + "/api/sha_an_abi";
    console.log("shaAnAbi");
    console.log(theUrlForData1);
    console.log(_data);
    _jsonData = {};
    _jsonData["abi"] = _data;
    var _dataString = JSON.stringify(_jsonData);
    $.ajax({
        url: theUrlForData1,
        type: "POST",
        data: _dataString,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            console.log(response);
            return response;
        },
        error: function(xhr) {
            console.log("Sha ABI failed");
        }
    });
}

function renderContractVariables(_result) {
    $(".results").empty();
    var row = jQuery("<div/>", {
        class: "row",
    });
    row.appendTo(".results");

    var details = jQuery("<div/>", {
        class: "col-sm-12",
        text: _result,
    });
    details.appendTo(row);
}

function getItemsUsingData(_url, _type, _data, _dataType, _contentType) {
    $.ajax({
        url: _url,
        type: _type,
        data: _data,
        dataType: _dataType,
        contentType: _contentType,
        success: function(response) {
            renderItems(response.hits.hits);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });
}

function getItemsUsingDataViaFlask(_data) {
    theUrlForData1 = publicIp + "/api/es_search";
    console.log("getItemsUsingDataViaFlask");
    console.log(theUrlForData1);
    console.log(_data);
    $.ajax({
        url: theUrlForData1,
        type: "POST",
        data: _data,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            //console.log(response);
            renderItems(response);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });
}

function getItemsUsingAddressViaFlask(_data) {
    theUrlForData1 = publicIp + "/api/describe_using_address";
    console.log("getItemsUsingAddressViaFlask");
    console.log(theUrlForData1);
    console.log(_data);
    $.ajax({
        url: theUrlForData1,
        type: "POST",
        data: _data,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            //console.log(response);
            renderItems(response);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });
}

function getItems(_url) {
    $.get(_url, function(data, status) {
        //console.log(data.hits.hits);
        renderItems(data.hits.hits);
    });
}

function getQuickItemsViaFlask() {
    theUrlForData2 = publicIp + "/api/es_quick_100_search";
    _data = {
        "query": {
            "match_all": {}
        }
    };
    var _dataString = JSON.stringify(_data);
    $.ajax({
        url: theUrlForData2,
        type: "POST",
        data: _dataString,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            //console.log(response)
            renderItems(response);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });

}

function getItemsViaFlask() {
    theUrlForData2 = publicIp + "/api/es_search";
    console.log("getItemsViaFlask");
    console.log(theUrlForData2);
    console.log("POST");
    _data = {
        "query": {
            "match_all": {}
        }
    };
    var _dataString = JSON.stringify(_data);
    $.ajax({
        url: theUrlForData2,
        type: "POST",
        data: _dataString,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            //console.log(response)
            renderItems(response);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });

}



function renderItems(_hits) {
    $(".results").empty();
    $.each(_hits, function(index, value) {

        var row = jQuery("<div/>", {
            class: "row",
        });
        row.appendTo(".results");

        var details = jQuery("<div/>", {
            class: "col-sm-12"
        });
        details.appendTo(row);

        var dl = jQuery("<dl/>", {});
        dl.appendTo(details);

        var address = jQuery("<dt/>", {
            text: "Address: " + value.contractAddress
        });
        address.appendTo(dl);

        var block = jQuery("<dt/>", {
            text: "Block: " + value.blockNumber
        });
        block.appendTo(dl);

        var transaction = jQuery("<dt/>", {
            text: "Transaction: " + value.TxHash
        });
        transaction.appendTo(dl);

        var creator = jQuery("<dt/>", {
            text: "Creator: " + value.creator
        });
        creator.appendTo(dl);

        var lineBreak = jQuery("<hr/>", {});
        lineBreak.appendTo(".results");

        var shaList = value.abiShaList;
        if (shaList.includes("0x2b5710e2cf7eb7c9bd50bfac8e89070bdfed6eb58f0c26915f034595e5443286")) {
            var type = jQuery("<dt/>", {
                text: "Type: ERC20"
            });
            type.appendTo(dl);

            var name = jQuery("<dt/>", {
                text: "ERC20 Name: " + value.functionData.name
            });
            name.appendTo(dl);

            var symbol = jQuery("<dt/>", {
                text: "ERC20 Symbol: " + value.functionData.symbol
            });
            symbol.appendTo(dl);

            var supply = jQuery("<dt/>", {
                text: "ERC20 Supply: " + value.functionData.totalSupply
            });
            supply.appendTo(dl);

            var decimals = jQuery("<dt/>", {
                text: "ERC20 Decimals: " + value.functionData.decimals
            });
            decimals.appendTo(dl);

        } else {
            $.each(value.functionData, function(key, value) {
                var theUnknownData = jQuery("<dt/>", {
                    text: key + ": " + value
                });
                theUnknownData.appendTo(dl);
            });
        }

        var breaker = jQuery("<br />", {});
        breaker.appendTo(dl);

        if (shaList.includes("0x2b5710e2cf7eb7c9bd50bfac8e89070bdfed6eb58f0c26915f034595e5443286") || shaList.includes("0x7f63f9caca226af6ac1e87fee18b638da04cfbb980f202e8f17855a6d4617a69")) {
            var etherscan = jQuery("<dd/>", {

            });

            var etherscanUrl = "https://gastracker.io/addr/" + value.contractAddress;
            var etherscanButton = jQuery("<a/>", {
                href: etherscanUrl,
                class: "btn btn-primary btn-sm",
                role: "button",
                target: "_blank",
                text: "View on GasTracker.io"
            });
            etherscanButton.appendTo(etherscan);
            etherscan.appendTo(dl);
        }

    });
}

class ESSS {
    // Search Engine Base URL (Please include protocol. Please do not include trailing slash)
    // Example: https://search-engine.com
    constructor(_searchEngineBaseUrl) {
        this.searchEngineBaseUrl = _searchEngineBaseUrl;
        console.log("Search Engine Base URL set to: " + this.searchEngineBaseUrl);
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

var esss = new ESSS("https://ethereum-classic.search.secondstate.io");

/*

esss.shaAbi(JSON.stringify(abi)).then((shaResult) => {
    var sha = JSON.parse(shaResult).abiSha3;
    esss.searchUsingAbi(sha).then((searchResult) => {
        var items = JSON.parse(searchResult);

    });
});

*/
