// Please set the following variables

var publicIp = "http://54.66.215.89"; // This is the public IP of the global search engine server where this file is deployed
var elasticSearchUrl = "https://search-smart-contract-search-engine-cdul5cxmqop325ularygq62khi.ap-southeast-2.es.amazonaws.com/fairplay/_search/?size=100"
var currentAccount = "";


$(document).ready(function() {
    window.addEventListener('load', function() {
        if (typeof web3 !== 'undefined') {
            web3 = new Web3(web3.currentProvider);
            console.log("Connected to web3 - Success!")
            web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
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
            $('#collapseAdvancedSearch').removeClass('show');
            this.currentAccount = "";
            $('.results').empty();
            $("#pb.progress-bar").attr('style', 'width:25%');
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr('style', 'width:100%');
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            var dFunctionDataOwner = {};
            dFunctionDataOwner['functionData.owner'] = this.currentAccount;
            var dMatchFunctionDataOwner = {};
            dMatchFunctionDataOwner['match'] = dFunctionDataOwner;
            var dMust = {};
            dMust['must'] = dMatchFunctionDataOwner;
            var dBool = {};
            dBool['bool'] = dMust;
            var dQuery = {};
            dQuery['query'] = dBool;
            $("#pbc").hide('slow');
            var jsonString = JSON.stringify(dQuery);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
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
            $('#collapseAdvancedSearch').removeClass('show');
            this.currentAccount = "";
            $('.results').empty();
            $("#pb.progress-bar").attr('style', 'width:25%');
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr('style', 'width:100%');
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            lShould = [];
            for (i = 0; i < 20; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = 'functionData.player_addrs.' + i;
                dPTemp[fString] = this.currentAccount;
                dPTemp2['match'] = dPTemp;
                lShould.push(dPTemp2);
            }
            var dMust = {};
            dMust['should'] = lShould;
            var dBool = {};
            dBool['bool'] = dMust;
            var dQuery = {};
            dQuery['query'] = dBool;
            $("#pbc").hide('slow');
            var jsonString = JSON.stringify(dQuery);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
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
            $('#collapseAdvancedSearch').removeClass('show');
            this.currentAccount = "";
            $('.results').empty();
            $("#pb.progress-bar").attr('style', 'width:25%');
            await web3.eth.getAccounts((err, accounts) => {
                this.currentAccount = accounts[0]
            });
            $("#pb.progress-bar").attr('style', 'width:100%');
            await new Promise((resolve, reject) => setTimeout(resolve, 1500));
            lShould = [];
            for (i = 0; i < 20; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = 'functionData.winner_addrs.' + i;
                dPTemp[fString] = this.currentAccount;
                dPTemp2['match'] = dPTemp;
                lShould.push(dPTemp2);
            }
            var dMust = {};
            dMust['should'] = lShould;
            var dBool = {};
            dBool['bool'] = dMust;
            var dQuery = {};
            dQuery['query'] = dBool;
            $("#pbc").hide('slow');
            var jsonString = JSON.stringify(dQuery);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            $("#pb.progress-bar").replaceWith(originalState.clone());
        }
        setUpAndProgress();
    });
});

$(document).ready(function() {
    $("#searchAddressButton").click(function() {
        $('.results').empty()
        var theAddress = $("#searchAddressInput").val();
        var theText = $("#searchTextInput").val();
        //console.log($.trim(theAddress.length));
        if ($.trim(theAddress.length) == "0" && $.trim(theText.length) == "0") {
            //console.log("Address and text are both blank, fetching all results without a filter");
            getItems(elasticSearchUrl);
        } else if ($.trim(theAddress.length) == "0" && $.trim(theText.length) > "0") {
            var dFields = {};
            var dQueryInner = {};
            var dMultiMatch = {};
            var dQueryOuter = {};
            var lFields = ["functionData.title", "functionData.desc"];
            dTemp = {};
            dTemp["fields"] = lFields;
            dTemp["query"] = theText;
            dMultiMatch["multi_match"] = dTemp;
            dQueryOuter["query"] = dMultiMatch;
            var jsonString = JSON.stringify(dQueryOuter);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            //console.log(itemArray);
        } else if ($.trim(theAddress.length) > "0" && $.trim(theText.length) > "0") {
            var dDesc = {};
            dDesc['desc'] = theText;
            //console.log(dDesc);
            var dTitle = {};
            dTitle['title'] = theText;
            //console.log(dTitle);
            var dFunctionDataOwner = {};
            dFunctionDataOwner['functionData.owner'] = theAddress;
            //console.log(dFunctionDataOwner);
            var dContractAddress = {};
            dContractAddress['contractAddress'] = theAddress;
            //console.log(dContractAddress);
            var dMatchContractAddress = {};
            dMatchContractAddress['match'] = dContractAddress;
            //console.log(dMatchContractAddress);
            var dMatchFunctionDataOwner = {};
            dMatchFunctionDataOwner['match'] = dFunctionDataOwner;
            //console.log(dMatchFunctionDataOwner);
            var dMatchTitle = {};
            dMatchTitle['match'] = dTitle;
            //console.log(dMatchTitle);
            var dMatchDesc = {};
            dMatchDesc['match'] = dDesc;
            //console.log(dMatchDesc);
            var lShould = [];
            lShould.push(dMatchContractAddress);
            lShould.push(dMatchFunctionDataOwner);
            lShould.push(dMatchTitle);
            lShould.push(dMatchDesc);
            // Start - Players and Winners
            // Players
            for (i = 0; i < 20; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = 'functionData.player_addrs' + i;
                dPTemp[fString] = theAddress;
                dPTemp2['match'] = dPTemp;
                lShould.push(dPTemp2);
            }
            // Winners
            for (i = 0; i < 20; i++) {
                var dWTemp = {};
                var dWTemp2 = {};
                var fStringW = 'functionData.player_addrs' + i;
                dWTemp[fStringW] = theAddress;
                dWTemp2['match'] = dWTemp;
                lShould.push(dWTemp2);
            }
            // End - Players and Winners
            //console.log(lShould);
            var dShould = {};
            dShould['should'] = lShould;
            //console.log(dShould);
            var dBool = {};
            dBool['bool'] = dShould;
            //console.log(dBool);
            var dQuery = {};
            dQuery['query'] = dBool;
            //console.log(dQuery);
            //console.log(JSON.stringify(dQuery));
            var jsonString = JSON.stringify(dQuery);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            //console.log(itemArray);
        } else if ($.trim(theAddress.length) > "0" && $.trim(theText.length) == "0") {
            var dFunctionDataOwner = {};
            dFunctionDataOwner['functionData.owner'] = theAddress;
            //console.log(dFunctionDataOwner);
            var dContractAddress = {};
            dContractAddress['contractAddress'] = theAddress;
            //console.log(dContractAddress);
            var dMatchContractAddress = {};
            dMatchContractAddress['match'] = dContractAddress;
            //console.log(dMatchContractAddress);
            var dMatchFunctionDataOwner = {};
            dMatchFunctionDataOwner['match'] = dFunctionDataOwner;
            //console.log(dMatchFunctionDataOwner);
            var lShould = [];
            lShould.push(dMatchContractAddress);
            lShould.push(dMatchFunctionDataOwner);
            // Start - Players and Winners
            // Players
            for (i = 0; i < 20; i++) {
                var dPTemp = {};
                var dPTemp2 = {};
                var fString = 'functionData.player_addrs' + i;
                dPTemp[fString] = theAddress;
                dPTemp2['match'] = dPTemp;
                lShould.push(dPTemp2);
            }
            // Winners
            for (i = 0; i < 20; i++) {
                var dWTemp = {};
                var dWTemp2 = {};
                var fStringW = 'functionData.winner_addrs' + i;
                dWTemp[fStringW] = theAddress;
                dWTemp2['match'] = dWTemp;
                lShould.push(dWTemp2);
            }
            // End - Players and Winners
            //console.log(lShould);
            var dShould = {};
            dShould['should'] = lShould;
            //console.log(dShould);
            var dBool = {};
            dBool['bool'] = dShould;
            //console.log(dBool);
            var dQuery = {};
            dQuery['query'] = dBool;
            //console.log(dQuery);
            //console.log(JSON.stringify(dQuery));
            var jsonString = JSON.stringify(dQuery);
            var itemArray = getItemsUsingData(elasticSearchUrl, "post", jsonString, "json", "application/json");
            //console.log(itemArray);
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

function getItems(_url) {
    $.get(_url, function(data, status) {
        //console.log(data.hits.hits);
        renderItems(data.hits.hits);
    });
}

function renderItems(_hits) {
    $('.results').empty();
    $.each(_hits, function(index, value) {

        var row = jQuery('<div/>', {
            class: 'row',
        });
        row.appendTo('.results');

        var imageContainer = jQuery('<div/>', {
            class: 'col-sm-4'
        });
        imageContainer.appendTo(row);

        var image = jQuery('<img/>', {
            class: 'img-thumbnail',
            src: value._source.functionData.info[3],
            alt: 'giveaway'
        });
        image.appendTo(imageContainer);

        var details = jQuery('<div/>', {
            class: 'col-sm-8'
        });
        details.appendTo(row);

        var dl = jQuery('<dl/>', {});
        dl.appendTo(details);

        var title = jQuery('<dt/>', {
            text: "Title: " + value._source.functionData.info[1]
        });
        title.appendTo(dl);

        var description = jQuery('<dd/>', {
            text: "Description: " + value._source.functionData.info[2]
        });
        description.appendTo(dl);

        var winners = jQuery('<dd/>', {
            text: "Number of winners: " + value._source.functionData.info[4]
        });
        winners.appendTo(dl);

        var textStatus = "";
        if (value._source.functionData.status == 0) {
            textStatus = "Winners have not been declared as yet";
            var status = jQuery('<dd/>', {
                text: textStatus,
                // Optional color change?
                // class: 'current'
            });
            status.appendTo(dl);

        } else if (value._source.functionData.status == 1) {
            textStatus = "Winners have been declared";
            var status = jQuery('<dd/>', {
                text: textStatus,
                // Optional color change?
                // class: 'expired'
            });
            status.appendTo(dl);
        }

        // Expiry time
        var epochRepresentation = value._source.functionData.info[5];
        if (epochRepresentation.toString().length == 10) {
            var endDate = new Date(epochRepresentation * 1000);
        } else if (epochRepresentation.toString().length == 13) {
            var endDate = new Date(epochRepresentation);
        }

        // Current time
        var currentDate = new Date();

        if (currentDate > endDate) {
            var time = jQuery('<dd/>', {
                text: "End date: " + endDate,
                class: "expired"
            });
            time.appendTo(dl);
        } else if (currentDate < endDate) {
            var time = jQuery('<dd/>', {
                text: "End date: " + endDate,
                class: "current"
            });
            time.appendTo(dl);
            // Allow user to play this giveaway
            var play = jQuery('<dd/>', {

            });
            var playUrl = "https://cybermiles.github.io/smart_contracts/FairPlay/v1/dapp/play.html?contract=" + value._source.contractAddress;
            var playButton = jQuery('<a/>', {
                href: playUrl,
                class: "btn btn-success",
                role: "button",
                target: "_blank",
                text: "Play"
            });
            playButton.appendTo(play);
            play.appendTo(dl);

        }

        //https://cybermiles.github.io/smart_contracts/FairPlay/dapp/play.html?contract=0x

        /* More details */
        var pGroup = jQuery('<div/>', {
            class: 'panel-group'
        });
        pGroup.appendTo(details);

        var pDefault = jQuery('<div/>', {
            class: 'panel panel-default'
        });
        pDefault.appendTo(pGroup);

        var pHeading = jQuery('<div/>', {
            class: 'panel-heading'
        });
        pHeading.appendTo(pDefault);

        var pTitle = jQuery('<p/>', {
            class: 'panel-title'
        });
        pTitle.appendTo(pHeading);

        var pToggle = jQuery('<a/>', {
            "data-toggle": 'collapse',
            href: "#collapse1",
            text: "Show/Hide Details"
        });
        pToggle.appendTo(pTitle);

        var pCollapse = jQuery('<div/>', {
            id: 'collapse1',
            class: 'panel-collapse collapse'
        });
        pCollapse.appendTo(pDefault);

        var pBody = jQuery('<div/>', {
            class: 'panel-body'
        });
        pBody.appendTo(pCollapse);

        var dl2 = jQuery('<dl/>', {});
        dl2.appendTo(pBody);

        var blockNumber = jQuery('<dd/>', {
            text: "Block number: " + value._source.blockNumber
        });
        blockNumber.appendTo(dl2);

        var cOwner = jQuery('<dd/>', {
            text: "Contract's owner: " + value._source.functionData.owner
        });
        cOwner.appendTo(dl2);

        var cAddress = jQuery('<dd/>', {
            text: "Contract's address: " + value._source.contractAddress
        });
        cAddress.appendTo(dl2);

        if (value._source.functionData.player_addrs == undefined) {
            var lineBreak = jQuery('<hr/>', {});
            lineBreak.appendTo(dl2);
            var pAddress = jQuery('<dd/>', {
                text: "Players: There are no players yet!"
            });
            pAddress.appendTo(dl2);
        } else {
            var lineBreak = jQuery('<hr/>', {});
            lineBreak.appendTo(dl2);
            $.each(value._source.functionData.player_addrs, function(playerIndex, playerValue) {
                var pAddress = jQuery('<dd/>', {
                    text: "Player : " + playerValue
                });
                pAddress.appendTo(dl2);
            });
        }

        if (value._source.functionData.winner_addrs == undefined) {
            var lineBreak = jQuery('<hr/>', {});
            lineBreak.appendTo(dl2);
            var wAddress = jQuery('<dd/>', {
                text: "Winners: There are no winners yet!"
            });
            wAddress.appendTo(dl2);
        } else {
            var lineBreak = jQuery('<hr/>', {});
            lineBreak.appendTo(dl2);
            $.each(value._source.functionData.winner_addrs, function(winnerIndex, winnerValue) {
                var wAddress = jQuery('<dd/>', {
                    text: "Winner : " + winnerValue
                });
                wAddress.appendTo(dl2);
            });
        }
        var lineBreak = jQuery('<hr/>', {});
        lineBreak.appendTo('.results');
    });


}
