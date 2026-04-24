// Luna Chat Widget JavaScript - Professional Streaming Version
(function() {
    // 1. Inject Stylesheet Link
    const styleLink = document.createElement("link");
    styleLink.rel = "stylesheet";
    styleLink.href = "/luna-widget/luna-style.css"; 
    document.head.appendChild(styleLink);

    // 2. Build Widget HTML Structure
    const widgetHTML = `
        <div id="luna-chat-wrapper">
            <div id="luna-chat-window" style="display: none;">
                <div id="luna-chat-header">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 10px; height: 10px; background: #2ecc71; border-radius: 50%; margin-right: 10px;"></div>
                        <span>Luna AI Assistant</span>
                    </div>
                    <div class="luna-header-controls">
                        <span id="luna-toggle-fullscreen" title="Fullscreen">⛶</span>
                        <span id="luna-close-chat" title="Close">×</span>
                    </div>
                </div>
                <div id="luna-chat-messages">
                    <div class="luna-msg luna-msg-luna">
                        Namaste! I am Luna. How can I help you today?
                    </div>
                </div>
                <div id="luna-chat-input-area">
                    <input type="text" id="luna-chat-input" placeholder="Ask me about JUIT..." />
                    <button id="luna-send-btn">➤</button>
                </div>
            </div>
            <div id="luna-chat-bubble" title="Chat with Luna">
                <span style="font-size: 32px; color: white;">💬</span>
            </div>
        </div>
    `;

    // 3. Append Widget to DOM
    const div = document.createElement("div");
    div.innerHTML = widgetHTML;
    document.body.appendChild(div);

    // 4. Element Selectors
    const chatWrapper = document.getElementById("luna-chat-wrapper");
    const chatBubble = document.getElementById("luna-chat-bubble");
    const chatWindow = document.getElementById("luna-chat-window");
    const closeChat = document.getElementById("luna-close-chat");
    const fullScreenBtn = document.getElementById("luna-toggle-fullscreen");
    const sendBtn = document.getElementById("luna-send-btn");
    const chatInput = document.getElementById("luna-chat-input");
    const chatMessages = document.getElementById("luna-chat-messages");

    // 5. Toggle Logic
    chatBubble.addEventListener("click", () => {
        chatWindow.style.display = (chatWindow.style.display === "none") ? "flex" : "none";
    });

    closeChat.addEventListener("click", () => {
        chatWindow.style.display = "none";
    });

    fullScreenBtn.addEventListener("click", () => {
        chatWindow.classList.toggle("fullscreen");
        fullScreenBtn.innerText = chatWindow.classList.contains("fullscreen") ? "❐" : "⛶";
    });

    // 6. Message Sending Logic (Streaming)
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Display User Message
        appendMessage(message, "luna-msg-user");
        chatInput.value = "";

        // Create Luna message container for streaming
        const lunaMsgId = "luna-stream-" + Date.now();
        const msgDiv = appendMessage("", "luna-msg-luna", lunaMsgId);
        
        // Show Typing indicator inside
        msgDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

        try {
            const response = await fetch("http://localhost:5000/chat_stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";
            let citations = [];

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n");

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        
                        if (data.token) {
                            // If this is the first token, clear typing indicator
                            if (fullText === "") msgDiv.innerHTML = "";
                            fullText += data.token;
                            msgDiv.innerHTML = formatText(fullText);
                        }
                        
                        if (data.citations) {
                            citations = data.citations;
                        }

                        if (data.error) {
                            msgDiv.innerHTML = "Error: " + data.error;
                        }
                    } catch (e) {
                        console.error("JSON parse error in stream", e);
                    }
                }
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // After streaming, append citations
            if (citations.length > 0 && citations[0] !== "juit_facts.json") {
                const citBox = document.createElement("div");
                citBox.className = "luna-citation-box";
                citBox.innerHTML = "Sources: " + citations.map(c => 
                    `<a href="${c}" target="_blank" class="luna-citation-link">[ref]</a>`
                ).join("");
                msgDiv.appendChild(citBox);
            }

        } catch (error) {
            console.error("Luna AI Error:", error);
            msgDiv.innerHTML = "Could not connect to the assistant server.";
        }
    }

    function formatText(text) {
        // Basic markdown-like formatting
        return text
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: inherit; text-decoration: underline;">$1</a>');
    }

    function appendMessage(text, className, id = null) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "luna-msg " + className;
        if (id) msgDiv.id = id;
        msgDiv.innerHTML = formatText(text);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    // 7. Event Handlers
    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
})();
