// CONFIG START
// STATIC
//
// Local single user vs global multiuser
//var publicIp = ""; // This must be an empty string, unless you are hosting this on a public server
var publicIp = "https://ethereum.search.secondstate.io"; // If you are hosting this on a public server, this must be the IP address or Base Domain (including the protocol i.e. http://mysite.com or http://123.456.7.8)

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
    blockExplorer = "https://etherscan.io/";
    esIndexName = "ercchecker";
}

var elasticSearchUrl = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/" + esIndexName + "/_search/?size=100";
var elasticSearchUrl = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/" + esIndexName + "/_search/?size=100";
// CONFIG END

// CODE START
// Check network
function checkNetwork() {
    if (this.searchEngineNetwork != this.currentNetwork) {
        alert("Please download \nhttps://metamask.io/ \nand/or\n select the correct network in your correctly installed MetaMask Chrome extension!");
    }
}

$(document).ready(function() {
    contractsQuery = JSON.stringify({"query":{"match_all" :{}},"size":0})
    var master = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/allercchecker/_search";
    var common = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/ercchecker/_search";
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
        text: "This demonstration, of the Ethereum MainNet has:",
        class: "centeredText",
    });
    overviewText.appendTo(overviewDetails);

    var dlOverview = jQuery("<dl/>", {});
    dlOverview.appendTo(overviewDetails);


    $.ajax({
        url: master,
        type: "post",
        data: contractsQuery,
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
        url: common,
        type: "post",
        data: contractsQuery,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            contractsWithAbisAmount = response["hits"]["total"];
            console.log("Fetched contracts with ABI amount: " + contractsWithAbisAmount);
            contractsWithAbis = jQuery("<dt/>", {
                text: " - " + contractsWithAbisAmount.toLocaleString() + " contracts with supporting ABIs",
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
    $("#searchAddressButton").click(function() {
        $(".results").empty()
        getItemsViaFlask(elasticSearchUrl);
    });
});

$(document).ready(function() {
    $("#indexContractButton").click(function() {
        $(".results").empty()
        var abiLoadUrl = publicIp + "/api/submit_abi";
        var theAbi = $("#abiInput").val();
        var theHash = $("#hashInput").val();
        var hashLength = $.trim(theHash.length)
        if (hashLength == 66){
            data = {};
            data["abi"] = theAbi;
            data["hash"] = theHash;
            $.ajax({
                url: abiLoadUrl,
                type: "POST",
                data: data,
                dataType: "json",
                contentType: "application/json",
                success: function(response) {
                    console.log(response);
                    renderContractVariables(response)
                },
                error: function(xhr) {
                    console.log("Index failed");
                }
            });
            //Index using Transaction Hash
        }
        else{
            if(hashLength == 42){
                console.log("We can upload the ABI and your contract will appear after some time")
                console.log("If you use a transaction hash (instead of an address) your contract will be permanently indexed in real time.")
                //Index using Address
            }
        }

    });
});

function renderContractVariables(_result){
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
            console.log(response);
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

function getItemsViaFlask() {
    theUrlForData2 = publicIp + "/api/es_search";
    console.log("getItemsViaFlask");
    console.log(theUrlForData2);
    console.log("POST");
    _data = {"query":{"match_all":{}},"size":25}
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
        if (shaList.includes("0x2b5710e2cf7eb7c9bd50bfac8e89070bdfed6eb58f0c26915f034595e5443286")){
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
        }
        console.log(value);
    });
}

// CODE END
