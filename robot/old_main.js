// init casper instance
var casper = require('casper').create();
// load modules
var GroupUserHandler = require("./GroupUserHandler");
var DataHandler = require("./DataHandler");
// init module instance
var group_user_handler = new GroupUserHandler();
var data_handler = new DataHandler();

// global options
var vote_expire_time = 10;
var auto_finish_tip = '已经超过' + vote_expire_time + "秒无人投票，投票自动结束";

// open weixin web page
casper.start('https://wx.qq.com/', function() {
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
    this.page.render("chat.jpg");
    console.log("render chat finished");
}, function timeout(){
    console.log("wait for login timeout");
    casper.die()
}, 300000);

/* start to check and process new friend request */

var processing = false;

var max_message_id = 0;

function has_new_friend_request(){
    //console.log("check if has new friend request");
    var elem = document.querySelectorAll("div#conversationContainer div#conv_fmessage span.unreadDot");
    //console.log(elem);
    //console.log("Got unread friend request: " + elem.length);
    if (elem.length > 0){
        elem = elem[0];
        var style = elem.style.display;
        //console.log(style);
        if (style.indexOf("none") != -1){
            return false;
        } else {
            return true;
        }
    } else {
        return false;
    }
}

function process_new_friend(obj){
    processing = true;
    console.log("process new friend");
    // first, click new friend conversation to open it
    console.log("swith to friend conversation");
    try {
        obj.click("div#conversationContainer div#conv_fmessage");
    } catch (err) {
        console.log("###Error### can not switch to friend conversation");
        return;
    }
    // second, get new message in conversation
    console.log("wait one second");
    obj.wait(1000, function(){
        console.log("get message ids");
        var msgids = obj.evaluate(function(){
            var elems = document.querySelectorAll("div#chat_chatmsglist .cloudPannel");
            var msgids = new Array();
            for (var i=0; i < elems.length; i++){
                console.log("got message id: " + elems[i].getAttribute("msgid"))
                msgids.push(parseInt(elems[i].getAttribute("msgid")));
            }
            return msgids;
        });
        console.log("get message ids finished");
        console.log("start following processes");
        obj.wait(2000, function(){
            // process messages
            for (var i=0; i < msgids.length; i++){
                var message_id = msgids[i];
                if (message_id <= max_message_id){
                    // already processed, continue
                    continue;
                }
                max_message_id = message_id;
                console.log("process new message: " + message_id);
                // then, click allow add link, it's a link
                console.log("click footer link to allow add");
                try {
                    obj.click('div[msgid="' + message_id + '"] div.footer a');
                } catch (err) {
                    console.log("###Error### can not click footer link while add new friend");
                    continue;
                }
                console.log("wait 500 ms");
                obj.wait(2000, function(){
                    // then, click allow add button
                    console.log("click allow add button");
                    try {
                        obj.click('div#popupcontactprofile div.nextStep input[value="Accept"]');
                    } catch (err){
                        console.log("###Error### can not click Accept while add new friend");
                        return;
                    }
                    console.log("wait for 200 ms");
                    obj.wait(1000, function(){
                        // then, click close button
                        console.log("click close");
                        try {
                            obj.click("div#popupcontactprofile span.closeIconPanel a");
                        } catch (err){
                            console.log("###Error### can not click close wihle add new friend");
                        }
                        obj.wait(500, function(){
                            // switch to weixin tab, in order to check new request by unread count
                            console.log("switch to weixin conversation");
                            try {
                                obj.click("div#conversationContainer div#conv_weixin");
                            } catch (err){
                                try {
                                    obj.click("div#conversationContainer div#conv_filehelper");
                                } catch (err){
                                    console.log("###Error### can not switch to weixin or filehelper after add new friend");
                                }
                            }
                            processing = false;
                        });
                    });
                });
            }
        });
    });
}

// check and process new friend request
function check_new_friend(obj){
    //console.log("start check new friend request");
    var has_new = obj.evaluate(has_new_friend_request);
    if (has_new){
        process_new_friend(obj);
    }
}

/* ============================================ */

/* start to check and process new message in chat rooms */

// max message id dict, key is conversation id, value is max message id
var max_message_dict = {};

/* following to variable is to auto-finish voting */
// voting dict, key is conversation id, value is boolean value to indicate
// whether the conversation is voting
var voting_dict = {};
// last voting time dict, key is conversation id, value is date object to
// indicate the last voting time in conversation
var last_vote_dict = {};

function really_finish_vote(obj, conv_id){
    var data = {
        message: {
            id: "auto_stop_vote",
            username: "robot",
            nickname: "投票小助手",
            message: "@投票小助手 完成投票",
            group_id: conv_id,
        },
        type: "stop_vote",
    };
    group_user_handler.get_group_users(obj, function(obj, data, users){
        //console.log("Get group users callback");
        var group_users = [];
        for (var i=0; i < users.length; i++){
            //console.log("Got group user: " + users[i].username + ", nickname: " + users[i].nickname);
            group_users.push({id: users[i].username, name: users[i].nickname});
        }
        var resp = data_handler.send_message(obj, data.message, data.type, group_users);
        //console.log(JSON.stringify(resp));
        if ('tip' in resp && resp.tip.length > 0){
            processing_send_message += 1;
            // fill and send response message
            obj.sendKeys("#chat_editor #textInput", resp.tip);
            obj.wait(100, function(){
                obj.click("#chat_editor a.chatSend");
                processing_send_message -= 1
            });
        }
        processing_send_message -= 1;
    }, data);
}

function auto_finish_vote(obj, conv_id){
    console.log("Conversation expired, auto finish: " + conv_id);
    // auto finish conversation vote
    // first, click at conversation div, switch to conversation
    obj.click('div#' + conv_id);
    processing_send_message += 2;
    obj.wait(500, function(){
        // second, fill and submit auto finish vote message
        // fill and send response message
        obj.sendKeys("#chat_editor #textInput", auto_finish_tip);
        obj.wait(100, function(){
            obj.click("#chat_editor a.chatSend");
            processing_send_message -= 1
        });
        // then, call api and add later processing logic
        obj.wait(100, function(){
            if (conv_id in voting_dict){
                delete voting_dict[conv_id];
            }
            really_finish_vote(obj, conv_id);
        });
    });
}

// check whether voting is expired in every voting conversations
function check_auto_finish_vote(obj){
    var last_vote_time = null;
    // iterate over all voting conversations to find out expired conversation,
    // just process the first expired conversation one time
    var now = new Date();
    for (conv_id in voting_dict){
        if (!(conv_id in last_vote_dict)){
            console.log("###Error### last vote not exists in last_vote_dict for conversation: " + conv_id);
            continue;
        }
        last_vote_time = last_vote_dict[conv_id];
        // longer than 10 seconds after last vote
        if (parseInt((now - last_vote_time) / 1000) >= vote_expire_time){
            auto_finish_vote(obj, conv_id);
            return;
        }
    }
}

function get_updated_conversations(){
    var elems = document.querySelectorAll('div#conversationContainer div[id$="chatroom"] span.unreadDot');
    var elem;
    var updated_conversations = [];
    //console.log("Got chatroom conversations: " + elems.length);
    for (var i=0; i < elems.length; i++){
        elem = elems[i];
        var style = elem.style.display;
        //console.log(style);
        if (style.indexOf("none") == -1){
            //console.log("Got updated chatroom conversations: " + elem.parentNode.id);
            updated_conversations.push(elem.parentNode.id);
        } 
    }
    //console.log("return updated conversations: " + updated_conversations.length);
    // TODO just return first conversation
    if (updated_conversations.length > 0){
        return [updated_conversations[0]]
    }
    return updated_conversations;
}

function get_messages(max_id, conv_id){
    var elems = document.querySelectorAll('div#chat_chatmsglist div.chatItem.you div.cloud.cloudText');
    var find_max = false;
    var messages = [];
    for (var i=0; i < elems.length; i++){
        var msgid = parseInt(elems[i].getAttribute("msgid"));
        if (msgid < max_id){
            continue;
        }
        if (msgid == max_id){
            find_max = true;
            continue;
        }
        var img_node = elems[i].previousSibling.previousSibling;
        //console.log(img_node);
        //console.log(img_node.tagName);
        if (img_node == null || img_node.tagName != "IMG"){
            console.log("###Error### can not get image node of message!");
            console.log(elems[i].innerHTML);
            console.log(elems[i].parentNode.innerHTML);
            continue;
        }
        var msg_dom = document.querySelector('div#chat_chatmsglist div[msgid="' + msgid + '"] .cloudContent pre');
        if (msg_dom == null){
            console.log("###Error### can not get message!");
            console.log(elems[i].innerHTML);
            continue;
        }
        var message = {
            id: msgid,
            username: img_node.getAttribute("username"),
            nickname: img_node.getAttribute("title"),
            message: msg_dom.innerHTML,
            group_id: conv_id,
        };
        messages.push(message);
    }
    if (!find_max && max_id != 0){
        console.log("###Error### not find max message id, may be need to scroll!");
    }
    return messages;
}

function parse_message(message){
    var result = {
        atme: false,
        vote: false,
        start_vote: false,
        finish_vote: false,
        history: false,
    };
    // check if at me 
    // TODO should construct regex by myname dynamicly
    var atme_re = /\@投票小助手/g;
    var finish_re = /(完成投票)|(@投票小助手(\s)0)/g;
    var start_re = /(开始投票)|(@投票小助手(\s)1(\s))|(@投票小助手(\s)2(\s))/g;
    if (atme_re.test(message.message)){
        result.atme = true;
        if (start_re.test(message.message)){
            result.start_vote = true;
        }
        if (finish_re.test(message.message)){
            result.finish_vote = true;
        }
        if (/查询/.test(message.message)){
            result.history = true;
        }
        return result;
    }
    // check if strong or weak
    var strong_re = /\/qqface\/79\.png/g;
    if (strong_re.test(message.message)){
        //message.message = message.message.replace(/<img .*?(\/qqface\/79\.png).*?>/g, "[strong]");
        //message.message = message.message.replace("/qqface/79.png", "[strong]");
        message.message = message.message.replace(/\/qqface\/79\.png/g, "[strong]");
        result.vote = true;
    }
    var weak_re = /\/qqface\/80\.png/g;
    if (weak_re.test(message.message)){
        //message.message = message.message.replace(/<img .*?(\/qqface\/80\.png).*?>/g, "[weak]");
        //message.message = message.message.replace("/qqface/80.png", "[weak]");
        message.message = message.message.replace(/\/qqface\/80\.png/g, "[weak]");
        result.vote = true;
    }
    return result;
}

var processing_send_message = 0;

function process_useful_message(obj, message, result){
    var type = "normal";
    if (result.history){
        type = "history";
    } else if (result.finish_vote){
        type = "stop_vote";
    }
    var users = null;
    if (type == "history" || type == "stop_vote"){
        var data = {
            message: message,
            type: type,
        };
        processing_send_message += 1;
        group_user_handler.get_group_users(obj, function(obj, data, users){
            if (data.type == "stop_vote"){
                //console.log("Get group users callback");
                var group_users = [];
                for (var i=0; i < users.length; i++){
                    //console.log("Got group user: " + users[i].username + ", nickname: " + users[i].nickname);
                    group_users.push({id: users[i].username, name: users[i].nickname});
                }
                var resp = data_handler.send_message(obj, data.message, type, group_users);
                //console.log(JSON.stringify(resp));
                if ('tip' in resp && resp.tip.length > 0){
                    processing_send_message += 1;
                    // fill and send response message
                    obj.sendKeys("#chat_editor #textInput", resp.tip);
                    obj.wait(100, function(){
                        obj.click("#chat_editor a.chatSend");
                        processing_send_message -= 1
                    });
                }
                processing_send_message -= 1;
            } else if (data.type == "history"){
                //console.log("Get group users callback");
                var find_user = null;
                if (/查询\@/gi.test(message.message)){
                    //console.log("find some one else history: " + message.message);
                    find_user = message.message.replace(/@.*?查询(\s)*@/g, "");
                    for (var i=0; i < users.length; i++){
                        //console.log("Compare group user: " + users[i].username + ", nickname: " + users[i].nickname);
                        //console.log("find user: " + find_user);
                        if (users[i].nickname.trim() == find_user.trim()){
                            find_user = users[i].username;
                            break;
                        }
                    }
                } else {
                    //console.log("find self history: " + message.message);
                    find_user = message.username;
                }
                //console.log("want to find history of user: " + find_user);
                var resp = data_handler.send_history_message(obj, message, type, find_user);
                //console.log(JSON.stringify(resp));
                if ('tip' in resp && resp.tip.length > 0){
                    processing_send_message += 1;
                    // fill and send response message
                    obj.sendKeys("#chat_editor #textInput", resp.tip);
                    obj.wait(100, function(){
                        obj.click("#chat_editor a.chatSend");
                        processing_send_message -= 1
                    });
                }
                processing_send_message -= 1;
            } else {
                console.log("unknow type in get group users callback: " + data.type);
                processing_send_message -= 1;
            }
        }, data);
        return;
    } else {
        var resp = data_handler.send_message(obj, message, type);
        //console.log(JSON.stringify(resp));
        if ('tip' in resp && resp.tip.length > 0){
            processing_send_message += 1;
            // fill and send response message
            obj.sendKeys("#chat_editor #textInput", resp.tip);
            obj.wait(200, function(){
                obj.click("#chat_editor a.chatSend");
                processing_send_message -= 1
            });
        }
    }
}

function update_voting_status(conv_id, message, result){
    // update voting status
    if (result.start_vote){
        voting_dict[conv_id] = true;
        last_vote_dict[conv_id] = new Date();
    } else if (result.finish_vote){
        if (!(conv_id in voting_dict)){
            console.log("###Error### conversation not in voting dict when finish voting: " + conv_id);
        } else {
            delete voting_dict[conv_id];
        }
        if (!(conv_id in last_vote_dict)){
            console.log("###Error### conversation not in last vote dict when finish voting: " + conv_id);
        } else {
            delete last_vote_dict[conv_id];
        }
    } else if (result.vote){
        if (!(conv_id in voting_dict)){
            console.log("###Error### conversation not in voting dict when voting: " + conv_id);
        }
        if (!(conv_id in last_vote_dict)){
            console.log("###Error### conversation not in last vote dict when voting: " + conv_id);
        } else {
            last_vote_dict[conv_id] = new Date();
        }
    } else {
        //
    }
}

function process_new_messages(conv_id, messages, obj, finish_process_callback){
    for (var i=0; i < messages.length; i++){
        //console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
        // parse message
        var result = parse_message(messages[i]);
        update_voting_status(conv_id, messages[i], result);
        //console.log("message after parse: ");
        //console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
        // record max message id
        if (!(conv_id in max_message_dict)){
            max_message_dict[conv_id] = messages[i].id;
        }
        if (conv_id in max_message_dict && max_message_dict[conv_id] < messages[i].id){
            max_message_dict[conv_id] = messages[i].id;
        }
        // process useful message
        if (result.atme || result.vote){
            // sync process useful message
            process_useful_message(obj, messages[i], result);
        }
    }
    finish_process_callback(obj);
}

function finish_process_callback(obj){
    obj.waitFor(function check(){
        return processing_send_message == 0;
    }, function then(){
        //console.log('process conversation finished, switch to weixin or helper');
        try {
            obj.click("div#conversationContainer div#conv_weixin");
        } catch (err){
            try {
                obj.click("div#conversationContainer div#conv_filehelper");
            } catch (err){
                console.log("###Error### can not switch to weixin or filehelper");
            }
        }
        processing = false;
    }, function timeout(){
        console.log("###Error### send new message longer than 60 seconds!");
    }, 50000);
}

function check_new_message(obj){
    //console.log("start to check new message");
    // first, check conversation list to get updated conversation
    //obj.debugHTML("div#conversationContainer");
    var conv_ids = obj.evaluate(get_updated_conversations);
    if (conv_ids.length == 0){
        //console.log("no new message in chatroom conversation");
        return;
    }
    // second, click on updated conversation, get conversation detail

    // TODO just handle one conversation one time
    //for (var i=0; i < conv_ids.length; i++){
    processing = true;
    var conv_id = conv_ids[0];
    //console.log("click conversation: " + conv_id);
    try {
        obj.click('div#' + conv_id);
    } catch (err){
        return;
    }
    var max_id = 0;
    if (conv_id in max_message_dict){
        max_id = max_message_dict[conv_id];
    }
    obj.wait(200, function(){
        // then, get new messages by message id
        //console.log("get messages from conversation: " + conv_id + " with max message id: " + max_id);
        var messages = obj.evaluate(get_messages, max_id, conv_id);
        //console.log("got messages: " + messages.length);
        // process new messages
        process_new_messages(conv_id, messages, obj, finish_process_callback);
    });
    //}
}

/* ============================================ */

// main process
function _main_process(obj){
    //console.log("in main process");
    // check and process new friend request
    check_new_friend(obj);
    // check new message in chat rooms
    check_new_message(obj);
    // check auto finish voting
    check_auto_finish_vote(obj);
}

// endless loop to handle message, process every seconds
function endlessLoop(obj){
    casper.wait(100, function(){
        _main_process(obj);
        obj.waitFor(function check(){
            return !processing;
        }, function then(){
            endlessLoop(obj);
        }, function timeout(){
            console.log("###Error### process message longer than 60 seconds, something must be wrong!");
        }, 60000)
    });
}

// enter endless loop
casper.then(function(){
    endlessLoop(casper);
});

casper.run();
