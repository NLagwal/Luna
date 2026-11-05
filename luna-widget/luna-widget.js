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
            const backendHost = window.location.hostname || "localhost";
            let sessionId = sessionStorage.getItem("luna_sid");
            if (!sessionId) {
                sessionId = "sess-" + Math.random().toString(36).substring(2) + Date.now();
                sessionStorage.setItem("luna_sid", sessionId);
            }

            const response = await fetch(`http://${backendHost}:5000/chat_stream`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message, session_id: sessionId })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";
            let citations = [];
            let trustLevel = null;

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
                            // Clear typing indicator on first token
                            if (fullText === "") msgDiv.innerHTML = "";
                            fullText += data.token;
                            msgDiv.innerHTML = formatText(fullText);
                        }
                        
                        if (data.citations) {
                            citations = data.citations;
                        }

                        if (data.trust_level) {
                            trustLevel = data.trust_level;
                        }

                        if (data.error) {
                            msgDiv.innerHTML = escapeHTML("Error: " + data.error);
                        }
                    } catch (e) {
                        console.error("JSON parse error in stream", e);
                    }
                }
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // After streaming finishes:
            // 1. Strip redundant trailing "Sources: ..." text emitted by LLM prompt
            const cleanedText = fullText.replace(/(?:\r?\n)+\s*(?:Sources|References|Citations)\s*:(?:\r?\n\s*[-*•]?\s*https?:\/\/[^\s]+)*\s*$/i, '');
            msgDiv.innerHTML = formatText(cleanedText);

            // 2. Append rich Trust Badge and Interactive Citation Pills
            const footerEl = renderFooter(citations, trustLevel);
            if (footerEl) {
                msgDiv.appendChild(footerEl);
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;

        } catch (error) {
            console.error("Luna AI Error:", error);
            msgDiv.innerHTML = escapeHTML("Could not connect to the assistant server.");
        }
    }

    function escapeHTML(str) {
        if (!str) return "";
        return String(str).replace(/[&<>'"]/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag));
    }

    function getCitationMeta(url) {
        try {
            const u = new URL(url);
            const path = u.pathname.toLowerCase();
            const search = u.search.toLowerCase();
            
            // Faculty Profile PDF or other PDFs
            if (path.endsWith(".pdf")) {
                if (path.includes("/profiles/")) return { label: "Faculty Profile (PDF)", icon: "📄" };
                if (path.includes("fee")) return { label: "Fee Structure (PDF)", icon: "📄" };
                if (path.includes("calendar")) return { label: "Academic Calendar (PDF)", icon: "📅" };
                if (path.includes("syllabus") || path.includes("curriculum")) return { label: "Syllabus (PDF)", icon: "📚" };
                
                const filename = path.split("/").pop().replace(/\.pdf$/i, "").replace(/[_-]/g, " ");
                const cleanName = filename.length > 24 ? filename.substring(0, 22) + "..." : filename;
                return { label: cleanName + " (PDF)", icon: "📄" };
            }
            
            // Faculty profile HTML
            if (path.includes("faculty.php") || search.includes("id=")) {
                return { label: "Faculty Profile", icon: "👤" };
            }
            
            // Departments
            if (path.includes("department")) {
                return { label: "Department Portal", icon: "🏛️" };
            }
            
            // Admissions / Fee
            if (path.includes("admission") || path.includes("fee")) {
                return { label: "Admissions & Fees", icon: "🎓" };
            }
            
            // Placements
            if (path.includes("placement")) {
                return { label: "Placements", icon: "💼" };
            }

            // General JUIT Page Path
            const segments = u.pathname.split("/").filter(s => s && s !== "index.html" && s !== "index.php");
            if (segments.length > 0) {
                const last = segments[segments.length - 1].replace(/\.(html|php)$/i, "").replace(/[_-]/g, " ");
                const cleanName = (last.charAt(0).toUpperCase() + last.slice(1)).trim();
                const shortName = cleanName.length > 24 ? cleanName.substring(0, 22) + "..." : cleanName;
                return { label: shortName, icon: "🔗" };
            }

            return { label: u.hostname.replace(/^www\./, ""), icon: "🔗" };
        } catch (e) {
            return { label: "Web Reference", icon: "🔗" };
        }
    }

    function renderFooter(citations, trustLevel) {
        // Filter and deduplicate citations
        const seen = new Set();
        const validCitations = [];
        if (Array.isArray(citations)) {
            for (const c of citations) {
                if (c && typeof c === "string" && c.startsWith("http") && !c.includes("juit_facts.json")) {
                    const trimmed = c.trim();
                    if (!seen.has(trimmed)) {
                        seen.add(trimmed);
                        validCitations.push(trimmed);
                    }
                }
            }
        }

        if (validCitations.length === 0 && !trustLevel) return null;

        const footer = document.createElement("div");
        footer.className = "luna-msg-footer";

        // Trust Level Badge
        if (trustLevel === "A") {
            const badge = document.createElement("div");
            badge.className = "luna-trust-badge luna-trust-a";
            badge.title = "Verified against canonical JUIT institutional records";
            badge.innerHTML = `<span class="luna-badge-icon">✓</span> Official JUIT Record`;
            footer.appendChild(badge);
        } else if (trustLevel === "B") {
            const badge = document.createElement("div");
            badge.className = "luna-trust-badge luna-trust-b";
            badge.title = "Retrieved via semantic search across university web documents";
            badge.innerHTML = `<span class="luna-badge-icon">ℹ</span> Supplementary Search`;
            footer.appendChild(badge);
        }

        // Interactive Citation Pills
        if (validCitations.length > 0) {
            const citContainer = document.createElement("div");
            citContainer.className = "luna-citations-container";
            
            const citHeader = document.createElement("div");
            citHeader.className = "luna-citations-label";
            citHeader.textContent = "Verified Sources:";
            citContainer.appendChild(citHeader);

            const citList = document.createElement("div");
            citList.className = "luna-citations-list";

            for (const url of validCitations) {
                const meta = getCitationMeta(url);
                const pill = document.createElement("a");
                pill.href = url;
                pill.target = "_blank";
                pill.rel = "noopener noreferrer";
                pill.className = "luna-citation-pill";
                pill.title = url;
                pill.innerHTML = `<span class="luna-pill-icon">${meta.icon}</span><span class="luna-pill-label">${escapeHTML(meta.label)}</span><span class="luna-pill-arrow">↗</span>`;
                citList.appendChild(pill);
            }
            citContainer.appendChild(citList);
            footer.appendChild(citContainer);
        }

        return footer;
    }

    function formatText(text) {
        if (!text) return "";
        // 1. Sanitize first to prevent XSS
        let str = escapeHTML(text);

        // 2. Fenced code blocks ```lang ... ```
        str = str.replace(/```([a-zA-Z0-9_]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="luna-code-block"><code>${code.trim()}</code></pre>`;
        });

        // 3. Inline code `...`
        str = str.replace(/`([^`\n]+)`/g, '<code class="luna-inline-code">$1</code>');

        // 4. Line-by-line block formatting (Headers, Lists, Blockquotes, Rules)
        const lines = str.split("\n");
        const formattedLines = [];

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];

            // Headers
            if (/^###\s+(.+)$/.test(line)) {
                formattedLines.push(line.replace(/^###\s+(.+)$/, '<div class="luna-h3">$1</div>'));
                continue;
            }
            if (/^##\s+(.+)$/.test(line)) {
                formattedLines.push(line.replace(/^##\s+(.+)$/, '<div class="luna-h2">$1</div>'));
                continue;
            }
            if (/^#\s+(.+)$/.test(line)) {
                formattedLines.push(line.replace(/^#\s+(.+)$/, '<div class="luna-h1">$1</div>'));
                continue;
            }

            // Horizontal rule
            if (/^(\-{3,}|\*{3,})$/.test(line.trim())) {
                formattedLines.push('<hr class="luna-hr" />');
                continue;
            }

            // Blockquote
            if (/^&gt;\s*(.+)$/.test(line)) {
                formattedLines.push(line.replace(/^&gt;\s*(.+)$/, '<div class="luna-blockquote">$1</div>'));
                continue;
            }

            // Bullet points: "* ", "- ", "• "
            const bulletMatch = line.match(/^(\s*)(?:[\*\-\•])\s+(.+)$/);
            if (bulletMatch) {
                const indent = bulletMatch[1].length > 1 ? " luna-bullet-indent" : "";
                formattedLines.push(`<div class="luna-bullet-item${indent}"><span class="luna-bullet-dot">•</span><span class="luna-bullet-content">${bulletMatch[2]}</span></div>`);
                continue;
            }

            // Numbered list: "1. ", "2. "
            const numMatch = line.match(/^(\s*)(\d+)\.\s+(.+)$/);
            if (numMatch) {
                const indent = numMatch[1].length > 1 ? " luna-bullet-indent" : "";
                formattedLines.push(`<div class="luna-num-item${indent}"><span class="luna-num-idx">${numMatch[2]}.</span><span class="luna-num-content">${numMatch[3]}</span></div>`);
                continue;
            }

            // Empty line spacing vs regular text line
            if (line.trim() === "") {
                formattedLines.push('<div class="luna-line-break"></div>');
            } else {
                formattedLines.push(`<div class="luna-line">${line}</div>`);
            }
        }

        str = formattedLines.join("");

        // 5. Inline formatting
        // Bold: **text** or __text__
        str = str.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        str = str.replace(/__([^_]+)__/g, '<strong>$1</strong>');

        // Italic: *text* or _text_
        str = str.replace(/(^|[^\*])\*([^*\n]+)\*([^\*]|$)/g, '$1<em>$2</em>$3');
        str = str.replace(/(^|[^_])_([^_\n]+)_([^_]|$)/g, '$1<em>$2</em>$3');

        // URLs (outside of attributes)
        str = str.replace(/(https?:\/\/[^\s<"']+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="luna-link">$1</a>');

        return str;
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

