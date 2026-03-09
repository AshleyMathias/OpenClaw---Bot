// Generate session ID
const sessionId = "user_" + Math.floor(Math.random() * 10000);

// API Base URL
const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const fileInput = document.getElementById("file-input");
const uploadStatus = document.getElementById("upload-status");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const closeSidebarBtn = document.getElementById("close-sidebar-btn");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const micBtn = document.getElementById("mic-btn");       // STT only
const vaBtn = document.getElementById("va-btn");           // Full voice assistant (continuous loop)
const voiceBanner = document.getElementById("voice-banner");
const voiceBannerText = document.getElementById("voice-banner-text");
const voiceStopBtn = document.getElementById("voice-stop-btn");

// Tracks whether current message came from Voice Assistant (auto-speak reply)
let voiceTriggered = false;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    messageInput.focus();
});

// Send Message Function
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = "";
    sendBtn.disabled = true;

    // Add user message to chat
    addMessage(message, "user");

    // Show typing indicator
    showTypingIndicator();

    try {
        // Call API - using query params as per current backend
        const params = new URLSearchParams({
            message: message,
            session_id: sessionId
        });

        const response = await fetch(`${API_BASE_URL}/chat?${params.toString()}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        removeTypingIndicator();

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const aiResponse = data.response || "No response from the assistant.";

        // Add AI response to chat
        addMessage(aiResponse, "ai");

        // If the question came from voice, speak the response back
        if (voiceTriggered) {
            voiceTriggered = false;
            speakResponse(aiResponse);
        }

    } catch (error) {
        removeTypingIndicator();
        console.error("Error sending message:", error);
        addMessage("Sorry, I couldn't process your request. Please make sure the backend is running.", "ai", true);
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// Format timestamp helper
function getTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Add Message to Chat
function addMessage(text, type, isError = false) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector(".welcome-message");
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    if (isError) {
        bubble.classList.add("error-message");
    }

    // Check if response contains a chart path
    if (type === "ai" && text.includes("charts/")) {
        console.log("Chart detected in response:", text);
        // Extract chart path (e.g., "charts/employee_distribution.png")
        // Handle both plain text and markdown link formats: [text](charts/file.png)
        // Match charts/ followed by valid filename characters and image extension
        // Use a capturing group to ensure we only get the valid path
        const chartMatch = text.match(/(charts\/[a-zA-Z0-9_.-]+\.(?:png|jpg|jpeg|svg|gif|webp))/i);
        if (chartMatch) {
            const chartPath = chartMatch[0];
            console.log("Extracted chart path:", chartPath);
            // Extract filename from path (just the filename, no path)
            // Trim to remove any whitespace or hidden characters
            let fullFilename = chartPath.split("/").pop().trim();
            // Extract just the filename with extension using strict regex
            // This ensures we only get valid filename characters, no parentheses or other punctuation
            let filename;
            const filenameMatch = fullFilename.match(/^([a-zA-Z0-9_.-]+\.(png|jpg|jpeg|svg|gif|webp))$/i);
            if (filenameMatch) {
                filename = filenameMatch[1];
            } else {
                // Fallback: try to extract just the base filename and extension
                // This handles cases where there might be trailing characters
                const fallbackMatch = fullFilename.match(/^([a-zA-Z0-9_.-]+)\.(png|jpg|jpeg|svg|gif|webp)/i);
                if (fallbackMatch) {
                    filename = `${fallbackMatch[1]}.${fallbackMatch[2]}`;
                } else {
                    // If we can't extract a valid filename, fall back to text display
                    bubble.textContent = text;
                    messageDiv.appendChild(bubble);
                    chatMessages.appendChild(messageDiv);
                    scrollToBottom();
                    return;
                }
            }
            // Build full image URL - use filename directly (no encoding needed for valid filenames)
            const imageUrl = `${API_BASE_URL}/charts/${filename}`;
            console.log("Built image URL:", imageUrl);
            
            // Add class to message div for chart styling
            messageDiv.classList.add("has-chart");
            
            // Extract text before chart path (if any)
            // Remove markdown link syntax if present
            let textBeforeChart = text.substring(0, text.indexOf(chartPath)).trim();
            // Clean up markdown link syntax like "[here]("
            textBeforeChart = textBeforeChart.replace(/\[([^\]]+)\]\(?$/, '$1').trim();
            
            // Add text before chart if it exists
            if (textBeforeChart) {
                const textNode = document.createTextNode(textBeforeChart);
                bubble.appendChild(textNode);
            }
            
            // Create chart container for dashboard styling
            const chartContainer = document.createElement("div");
            chartContainer.className = "chart-container";
            
            // Create image element
            const img = document.createElement("img");
            img.src = imageUrl;
            img.className = "chart-image";
            img.alt = "Chart";
            
            // Add error handling for image loading
            img.onerror = function() {
                console.error("Failed to load chart image:", imageUrl);
                // Show error message
                const errorText = document.createTextNode(" (Chart image could not be loaded)");
                chartContainer.appendChild(errorText);
                chartContainer.style.color = "#ef4444";
            };
            
            img.onload = function() {
                console.log("Chart image loaded successfully:", imageUrl);
            };
            
            // Add image to container, then container to bubble
            chartContainer.appendChild(img);
            bubble.appendChild(chartContainer);
        } else {
            // Fallback to text if extraction fails
            bubble.textContent = text;
        }
    } else {
        // Normal text response
        bubble.textContent = text;
    }

    // Wrap bubble + meta in inner container
    const inner = document.createElement("div");
    inner.className = "message-inner";
    inner.appendChild(bubble);

    // Meta row: timestamp + copy button (AI messages only)
    const meta = document.createElement("div");
    meta.className = "message-meta";

    const timestamp = document.createElement("span");
    timestamp.className = "message-timestamp";
    timestamp.textContent = getTimestamp();
    meta.appendChild(timestamp);

    if (type === "ai" && !isError) {
        const copyBtn = document.createElement("button");
        copyBtn.className = "copy-btn";
        copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
        copyBtn.addEventListener("click", () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.textContent = "Copied!";
                copyBtn.classList.add("copied");
                setTimeout(() => {
                    copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
                    copyBtn.classList.remove("copied");
                }, 2000);
            });
        });
        meta.appendChild(copyBtn);
    }

    inner.appendChild(meta);
    messageDiv.appendChild(inner);
    chatMessages.appendChild(messageDiv);

    // Auto scroll to bottom
    scrollToBottom();
}

// Show Typing Indicator
function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message ai";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// Remove Typing Indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll to Bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// New Chat Function
function newChat() {
    // Clear chat messages
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to OpenClaw AI</h2>
            <p>Ask me anything or upload a document to get started.</p>
        </div>
    `;
    
    // Clear upload status
    uploadStatus.textContent = "";
    uploadStatus.className = "upload-status";
    
    // Clear file input
    fileInput.value = "";
    
    // Focus on input
    messageInput.focus();
}

// Upload File Function
async function uploadFile(file) {
    if (!file) return;

    // Validate file type
    const validTypes = [".txt", ".pdf", ".docx"];
    const fileExtension = "." + file.name.split(".").pop().toLowerCase();

    if (!validTypes.includes(fileExtension)) {
        uploadStatus.textContent = "Unsupported file type. Please upload .txt, .pdf, or .docx files.";
        uploadStatus.className = "upload-status error";
        return;
    }

    // Show upload status
    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = "upload-status";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || "Upload failed");
        }

        const data = await response.json();
        const message = data.message || "File uploaded successfully";

        uploadStatus.textContent = message;
        uploadStatus.className = "upload-status success";

        // Show success message in chat
        addMessage(`✅ ${message}`, "ai");

        // Clear status after 3 seconds
        setTimeout(() => {
            uploadStatus.textContent = "";
            uploadStatus.className = "upload-status";
        }, 3000);

    } catch (error) {
        console.error("Upload error:", error);
        uploadStatus.textContent = "Upload failed. Please try again.";
        uploadStatus.className = "upload-status error";
        addMessage("❌ File upload failed. Please make sure the backend is running.", "ai", true);
    }
}

// Event Listeners
sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

newChatBtn.addEventListener("click", newChat);

fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
});

// Prevent form submission on Enter in file input
fileInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
    }
});

// Sidebar Toggle Logic
function toggleSidebar() {
    if (window.innerWidth <= 768) {
        // Mobile behavior
        sidebar.classList.toggle("open");
        sidebarOverlay.classList.toggle("show");
    } else {
        // Desktop behavior
        sidebar.classList.toggle("collapsed");
    }
}

function closeSidebar() {
    if (window.innerWidth <= 768) {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("show");
    }
}

sidebarToggle.addEventListener("click", toggleSidebar);
closeSidebarBtn.addEventListener("click", closeSidebar);
sidebarOverlay.addEventListener("click", closeSidebar);

// Close sidebar on window resize if switching from mobile to desktop
window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove("open");
        sidebarOverlay.classList.remove("show");
    }
});

// ══════════════════════════════════════════════════════════════════════════
// 1.  MIC BUTTON — Speech-to-text only. Fills the input box. User sends manually.
// ══════════════════════════════════════════════════════════════════════════
(function initMicDictation() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { micBtn.style.display = "none"; return; }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    let active = false;

    recognition.onresult = (event) => {
        let t = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            t += event.results[i][0].transcript;
        }
        messageInput.value = t;
    };

    recognition.onend = () => {
        active = false;
        micBtn.classList.remove("recording");
        messageInput.focus();
    };

    recognition.onerror = () => {
        active = false;
        micBtn.classList.remove("recording");
    };

    micBtn.addEventListener("click", () => {
        if (active) {
            recognition.stop();
        } else {
            active = true;
            messageInput.value = "";
            micBtn.classList.add("recording");
            recognition.start();
        }
    });
})();


// ══════════════════════════════════════════════════════════════════════════
// 2.  VOICE ASSISTANT BUTTON — Continuous loop: listen → send → speak → listen…
//     Runs until the user clicks the button again or presses Stop.
// ══════════════════════════════════════════════════════════════════════════
(function initVoiceAssistant() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { vaBtn.style.display = "none"; return; }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;   // one utterance at a time; we restart manually
    recognition.interimResults = true;
    recognition.lang = "en-US";
    let vaActive = false;

    // ── Banner helpers ────────────────────────────────────────────────────
    function showBanner(state) {
        voiceBanner.classList.remove("hidden", "speaking");
        if (state === "listening") {
            voiceBannerText.textContent = "Listening… speak now";
        } else if (state === "thinking") {
            voiceBannerText.textContent = "Processing your request…";
        } else if (state === "speaking") {
            voiceBanner.classList.add("speaking");
            voiceBannerText.textContent = "OpenClaw is speaking…";
        }
    }

    // ── Stop everything ───────────────────────────────────────────────────
    function stopVA() {
        vaActive = false;
        voiceTriggered = false;
        try { recognition.abort(); } catch (_) {}
        voiceBanner.classList.add("hidden");
        vaBtn.classList.remove("active");
        vaBtn.title = "Voice Assistant — continuously listens and speaks until stopped";
    }

    // ── Start a single listen cycle ───────────────────────────────────────
    function listenCycle() {
        if (!vaActive) return;
        messageInput.value = "";
        showBanner("listening");
        try { recognition.start(); } catch (_) {}
    }

    // ── Toggle VA on button click ─────────────────────────────────────────
    vaBtn.addEventListener("click", () => {
        if (vaActive) {
            stopVA();
        } else {
            vaActive = true;
            vaBtn.classList.add("active");
            vaBtn.title = "Stop Voice Assistant";
            listenCycle();
        }
    });

    // ── Stop button in the banner ─────────────────────────────────────────
    voiceStopBtn.addEventListener("click", stopVA);

    // ── Capture speech result ─────────────────────────────────────────────
    recognition.onresult = (event) => {
        let t = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            t += event.results[i][0].transcript;
        }
        messageInput.value = t;
    };

    // ── Utterance finished — send if we got text, else re-listen ─────────
    recognition.onend = () => {
        if (!vaActive) return;
        const text = messageInput.value.trim();
        if (text) {
            showBanner("thinking");
            voiceTriggered = true;   // tells sendMessage to call speakResponse
            sendMessage();           // after send, speakResponse → restarts loop
        } else {
            // No speech detected, just listen again
            setTimeout(listenCycle, 400);
        }
    };

    recognition.onerror = (e) => {
        if (e.error === "not-allowed") {
            voiceBannerText.textContent = "Microphone access denied.";
            setTimeout(stopVA, 2500);
        } else if (e.error === "no-speech") {
            // Silently restart
            if (vaActive) setTimeout(listenCycle, 400);
        } else {
            // On other errors keep trying unless user stopped
            if (vaActive) setTimeout(listenCycle, 1000);
        }
    };

    // Expose helpers for speakResponse
    window._vaShowBanner = showBanner;
    window._vaStop = stopVA;
    window._vaListenCycle = listenCycle;
    window._vaIsActive = () => vaActive;
})();


// ── TTS: send AI text to backend /speak, then restart listening loop ────────
async function speakResponse(text) {
    const cleanText = text
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .replace(/charts\/[a-zA-Z0-9_.-]+\.(?:png|jpg|jpeg)/gi, "")
        .trim();

    if (!cleanText) {
        // Nothing to speak — restart listening immediately if VA still active
        if (window._vaIsActive && window._vaIsActive()) {
            setTimeout(window._vaListenCycle, 400);
        }
        return;
    }

    if (window._vaShowBanner) window._vaShowBanner("speaking");

    // Estimate reading time so we can restart listening after TTS finishes
    const wordCount = cleanText.split(/\s+/).length;
    const estimatedMs = Math.max(2000, (wordCount / 2.5) * 1000);

    try {
        await fetch(`${API_BASE_URL}/speak`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: cleanText })
        });
    } catch (e) {
        console.error("[VA] /speak request failed:", e);
    } finally {
        // After speaking (estimated time), restart the listen cycle if VA is still active
        setTimeout(() => {
            if (window._vaIsActive && window._vaIsActive()) {
                window._vaListenCycle();
            } else if (window._vaStop) {
                window._vaStop();
            }
        }, estimatedMs);
    }
}
