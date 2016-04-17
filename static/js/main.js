function messageProcess(message){
    console.log(message)
}

function websocketSubscribePollChanges(){

    var ws = new WebSocket("ws://0.0.0.0:8888/subscribe");
    ws.onopen = function() {
        console.log("Connected to WebSocket");
    };
    ws.onmessage = function(event) {
        messageProcess(event.data);
    };
    ws.onclose = function() {
        console.log("WebSocket connection closed");
    };
}

websocketSubscribePollChanges();
