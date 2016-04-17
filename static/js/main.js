$(document).ready(function() {

    function updateChoice(id, instance) {
        var $choice = $("#choice_" + id),
            $choiceText = $choice.find(".choice-text"),
            $choiceVotes = $choice.find(".votes");

        $choiceText.text(instance.choice_text);
        $choiceVotes.text(instance.votes);
    }

    function updateQuestion(id, instance) {
        var $question = $("#question_" + id),
            $questionText = $question.find(".question-text");

        $questionText.text(instance.question_text);
    }

    function addQuestion(instance) {
        var $emptyQuestion = $(".question_empty"),
            $newQuestion = $emptyQuestion.clone();

        $newQuestion.attr("id", "question_" + instance.id)
                    .find(".question-text").text(instance.question_text);
        $newQuestion.prependTo(".questions-container");
    }

    function messageProcess(message){
        var msgJSON = $.parseJSON(message),
            action = msgJSON.action.toLowerCase(),
            model = msgJSON.model.toLowerCase(),
            instance = msgJSON.instance,
            instanceID = instance.id;

        if ((model === "choice") && (action === "updated")) {
            updateChoice(instanceID, instance);
        } else

        if ((model === "question") && (action === "updated")) {
            updateQuestion(instanceID, instance);
        } else

        if ((model === "question") && (action === "created")) {
            addQuestion(instance);
        }

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
});

