const sessionId = "user_" + Math.floor(Math.random() * 10000);

function getChatBox() {
    return document.getElementById("chat-box");
}

function getInput() {
    return document.getElementById("user-input");
}

function getSendBtn() {
    return document.getElementById("send-btn");
}

function addMessage(text, type) {
    const chatBox = getChatBox();
    const wrap = document.createElement("div");
    wrap.className = "message " + type;
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = type === "user" ? "You" : "OpenClaw";
    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;
    wrap.appendChild(label);
    wrap.appendChild(bubble);
    chatBox.appendChild(wrap);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = getChatBox();
    const wrap = document.createElement("div");
    wrap.className = "message bot";
    wrap.id = "typing-indicator";
    wrap.innerHTML = '<div class="message-label">OpenClaw</div><div class="message-bubble typing-indicator"><span></span><span></span><span></span></div>';
    chatBox.appendChild(wrap);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

function showError(message) {
    const chatBox = getChatBox();
    const wrap = document.createElement("div");
    wrap.className = "message bot";
    const bubble = document.createElement("div");
    bubble.className = "message-bubble error-bubble";
    bubble.textContent = message || "Something went wrong. Please try again.";
    wrap.appendChild(bubble);
    chatBox.appendChild(wrap);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const input = getInput();
    const message = (input.value || "").trim();
    if (!message) return;

    const sendBtn = getSendBtn();
    addMessage(message, "user");
    input.value = "";
    sendBtn.disabled = true;
    showTypingIndicator();

    try {
        const params = new URLSearchParams({ message: message, session_id: sessionId });
        const response = await fetch("http://127.0.0.1:8000/chat?" + params.toString(), {
            method: "POST",
        });

        removeTypingIndicator();

        if (!response.ok) {
            showError("Request failed. Please check the connection and try again.");
            return;
        }

        const data = await response.json();
        const reply = data.response != null ? String(data.response) : "";
        if (reply) {
            addMessage(reply, "bot");
        } else {
            showError("No response from the assistant.");
        }
    } catch (err) {
        removeTypingIndicator();
        showError("Could not reach the server. Make sure the backend is running.");
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

getInput().addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
