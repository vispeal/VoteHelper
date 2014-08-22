/*
 * This module defines how to process new friend request, used in main module
 */

// patch require
var require = patchRequire(require);

// new friend request handler
var NewFriendHandler = function() {
    // define global variable to use this in function defination
    var self = this;

    // global variable used in handler defination
    this.processing = false;
    this.max_message_id = 0;

    // check if this handler is processing. if so, can not do
    // other processing, used in main module
    this.is_processing = function(){
        return self.processing;
    };

    this.has_new_friend_request = function(){
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
    };

    this.process_new_friend = function(obj){
        self.processing = true;
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
                var msgids = [];
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
                    if (message_id <= self.max_message_id){
                        // already processed, continue
                        continue;
                    }
                    // TODO what is max message id not in message ids?
                    // that means some messages may be missing?
                    self.max_message_id = message_id;
                    console.log("process new message: " + message_id);
                    // then, click allow add link, it's a link
                    console.log("click footer link to allow add");
                    try {
                        obj.click('div[msgid="' + message_id + '"] div.footer a');
                    } catch (err) {
                        // maybe duplicated friend request, just skip over
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
                            // TODO what situation?
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
                                self.processing = false;
                            });
                        });
                    });
                }
            });
        });
    }

    this.check_new_friend = function(obj){
        //console.log("start check new friend request");
        var has_new = obj.evaluate(self.has_new_friend_request);
        if (has_new){
            self.process_new_friend(obj);
        }
    }

}// finish module defination

// export handler
module.exports = NewFriendHandler;
