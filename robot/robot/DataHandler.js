// patch require
var require = patchRequire(require);

// GroupUserHandler
var DataHandler = function() {
    var self = this;

    this.server = "http://60.191.57.148:8080";
    this.handler_api = "/api/handler";

    this.build_normal_params = function(message){
        var param = "?";
        param += "group_id=" + message.group_id;
        param += "&msg=" + message.message;
        param += "&sender=" + message.username;
        param += "&nick=" + message.nickname;
        return param;
    };

    this.build_user_params = function(message, users){
        var param = "?";
        param += "group_id=" + message.group_id;
        param += "&msg=" + message.message;
        param += "&sender=" + message.username;
        param += "&nick=" + message.nickname;
        param += "&group_users=" + JSON.stringify(users);
        return param;
    };

    this.send_request_with_users = function(obj, message, users){
        var url = self.server + self.handler_api;
        //var params = self.build_user_params(message, users);
        //url += params;
        console.log("Request Api: " + url);
        var resp = obj.evaluate(function(url, message, users){
            try {
                console.log($.ajaxSetup);
                $.ajaxSetup({async: false});
                var response = null;
                $.ajax({
                    type: 'post',
                    url: url, 
                    data: {
                        group_id: message.group_id,
                        msg: message.message,
                        sender: message.username,
                        nick: message.nickname,
                        group_users: JSON.stringify(users)
                    },
                    async: false,
                    success: function(data, status){
                        console.log("got data finished");
                        console.log(status);
                        console.log(JSON.stringify(data));
                        if (status == 'success'){
                            response = data;
                        } else {
                            console.log("request api failed: " + data);
                        }
                    },
                    error: function(request, status, error){
                        console.log("request api failed, status: " + status + ", error: " + error);
                        //response = {tip: "request api failed, status: " + status + ", error: " + error};
                        response = {tip: "操作错误"};
                    }
                });
                return response;
            } catch (err) {
                console.log("evaluate failed: " + err);
            }
        }, url, message, users);
        return resp;
    };

    this.send_normal_request = function(obj, message){
        var url = self.server + self.handler_api;
        //var params = self.build_normal_params(message);
        //url += params;
        console.log("Request Api: " + url);
        var resp = obj.evaluate(function(url, message){
            try {
                console.log($.ajaxSetup);
                $.ajaxSetup({async: false});
                var response = null;
                $.ajax({
                    type: 'post',
                    url: url, 
                    data: {
                        group_id: message.group_id,
                        msg: message.message,
                        sender: message.username,
                        nick: message.nickname
                    },
                    async: false,
                    success: function(data, status){
                        console.log("got data finished");
                        console.log(status);
                        console.log(JSON.stringify(data));
                        if (status == 'success'){
                            response = data;
                        } else {
                            console.log("request api failed: " + data);
                        }
                    },
                    error: function(request, status, error){
                        console.log("request api failed, status: " + status + ", error: " + error);
                        //response = {tip: "request api failed, status: " + status + ", error: " + error};
                        response = {tip: "操作错误"};
                    }
                });
                return response;
            } catch (err) {
                console.log("evaluate failed: " + err);
            }
        }, url, message);
        return resp;
    };

    this.send_message = function(obj, message, type, users) {
        if (type == "history" || type == "stop_vote"){
            return self.send_request_with_users(obj, message, users);
        } else if (type == "normal"){
            return self.send_normal_request(obj, message);
        } else {
            console.log("unknow type!");
            return null;
        }
    };

    this.build_history_params = function(message, member){
        var param = "?";
        param += "group_id=" + message.group_id;
        param += "&msg=" + message.message;
        param += "&sender=" + message.username;
        param += "&nick=" + message.nickname;
        param += "&member=" + member;
        return param;
    };


    this.send_history_message = function(obj, message, type, member, nickname){
        var url = self.server + self.handler_api;
        //var params = self.build_history_params(message, member);
        //url += params;
        console.log("Request Api: " + url);
        var resp = obj.evaluate(function(url, message, member, nickname){
            try {
                console.log($.ajaxSetup);
                $.ajaxSetup({async: false});
                var response = null;
                $.ajax({
                    type: 'post',
                    url: url, 
                    data: {
                        group_id: message.group_id,
                        msg: message.message,
                        sender: message.username,
                        nick: nickname,
                        member: member
                    },
                    async: false,
                    success: function(data, status){
                        console.log("got data finished");
                        console.log(status);
                        console.log(JSON.stringify(data));
                        if (status == 'success'){
                            response = data;
                        } else {
                            console.log("request api failed: " + data);
                        }
                    },
                    error: function(request, status, error){
                        console.log("request api failed, status: " + status + ", error: " + error);
                        //response = {tip: "request api failed, status: " + status + ", error: " + error};
                        response = {tip: "操作错误"};
                    }
                });
                return response;
            } catch (err) {
                console.log("evaluate failed: " + err);
            }
        }, url, message, member, nickname);
        return resp;
    };
};

// export handler
module.exports = DataHandler;
