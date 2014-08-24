/*
 * This module is to process new message in conversations
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

// GroupUserHandler
var MessageHandler = function() {
    var self = this;

    this.step_count = 0;

    this.is_processing = function(){
        return self.step_count !== 0;
    };

    this.get_updated_conversations = function(){
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

    this.parse_message = function(message){
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
    };

    this.process_useful_message = function(obj, message, result){
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
            self.step_count += 1;
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
                        // fill and send response message
                        obj.sendKeys("#chat_editor #textInput", resp.tip);
                        obj.click("#chat_editor a.chatSend");
                    }
                    self.step_count -= 1;
                } else if (data.type == "history"){
                    //console.log("Get group users callback");
                    var find_username, find_nickname;
                    if (/查询\@/gi.test(message.message)){
                        //console.log("find some one else history: " + message.message);
                        find_nickname = message.message.replace(/@.*?查询(\s)*@/g, "");
                        find_username = find_nickname;
                        for (var i=0; i < users.length; i++){
                            if (users[i].nickname.trim() == find_nickname.trim()){
                                find_username = users[i].username;
                                break;
                            }
                        }
                    } else {
                        //console.log("find self history: " + message.message);
                        find_username = message.username;
                        find_nickname = message.nickname;
                    }
                    //console.log("want to find history of user: " + find_user);
                    var resp = data_handler.send_history_message(obj, message, type, find_username, find_nickname);
                    //console.log(JSON.stringify(resp));
                    if ('tip' in resp && resp.tip.length > 0){
                        // fill and send response message
                        obj.sendKeys("#chat_editor #textInput", resp.tip);
                        obj.click("#chat_editor a.chatSend");
                    }
                    self.step_count -= 1;
                } else {
                    console.log("unknow type in get group users callback: " + data.type);
                    self.step_count -= 1;
                }
            }, data);
            return;
        } else {
            var resp = data_handler.send_message(obj, message, type);
            //console.log(JSON.stringify(resp));
            if ('tip' in resp && resp.tip.length > 0){
                // fill and send response message
                obj.sendKeys("#chat_editor #textInput", resp.tip);
                obj.click("#chat_editor a.chatSend");
            }
        }
    };

    this.update_voting_status = function(obj, conv_id, message, result){
        var now = new Date();
        // update voting status
        if (result.start_vote){
            vote_status_manager.voting_dict[conv_id] = true;
            vote_status_manager.last_vote_dict[conv_id] = new Date();
        } else if (result.finish_vote){
            if (!(conv_id in vote_status_manager.voting_dict)){
                console.log("###Error### conversation not in voting dict when finish voting: " + conv_id);
            } else {
                delete vote_status_manager.voting_dict[conv_id];
            }
            if (!(conv_id in vote_status_manager.last_vote_dict)){
                console.log("###Error### conversation not in last vote dict when finish voting: " + conv_id);
            } else {
                delete vote_status_manager.last_vote_dict[conv_id];
            }
        } else if (result.vote){
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
            if (!(conv_id in vote_status_manager.last_vote_dict)){
                console.log("###Error### conversation not in last vote dict when voting: " + conv_id);
            } else {
                vote_status_manager.last_vote_dict[conv_id] = new Date();
            }
        } else {
            //
        }
    };

    this.process_new_messages = function(conv_id, messages, obj){
        for (var i=0; i < messages.length; i++){
            //console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
            // parse message
            var result = self.parse_message(messages[i]);
            self.update_voting_status(obj, conv_id, messages[i], result);
            //console.log("message after parse: ");
            //console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
            // record max message id
            if (!(conv_id in vote_status_manager.max_message_dict)){
                vote_status_manager.max_message_dict[conv_id] = messages[i].id;
            }
            if (conv_id in vote_status_manager.max_message_dict && vote_status_manager.max_message_dict[conv_id] < messages[i].id){
                vote_status_manager.max_message_dict[conv_id] = messages[i].id;
            }
            // process useful message
            if (result.atme || result.vote){
                // sync process useful message
                self.process_useful_message(obj, messages[i], result);
            }
        }
        self.finish_process_callback(obj, conv_id);
    };

    this.finish_process_callback = function(obj, conv_id){
        obj.waitFor(function check(){
            return self.step_count == 0;
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

    this.check_new_messages = function(obj){
        //console.log("start to check new message");
        // first, check conversation list to get updated conversation
        //obj.debugHTML("div#conversationContainer");
        var conv_ids = obj.evaluate(self.get_updated_conversations);
        if (conv_ids.length == 0){
            //console.log("no new message in chatroom conversation");
            return;
        }
        // second, click on updated conversation, get conversation detail

        // TODO just handle one conversation one time
        //for (var i=0; i < conv_ids.length; i++){
        var conv_id = conv_ids[0];
        //console.log("click conversation: " + conv_id);
        try {
            obj.click('div#' + conv_id);
        } catch (err){
            return;
        }
        var max_id = 0;
        if (conv_id in vote_status_manager.max_message_dict){
            max_id = vote_status_manager.max_message_dict[conv_id];
        }
        obj.wait(200, function(){
            // then, get new messages by message id
            //console.log("get messages from conversation: " + conv_id + " with max message id: " + max_id);
            var messages = obj.evaluate(self.get_messages, max_id, conv_id);
            //console.log("got messages: " + messages.length);
            // process new messages
            self.process_new_messages(conv_id, messages, obj);
        });
    };
};

// export handler
module.exports = MessageHandler;
