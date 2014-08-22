/*
 * This module check if should auto finish vote and process
 */
// patch require
var require = patchRequire(require);

// load modules
var GroupUserHandler = require("./GroupUserHandler");
var DataHandler = require("./DataHandler");
// init module instance
var group_user_handler = new GroupUserHandler();
var data_handler = new DataHandler();
var vote_status_manager = require("./VoteStatusManager");

// Auto finish vote handler
var AutoFinishHandler = function() {
    var self = this;

    var vote_expire_time = 10;
    var auto_finish_tip = '已经超过' + vote_expire_time + "秒无人投票，投票自动结束";

    /* following to variable is to auto-finish voting */
    // step count, indicate how many steps is going on
    this.step_count = 0;

    this.is_processing = function(){
        return self.step_count !== 0;
    };

    this.really_finish_vote = function(obj, conv_id){
        var data = {
            message: {
                id: "auto_stop_vote",
                username: "robot",
                nickname: "投票小助手",
                message: "@投票小助手 完成投票",
                group_id: conv_id
            },
            type: "stop_vote"
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
                // start send message step
                // fill and send response message
                obj.sendKeys("#chat_editor #textInput", resp.tip);
                obj.click("#chat_editor a.chatSend");
            }
            self.step_count -= 1;
        }, data);
    };

    this.get_messages = function(max_id, conv_id){
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
    };


    this.auto_finish_vote = function(obj, conv_id){
        console.log("Conversation expired, auto finish: " + conv_id);
        // auto finish conversation vote
        // first, click at conversation div, switch to conversation
        obj.click('div#' + conv_id);
        // start send auto finish message step and finish vote step
        self.step_count += 1;
        var max_id = 0;
        if (conv_id in vote_status_manager.max_message_dict){
            max_id = vote_status_manager.max_message_dict[conv_id];
        }
        console.log("max id before auto finish: " + max_id);
        obj.wait(500, function(){
            // second, fill and submit auto finish vote message
            // fill and send response message
            obj.sendKeys("#chat_editor #textInput", auto_finish_tip);
            obj.click("#chat_editor a.chatSend");
            vote_status_manager.auto_finish_dict[conv_id] = new Date();
            // then, call api and add later processing logic
            if (conv_id in vote_status_manager.voting_dict){
                delete vote_status_manager.voting_dict[conv_id];
            }
            self.really_finish_vote(obj, conv_id);
        });
        self.finish_process_callback(obj, conv_id);
    };

    this.check_auto_finish_vote = function(obj){
        var last_vote_time = null;
        // iterate over all voting conversations to find out expired conversation,
        // just process the first expired conversation one time
        var now = new Date();
        for (conv_id in vote_status_manager.voting_dict){
            if (!(conv_id in vote_status_manager.last_vote_dict)){
                console.log("###Error### last vote not exists in last vote dict for conversation: " + conv_id);
                continue;
            }
            last_vote_time = vote_status_manager.last_vote_dict[conv_id];
            // longer than 10 seconds after last vote
            if (parseInt((now - last_vote_time) / 1000) >= vote_expire_time){
                self.auto_finish_vote(obj, conv_id);
                return;
            }
        }
    };

    this.parse_message = function(message){
        var result = {
            vote: false,
        };
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
    };

    this.process_leftover_message = function(obj, conv_id, message, result){
        var now = new Date();
        // update voting status
        if (!(conv_id in vote_status_manager.voting_dict)){
            if (conv_id in vote_status_manager.auto_finish_dict &&
                parseInt((now - vote_status_manager.auto_finish_dict[conv_id]) / 1000) <= 2){
                console.log("send tip to remind vote not valid");
                obj.sendKeys("#chat_editor #textInput", "@" + message.nickname + "的投票在结束后发生，不计入统计结果");
                obj.click("#chat_editor a.chatSend");
            }
            console.log("###Error### conversation not in voting dict when voting: " + conv_id);
            console.log(conv_id in vote_status_manager.auto_finish_dict);
            console.log(now);
            console.log(vote_status_manager.auto_finish_dict[conv_id]);
            console.log("###Error### conversation not in voting dict when voting: " + conv_id);
        }
    };


    this.finish_processing_leftover_messages = function(obj, conv_id){
        while (true){
            if (!(conv_id in vote_status_manager.max_message_dict)){
                return true;
            }
            var max_id = vote_status_manager.max_message_dict[conv_id];
            var messages = obj.evaluate(self.get_messages, max_id, conv_id);
            if (messages.length == 0){
                return true;
            }
            console.log("got " + messages.length + " new messages in finish leftover messages");
            for (var i=0; i < messages.length; i++){
                var result = self.parse_message(messages[i]);
                if (result.vote){
                    self.process_leftover_message(obj, conv_id, messages[i], result);
                }
                vote_status_manager.max_message_dict[conv_id] = messages[i].id;
            }
        }
    };

    this.finish_process_callback = function(obj, conv_id){
        obj.waitFor(function check(){
            return self.step_count == 0 && self.finish_processing_leftover_messages(obj, conv_id);
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
        }, function timeout(){
            console.log("###Error### send new message longer than 60 seconds!");
        }, 50000);
    };

};

// export handler
module.exports = AutoFinishHandler;
