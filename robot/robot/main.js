// init casper instance
var casper = require('casper').create();
// load modules
var NewFriendHandler = require("./NewFriendHandler");
var MessageHandler = require("./MessageHandler");
//var AutoFinishHandler = require("./AutoFinishHandler");
var GroupUserHandler = require("./GroupUserHandler");
var DataHandler = require("./DataHandler");
// init module instance
var new_friend_handler = new NewFriendHandler();
var message_handler = new MessageHandler();
//var auto_finish_handler = new AutoFinishHandler();
var group_user_handler = new GroupUserHandler();
var data_handler = new DataHandler();

// open weixin web page
casper.start('https://wx.qq.com/', function() {
    casper.viewport(1280, 800);
    this.echo(this.getTitle());
    console.log("load page finished");
});

casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});

// render weixin webpage, contans qrcode
casper.then(function(){
    this.page.render("qrcode.jpg");
    console.log("render qrcode finished");
});

// wait for 5 minutes to login
casper.waitFor(function check() {
    return this.evaluate(function() {
        return document.querySelectorAll('#profile div.myProfile').length > 0;
    });
}, function then() {
    // login finished 
    // render chat page for test
    //this.page.render("chat.jpg");
    console.log("render chat finished");
}, function timeout(){
    console.log("wait for login timeout");
    casper.die();
}, 300000);

// main process
function _main_process(){
    //console.log("in main process");
    // check and process new friend request
    new_friend_handler.check_new_friend(casper);
    // check new message in chat rooms
    message_handler.check_new_messages(casper);
    // check auto finish voting
    //auto_finish_handler.check_auto_finish_vote(obj);
}

// endless loop to handle message, process every seconds
function endlessLoop(){
    casper.wait(100, function(){
        _main_process();
        casper.waitFor(function check(){
            //return !new_friend_handler.is_processing() && !message_handler.is_processing() &&
            //        !auto_finish_handler.is_processing();
            return !new_friend_handler.is_processing() && !message_handler.is_processing();
        }, function then(){
            endlessLoop();
        }, function timeout(){
            console.log(new_friend_handler.is_processing());
            console.log(message_handler.is_processing());
            //console.log(auto_finish_handler.is_processing());
            console.log("###Error### process message longer than 60 seconds, something must be wrong!");
        }, 60000);
    });
}

// enter endless loop
casper.then(function(){
    endlessLoop();
});

casper.run();
