var casper = require("casper").create();

casper.start("http://www.baidu.com/");

casper.on('remote.message', function(msg){
    console.log('remote: ' + msg);
});

var data = null;
casper.then(function(){
    console.log("load finished");
    data = this.evaluate(function(){
        console.log($);
        $.ajaxSetup({async: false});
        var resp = null;
        $.get("http://60.191.57.148:8080/api/handler?group_id=test&msg=%E9%A1%B6&sender=testuser&nick=testuser&group_users=", function(data, status){
            resp = data;
        });
        return resp;
    });
});

casper.then(function(){
    console.log(data.tip);
});

casper.run();
