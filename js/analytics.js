
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
                max: Math.floor((uniqueList.length/3)*4),
                title: "Unique Visitors (this week)"
            });
            console.log("Unique IP Addresses: " + uniqueList.length);
        })
        .catch(function() {
            console.log("Error");
        });
});