$(document).ready(function() {

    function updateChoice(instance) {
        var $choice = $("#choice_" + instance.id),
            $choiceText = $choice.find(".choice-text"),
            $choiceVotes = $choice.find(".votes");

        $choiceText.text(instance.choice_text);
        $choiceVotes.text(instance.votes);
    }

    function updateQuestion(instance) {
        var $question = $("#question_" + instance.id),
            $questionText = $question.find(".question-text");

        $questionText.text(instance.question_text);
    }

    function addQuestion(instance) {
        var $questions = $(".questions-container"),
            $emptyQuestion = $(".question_empty"),
            $newQuestion = $emptyQuestion.clone();

        $newQuestion.attr("id", "question_" + instance.id)
                    .removeClass("question_empty")
                    .find(".question-text").text(instance.question_text);
        $newQuestion.prependTo($questions);
    }

    function addChoice(instance) {
        var $choices = $("#question_" + instance.question).find(".choices"),
            $emptyChoice = $(".choice_empty"),
            $newChoice = $emptyChoice.clone();

        $newChoice.attr("id", "choice_" + instance.id)
                  .removeClass("choice_empty")
                  .find(".choice-text").text(instance.choice_text);
        $newChoice.find(".votes").text(instance.votes);
        $newChoice.appendTo($choices);
    }

    function delQuestion(instance) {
        $("#question_" + instance.id).remove();
    }

    function delChoice(instance) {
        $("#choice_" + instance.id).remove();
    }

    function logMessage(message) {
        $(".log").append("<li>" + message + "</li>");
    }

    function messageProcess(message){
        var msgJSON = $.parseJSON(message),
            action = msgJSON.action.toLowerCase(),
            model = msgJSON.model.toLowerCase(),
            instance = msgJSON.instance;

        logMessage(message);

        if ((model === "choice") && (action === "updated")) {
            updateChoice(instance);
        } else

        if ((model === "question") && (action === "updated")) {
            updateQuestion(instance);
        } else

        if ((model === "question") && (action === "created")) {
            addQuestion(instance);
        } else

        if ((model === "choice") && (action === "created")) {
            addChoice(instance);
        } else

        if ((model === "question") && (action === "deleted")) {
            delQuestion(instance);
        } else

        if ((model === "choice") && (action === "deleted")) {
            delChoice(instance);
        }
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

