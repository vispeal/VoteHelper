/* start to check and process new message in chat rooms */

// max message id dict, key is conversation id, value is max message id

var max_message_dict = {};

function get_updated_conversations(){
    var elems = document.querySelectorAll('div#conversationContainer div[id$="chatroom"] span.unreadDot');
    var elem;
    var updated_conversations = [];
    console.log("Got chatroom conversations: " + elems.length);
    for (var i=0; i < elems.length; i++){
        elem = elems[i];
        var style = elem.style.display;
        console.log(style);
        if (style.indexOf("none") == -1){
            console.log("Got updated chatroom conversations: " + elem.parentNode.id);
            updated_conversations.push(elem.parentNode.id);
        }
    }
    console.log("return updated conversations: " + updated_conversations.length);
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
        console.log(img_node);
        console.log(img_node.tagName);
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
    };
    // check if at me
    // TODO should construct regex by myname dynamicly
    var atme_re = /\@投票小助手/;
    if (atme_re.test(message.message)){
        result.atme = true;
        return result;
    }
    // check if strong or weak
    var strong_re = /\/qqface\/79\.png/;
    if (strong_re.test(message.message)){
        message.message = message.message.replace(/<img .*?(\/qqface\/79\.png).*?>/g, "[strong]");
        result.vote = true;
    }
    var weak_re = /\/qqface\/80\.png/;
    if (weak_re.test(message.message)){
        message.message = message.message.replace(/<img .*?(\/qqface\/80\.png).*?>/g, "[strong]");
        result.vote = true;
    }
    return result;
}

var processing_send_message = 0;

function process_useful_message(obj, message, result){
    // TODO call api to get message
    if (result.atme){
        processing_send_message += 1;
        // fill and send response message
        obj.sendKeys("#chat_editor #textInput", "自动回复了");
        obj.wait(500, function(){
            obj.click("#chat_editor a.chatSend");
            processing_send_message -= 1
        });
    }
}

function process_new_messages(conv_id, messages, obj, finish_process_callback){
    for (var i=0; i < messages.length; i++){
        console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
        // parse message
        var result = parse_message(messages[i]);
        if (result.atme){
            console.log("atme message");
        }
        if (result.vote){
            console.log("vote message");
        }
        console.log("message after parse: ");
        console.log("Got new message from chatroom, from user: " + messages[i].username + ", nickname: " + messages[i].nickname + ", message: " + messages[i].message);
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
        console.log('process conversation finished, switch to weixin or helper');
        try {
            obj.click("div#conversationContainer div#conv_weixin");
        } catch (err){
            obj.click("div#conversationContainer div#conv_filehelper");
        }
        processing = false;
    }, function timeout(){
        console.log("###Error### send new message longer than 60 seconds!");
    }, 60000);
}

function check_new_message(obj){
    console.log("start to check new message");
    // first, check conversation list to get updated conversation
    //obj.debugHTML("div#conversationContainer");
    var conv_ids = obj.evaluate(get_updated_conversations);
    if (conv_ids.length == 0){
        console.log("no new message in chatroom conversation");
        return;
    }
    // second, click on updated conversation, get conversation detail

    // TODO just handle one conversation one time
    //for (var i=0; i < conv_ids.length; i++){
    processing = true;
    var conv_id = conv_ids[0];
    console.log("click conversation: " + conv_id);
    obj.click('div#' + conv_id);
    var max_id = 0;
    if (conv_id in max_message_dict){
        max_id = max_message_dict[conv_id];
    }
    obj.wait(500, function(){
        // then, get new messages by message id
        console.log("get messages from conversation: " + conv_id + " with max message id: " + max_id);
        var messages = obj.evaluate(get_messages, max_id, conv_id);
        console.log("got messages: " + messages.length);
        // process new messages
        process_new_messages(conv_id, messages, obj, finish_process_callback);
    });
    //}
}

/* ============================================ */

