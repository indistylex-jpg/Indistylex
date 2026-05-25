/* Indistylex Chatbot Widget JS */
(function () {
    'use strict';

    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose  = document.getElementById('chatbotClose');
    const chatInput     = document.getElementById('chatInput');
    const chatSendBtn   = document.getElementById('chatSendBtn');
    const chatMessages  = document.getElementById('chatMessages');
    const suggestionsEl = document.getElementById('chatSuggestions');

    if (!chatbotToggle) return;

    let isOpen = false;
    let isFirstOpen = true;

    // Toggle chat window
    chatbotToggle.addEventListener('click', function () {
        isOpen = !isOpen;
        chatbotWindow.classList.toggle('open', isOpen);
        if (isOpen && isFirstOpen) {
            isFirstOpen = false;
            addBotMessage(
                "Hi there! 👋 I'm your Indistylex assistant. How can I help you today?"
            );
            loadSuggestions();
            // Remove notification dot
            var dot = chatbotToggle.querySelector('.badge-dot');
            if (dot) dot.remove();
        }
        if (isOpen) chatInput.focus();
    });

    chatbotClose.addEventListener('click', function () {
        isOpen = false;
        chatbotWindow.classList.remove('open');
    });

    // Send message on Enter
    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    chatSendBtn.addEventListener('click', sendMessage);

    function sendMessage() {
        var text = chatInput.value.trim();
        if (!text) return;

        addUserMessage(text);
        chatInput.value = '';
        showTyping();

        var csrfToken = document.querySelector('meta[name="csrf-token"]');

        fetch('/chatbot/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken ? csrfToken.content : '',
            },
            body: JSON.stringify({ message: text }),
        })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            hideTyping();
            addBotMessage(data.reply || "Sorry, something went wrong.");
        })
        .catch(function () {
            hideTyping();
            addBotMessage("Sorry, I couldn't connect. Please try again.");
        });
    }

    function addUserMessage(text) {
        var div = document.createElement('div');
        div.className = 'chat-msg user';
        div.textContent = text;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function addBotMessage(text) {
        var div = document.createElement('div');
        div.className = 'chat-msg bot';
        div.innerHTML = formatMessage(text);
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function formatMessage(text) {
        // Convert **bold** to <strong>
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Convert [link text](url) to <a>
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
        // Convert bullet points
        text = text.replace(/^• /gm, '&bull; ');
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        return text;
    }

    function showTyping() {
        var div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typingIndicator';
        div.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function hideTyping() {
        var el = document.getElementById('typingIndicator');
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function loadSuggestions() {
        fetch('/chatbot/suggestions')
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.suggestions && suggestionsEl) {
                    suggestionsEl.innerHTML = '';
                    data.suggestions.forEach(function (s) {
                        var chip = document.createElement('span');
                        chip.className = 'chip';
                        chip.textContent = s;
                        chip.addEventListener('click', function () {
                            chatInput.value = s;
                            sendMessage();
                        });
                        suggestionsEl.appendChild(chip);
                    });
                }
            })
            .catch(function () {});
    }
})();
