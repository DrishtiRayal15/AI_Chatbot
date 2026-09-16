const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");
const newChatBtn = document.getElementById("newChatBtn");
const downloadBtn = document.getElementById("downloadBtn");
const themeToggle = document.getElementById("themeToggle");

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function currentTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, text, quickReplies) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role === "user" ? "user-message" : "bot-message"}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "user" ? "user-avatar" : "bot-avatar"}`;
  avatar.textContent = role === "user" ? "🧑" : "🤖";

  const col = document.createElement("div");
  col.className = "bubble-col";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  col.appendChild(bubble);

  const time = document.createElement("div");
  time.className = "timestamp";
  time.textContent = currentTime();
  col.appendChild(time);

  if (quickReplies && quickReplies.length > 0) {
    const qrWrap = document.createElement("div");
    qrWrap.className = "quick-replies";
    quickReplies.forEach((qr) => {
      const btn = document.createElement("button");
      btn.className = "quick-reply-btn";
      btn.textContent = qr;
      btn.addEventListener("click", () => sendMessage(qr));
      qrWrap.appendChild(btn);
    });
    col.appendChild(qrWrap);
  }

  wrapper.appendChild(avatar);
  wrapper.appendChild(col);
  chatWindow.appendChild(wrapper);
  scrollToBottom();
}

function setTyping(show) {
  typingIndicator.style.display = show ? "flex" : "none";
  if (show) scrollToBottom();
}

async function sendMessage(message) {
  addMessage("user", message);
  userInput.value = "";
  sendBtn.disabled = true;
  setTyping(true);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    await new Promise((r) => setTimeout(r, 400 + Math.random() * 400));

    setTyping(false);
    if (data.error) {
      addMessage("bot", "Sorry, something went wrong. Please try again.");
    } else {
      addMessage("bot", data.reply, data.quick_replies);
    }
  } catch (err) {
    setTyping(false);
    addMessage("bot", "⚠️ Could not reach the server. Is the Flask app running?");
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;
  sendMessage(message);
});

newChatBtn.addEventListener("click", async () => {
  await fetch("/clear", { method: "POST" });
  chatWindow.innerHTML = "";
  addMessage("bot", "New chat started! 👋 Ask me anything.", ["Tell me a joke", "What can you do?"]);
});

downloadBtn.addEventListener("click", () => {
  window.location.href = "/download";
});

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("light-theme");
  themeToggle.textContent = document.body.classList.contains("light-theme") ? "☀️" : "🌙";
});

userInput.focus();
