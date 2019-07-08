// CONFIG START
// STATIC
//
// Local single user vs global multiuser
//var publicIp = ""; // This must be an empty string, unless you are hosting this on a public server
var publicIp = "https://cmt-testnet.search.secondstate.io"; // If you are hosting this on a public server, this must be the IP address or Base Domain (including the protocol i.e. http://mysite.com or http://123.456.7.8)

// Check blockchain network and accounts
// This is used to confirm that the user"s chrome extension is set to the correct network i.e. testnet/mainnet The search engine will only ever be deployed for a single blockchain network
var searchEngineNetwork = "19"; // CyberMiles TestNet
//var searchEngineNetwork = "18"; // CyberMiles MainNet


var currentNetwork = "";
var currentAccount = "";

// DYNAMIC
// Set up endpoints based on the above config
var esIndexName = "";
var blockExplorer = "";

if (searchEngineNetwork == "19") {
    blockExplorer = "https://testnet.cmttracking.io/";
    esIndexName = "testnetv2";
}

if (searchEngineNetwork == "18") {
    blockExplorer = "https://www.cmttracking.io/";
    esIndexName = "cmtmainnetmultiabi";
}

var elasticSearchUrl = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/" + esIndexName + "/_search/?size=100";
// CONFIG END

// CODE START
// Check network
function checkNetwork() {
    if (this.searchEngineNetwork != this.currentNetwork) {
        alert("Please select the correct network in your Venus Chrome extension!");
    }
}

$(document).ready(function() {
    contractsQuery = JSON.stringify({
        "query": {
            "match_all": {}
        },
        "size": 0
    })
    var abi = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/abitestnetv2/_search";
    var master = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/alltestnetv2/_search";
    var common = "https://search-cmtsearch-l72er2gp2gxdwazqb5wcs6tskq.ap-southeast-2.es.amazonaws.com/testnetv2/_search";
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
        text: "This demonstration, of the CyberMiles TestNet has:",
        class: "centeredText",
    });
    overviewText.appendTo(overviewDetails);

    var dlOverview = jQuery("<dl/>", {});
    dlOverview.appendTo(overviewDetails);

    $.ajax({
        url: abi,
        type: "post",
        data: contractsQuery,
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
            dFunctionDataOwner["functionDataList.0.functionData.owner"] = this.currentAccount;
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
            dQuery = '{"query":{"query_string":{"fields":["functionDataList.0.functionData.player_addrs.*"],"query":"' + this.currentAccount + '"}}}'
            $("#pbc").hide("slow");
            var jsonString = dQuery;
            console.log(jsonString)

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
            dQuery = '{"query":{"query_string":{"fields":["functionDataList.0.functionData.winner_addrs.*"],"query":"' + this.currentAccount + '"}}}'
            $("#pbc").hide("slow");
            var jsonString = dQuery;
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
        var theText = $("#searchTextInput").val();
        if ($.trim(theText.length) == "0") {
            //console.log("Address and text are both blank, fetching all results without a filter");
            if (publicIp) {
                getItemsViaFlask(elasticSearchUrl);
            } else {
                getItems(elasticSearchUrl);
            }
        } else if ($.trim(theText.length) > "0") {
            var jsonString = '{"query":{"multi_match":{"fields":["functionDataList.0.functionData.info.1","functionDataList.0.functionData.info.2"],"query":"' + theText + '"}}}'
            if (publicIp) {
                var itemArray = getItemsUsingDataViaFlask(jsonString);
            } else {
                var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            }
        }

    });
});

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
    _data = {
        "query": {
                "match_all": {}
        }
    }
    var _dataString = JSON.stringify(_data);
    $.ajax({
        url: theUrlForData2,
        type: "POST",
        data: _dataString,
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
            renderItems(response);
        },
        error: function(xhr) {
            console.log("Get items failed");
        }
    });

}

function renderItems(_hits) {
    console.log(_hits)
    $(".results").empty();
    $.each(_hits, function(index, value) {

        var row = jQuery("<div/>", {
            class: "row",
        });
        row.appendTo(".results");

        var imageContainer = jQuery("<div/>", {
            class: "col-sm-4"
        });
        imageContainer.appendTo(row);

        var image = jQuery("<img/>", {
            class: "img-thumbnail",
            src: value.functionData.info[3],
            alt: "giveaway"
        });
        image.appendTo(imageContainer);

        var details = jQuery("<div/>", {
            class: "col-sm-8"
        });
        details.appendTo(row);

        var dl = jQuery("<dl/>", {});
        dl.appendTo(details);

        var title = jQuery("<dt/>", {
            text: "Title: " + value.functionData.info[1]
        });
        title.appendTo(dl);

        var description = jQuery("<dd/>", {
            text: "Description: " + value.functionData.info[2]
        });
        description.appendTo(dl);

        var winners = jQuery("<dd/>", {
            text: "Number of potential winners: " + value.functionData.info[4]
        });
        winners.appendTo(dl);

        var textStatus = "";
        if (value.functionData.status == "0") {
            textStatus = "Winners have not been declared as yet";
            var status = jQuery("<dd/>", {
                text: textStatus,
                // Optional color change?
                // class: "current"
            });
            status.appendTo(dl);

        } else if (value.functionData.status == "1") {
            textStatus = "Winners have been declared";
            var status = jQuery("<dd/>", {
                text: textStatus,
                // Optional color change?
                // class: "expired"
            });
            status.appendTo(dl);
        }

        // Expiry time
        var epochRepresentation = value.functionData.info[5];
        if (epochRepresentation.toString().length == 10) {
            var endDate = new Date(epochRepresentation * 1000);
        } else if (epochRepresentation.toString().length == 13) {
            var endDate = new Date(epochRepresentation);
        }

        // Setting Dapp Version
        if (value.abiShaList.includes("0xb8a37479196c0f9d8ab647141f1f22863305d3ad86c4dd88f25304c01bff0eb6")){
                dappVersion = "v1";
            }
            else if (value.abiShaList.includes("0xe49f0c6abcbe2ab8264670478d7767df62be6b264d7fc8b067e9767dacf61c99")) {
                dappVersion = "v2";
            }

        // Current time
        var currentDate = new Date();

        if (currentDate > endDate) {
            var time = jQuery("<dd/>", {
                text: "End date: " + endDate,
                class: "expired"
            });
            time.appendTo(dl);
            // Allow user to VIEW this giveaway
            var view = jQuery("<dd/>", {

            });
            
            var viewUrl = "https://cybermiles.github.io/smart_contracts/FairPlay/" + dappVersion + "/dapp/play.html?contract=" + value.contractAddress;
            var viewButton = jQuery("<a/>", {
                href: viewUrl,
                class: "btn btn-info",
                role: "button",
                target: "_blank",
                text: "View"
            });
            viewButton.appendTo(view);
            view.appendTo(dl);
        } else if (currentDate < endDate) {
            var time = jQuery("<dd/>", {
                text: "End date: " + endDate,
                class: "current"
            });
            time.appendTo(dl);
            // Allow user to play this giveaway
            var play = jQuery("<dd/>", {

            });
            var playUrl = "https://cybermiles.github.io/smart_contracts/FairPlay/" + dappVersion + "/dapp/play.html?contract=" + value.contractAddress;
            var playButton = jQuery("<a/>", {
                href: playUrl,
                class: "btn btn-success",
                role: "button",
                target: "_blank",
                text: "Play"
            });
            playButton.appendTo(play);
            play.appendTo(dl);

        }

        var version = jQuery("<dd/>", {
            text: "DApp version: " + dappVersion
        });
        version.appendTo(dl);

        //https://cybermiles.github.io/smart_contracts/FairPlay/dapp/play.html?contract=0x

        /* More details */
        var pGroup = jQuery("<div/>", {
            class: "panel-group"
        });
        pGroup.appendTo(details);

        var pDefault = jQuery("<div/>", {
            class: "panel panel-default"
        });
        pDefault.appendTo(pGroup);

        var pHeading = jQuery("<div/>", {
            class: "panel-heading"
        });
        pHeading.appendTo(pDefault);

        var pTitle = jQuery("<p/>", {
            class: "panel-title"
        });
        pTitle.appendTo(pHeading);

        var pToggle = jQuery("<a/>", {
            "data-toggle": "collapse",
            href: "#collapse1",
            text: "Show/Hide Details"
        });
        pToggle.appendTo(pTitle);

        var pCollapse = jQuery("<div/>", {
            id: "collapse1",
            class: "panel-collapse collapse"
        });
        pCollapse.appendTo(pDefault);

        var pBody = jQuery("<div/>", {
            class: "panel-body"
        });
        pBody.appendTo(pCollapse);

        var dl2 = jQuery("<dl/>", {});
        dl2.appendTo(pBody);

        var blockNumber = jQuery("<dd/>", {

        });
        blockNumber.appendTo(dl2);

        var blockNumberA = jQuery("<a/>", {
            text: "- Block " + value.blockNumber,
            href: blockExplorer + "block/" + value.blockNumber,
            target: "_blank"
        });
        blockNumberA.appendTo(blockNumber);

        if (value.TxHash !== undefined) {
            var txHash = jQuery("<dd/>", {

            });
            txHash.appendTo(dl2);

            var txHashA = jQuery("<a/>", {
                text: "- Transaction " + value.TxHash,
                href: blockExplorer + "tx/" + value.TxHash,
                target: "_blank"
            });
            txHashA.appendTo(txHash);
        }

        var cOwner = jQuery("<dd/>", {

        });
        cOwner.appendTo(dl2);

        var cOwnerA = jQuery("<a/>", {
            text: "- Contract owner " + value.functionData.owner,
            href: blockExplorer + "address/" + value.functionData.owner,
            target: "_blank"
        });
        cOwnerA.appendTo(cOwner);

        var cAddress = jQuery("<dd/>", {

        });
        cAddress.appendTo(dl2);

        var cAddressA = jQuery("<a/>", {
            text: "- Contract address " + value.contractAddress,
            href: blockExplorer + "address/" + value.contractAddress,
            target: "_blank"
        });
        cAddressA.appendTo(cAddress);

        if (value.functionData.player_addrs == undefined){
            var lineBreak = jQuery("<hr/>", {});
            lineBreak.appendTo(dl2);
            var pAddress = jQuery("<dd/>", {
                text: "Players: There are no players yet!"
            });
            pAddress.appendTo(dl2);
        } else {
            var lineBreak = jQuery("<hr/>", {});
            lineBreak.appendTo(dl2);
            $.each(value.functionData.player_addrs, function(playerIndex, playerValue) {
                var pAddress = jQuery("<dd/>", {
                    text: "Player : " + playerValue
                });
                pAddress.appendTo(dl2);
            });
        }

        if (value.functionData.winner_addrs == undefined) {
            var lineBreak = jQuery("<hr/>", {});
            lineBreak.appendTo(dl2);
            var wAddress = jQuery("<dd/>", {
                text: "Winners: There are no winners yet!"
            });
            wAddress.appendTo(dl2);
        } else {
            var lineBreak = jQuery("<hr/>", {});
            lineBreak.appendTo(dl2);
            $.each(value.functionData.winner_addrs, function(winnerIndex, winnerValue) {
                var wAddress = jQuery("<dd/>", {
                    text: "Winner : " + winnerValue
                });
                wAddress.appendTo(dl2);
            });
        }
        var lineBreak = jQuery("<hr/>", {});
        lineBreak.appendTo(".results");
    });
}
// CODE END
