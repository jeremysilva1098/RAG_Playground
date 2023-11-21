
// Grabbing DOM elements
const userInput: HTMLInputElement = <HTMLInputElement>document.getElementById('userInput');
const sendButton: HTMLElement = document.getElementById('sendButton');
const rerunButton: HTMLElement = document.getElementById('rerunButton');
const messagesDiv: HTMLElement = document.getElementById('messages');
const ragDropdown = document.getElementById("rag-dropdown") as HTMLSelectElement;
const limitDropdown = document.getElementById("limit-dropdown") as HTMLSelectElement;
const cosineDropdown = document.getElementById("cosine-threshold-dropdown") as HTMLSelectElement;

// send button listener
sendButton.addEventListener('click', () => {
    let userMessage = userInput.value.trim();
    let ragApproach = ragDropdown.value;
    let limit = limitDropdown.value;
    let cosineThreshold = cosineDropdown.value;
    
    if (userMessage) {
        // Append user's message
        let userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);

        // Add "thinking" message
        let thinkingMsgDiv = document.createElement('div');
        thinkingMsgDiv.className = 'message thinking-msg';
        thinkingMsgDiv.textContent = `RAG Executing with ${ragApproach} strategy...`;
        messagesDiv.appendChild(thinkingMsgDiv);

        // Make an API call
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_message=${encodeURIComponent(userMessage)}&rag_strategy=${encodeURIComponent(ragApproach)}&limit=${encodeURIComponent(limit)}&cosine_threshold=${encodeURIComponent(cosineThreshold)}`
        }).then(response => response.json())
            .then(data => {
                // Remove "thinking" message
                messagesDiv.removeChild(thinkingMsgDiv);

                let botMsgDiv = document.createElement('div');
                botMsgDiv.className = 'message sys-msg';
                botMsgDiv.innerHTML = data.response; // Use innerHTML instead of textContent
                messagesDiv.appendChild(botMsgDiv);

                if (data.steps) {
                let stepsMsgDiv = document.createElement('div');
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
rerunButton.addEventListener('click', () => {
    // the 3rd from last message is the user's last message
    let userMessage = messagesDiv.childNodes[messagesDiv.childNodes.length - 3].textContent;
    let ragApproach = ragDropdown.value;
    let limit = limitDropdown.value;
    let cosineThreshold = cosineDropdown.value;

    if (userMessage) {
        // Append the user's message
        let userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'message user-msg';
        userMsgDiv.textContent = userMessage;
        messagesDiv.appendChild(userMsgDiv);

        // Add a "thinking" message
        let thinkingMsgDiv = document.createElement('div');
        thinkingMsgDiv.className = 'message thinking-msg';
        thinkingMsgDiv.textContent = `Reruning Query: RAG Executing with ${ragApproach} strategy...`;
        messagesDiv.appendChild(thinkingMsgDiv);

        // Make an API call
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_message=${encodeURIComponent(userMessage)}&rag_strategy=${encodeURIComponent(ragApproach)}&limit=${encodeURIComponent(limit)}&cosine_threshold=${encodeURIComponent(cosineThreshold)}`
        }).then(response => response.json()).then(data => {
            // Remove "thinking" message
            messagesDiv.removeChild(thinkingMsgDiv);

            let botMsgDiv = document.createElement('div');
            botMsgDiv.className = 'message sys-msg';
            botMsgDiv.innerHTML = data.response; // Use innerHTML instead of textContent
            messagesDiv.appendChild(botMsgDiv);

            if (data.steps) {
                let stepsMsgDiv = document.createElement('div');
                stepsMsgDiv.className = 'message steps-msg';
                stepsMsgDiv.innerHTML = '<b>Rag Actions:</b><br>' + JSON.stringify(data.steps, null, 2);
                messagesDiv.appendChild(stepsMsgDiv);
            }
    });
    }
});
