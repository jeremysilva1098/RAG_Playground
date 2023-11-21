// Grabbing DOM elements
var userInput = document.getElementById('userInput');
var sendButton = document.getElementById('sendButton');
var rerunButton = document.getElementById('rerunButton');
var messagesDiv = document.getElementById('messages');
var ragDropdown = document.getElementById("rag-dropdown");
var limitDropdown = document.getElementById("limit-dropdown");
var cosineDropdown = document.getElementById("cosine-threshold-dropdown");
// send button listener
sendButton.addEventListener('click', function () {
    var userMessage = userInput.value.trim();
    var ragApproach = ragDropdown.value;
    var limit = limitDropdown.value;
    var cosineThreshold = cosineDropdown.value;
    if (userMessage) {
        // Append user's message
        var userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);
        // Add "thinking" message
        var thinkingMsgDiv_1 = document.createElement('div');
        thinkingMsgDiv_1.className = 'message thinking-msg';
        thinkingMsgDiv_1.textContent = "RAG Executing with ".concat(ragApproach, " strategy...");
        messagesDiv.appendChild(thinkingMsgDiv_1);
        // Make an API call
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: "user_message=".concat(encodeURIComponent(userMessage), "&rag_strategy=").concat(encodeURIComponent(ragApproach), "&limit=").concat(encodeURIComponent(limit), "&cosine_threshold=").concat(encodeURIComponent(cosineThreshold))
        }).then(function (response) { return response.json(); })
            .then(function (data) {
            // Remove "thinking" message
            messagesDiv.removeChild(thinkingMsgDiv_1);
            var botMsgDiv = document.createElement('div');
            botMsgDiv.className = 'message sys-msg';
            botMsgDiv.innerHTML = data.response; // Use innerHTML instead of textContent
            messagesDiv.appendChild(botMsgDiv);
            if (data.steps) {
                var stepsMsgDiv = document.createElement('div');
                stepsMsgDiv.className = 'message steps-msg';
                stepsMsgDiv.innerHTML = '<b>Rag Actions:</b><br>' + JSON.stringify(data.steps, null, 2);
                messagesDiv.appendChild(stepsMsgDiv);
            }
        });
    }
    // Clear the input
    userInput.value = '';
});
// rerun button listener
rerunButton.addEventListener('click', function () {
    // the 3rd from last message is the user's last message
    var userMessage = messagesDiv.childNodes[messagesDiv.childNodes.length - 3].textContent;
    var ragApproach = ragDropdown.value;
    var limit = limitDropdown.value;
    var cosineThreshold = cosineDropdown.value;
    if (userMessage) {
        // Append the user's message
        var userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);
        // Add a "thinking" message
        var thinkingMsgDiv_2 = document.createElement('div');
        thinkingMsgDiv_2.className = 'message thinking-msg';
        thinkingMsgDiv_2.textContent = "Reruning Query: RAG Executing with ".concat(ragApproach, " strategy...");
        messagesDiv.appendChild(thinkingMsgDiv_2);
        // Make an API call
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: "user_message=".concat(encodeURIComponent(userMessage), "&rag_strategy=").concat(encodeURIComponent(ragApproach), "&limit=").concat(encodeURIComponent(limit), "&cosine_threshold=").concat(encodeURIComponent(cosineThreshold))
        }).then(function (response) { return response.json(); }).then(function (data) {
            // Remove "thinking" message
            messagesDiv.removeChild(thinkingMsgDiv_2);
            var botMsgDiv = document.createElement('div');
            botMsgDiv.className = 'message sys-msg';
            botMsgDiv.innerHTML = data.response; // Use innerHTML instead of textContent
            messagesDiv.appendChild(botMsgDiv);
            if (data.steps) {
                var stepsMsgDiv = document.createElement('div');
                stepsMsgDiv.className = 'message steps-msg';
                stepsMsgDiv.innerHTML = '<b>Rag Actions:</b><br>' + JSON.stringify(data.steps, null, 2);
                messagesDiv.appendChild(stepsMsgDiv);
            }
        });
    }
});
