// patch require
var require = patchRequire(require);

// GroupUserHandler
var GroupUserHandler = function() {
    var self = this;
    
    this.get_group_users = function(obj, callback, data) {
        // first, click at the group users button
        obj.click('div.chatContainer div#rightOpBtn a');
        // wait some time, than to get users by evaluate
        obj.wait(1000, function(){
            // to get users
            var users = obj.evaluate(self.get_users);
            // call callback to process group users
            callback(obj, data, users);
        });
    }

    this.get_users = function(){
        var elems = document.querySelectorAll('div[id^="personal_info_"]');
        var users = [];
        for (var i=0; i < elems.length; i++){
            var user = {
                username: elems[i].id.replace("personal_info_", ""),
                nickname: elems[i].getAttribute("title"),
            };
            if (user.nickname == null || user.nickname.length == 0){
                user.nickname = user.username;
            }
            users.push(user);
        }
        return users;
    }
}

// export handler
module.exports = GroupUserHandler;
