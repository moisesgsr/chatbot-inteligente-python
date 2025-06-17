document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Função para adicionar mensagem ao chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Rola para o final
    }

    
    async function getBotResponse(message) {
        try {
            
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erro do servidor: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            return data.response; 

        } catch (error) {
            console.error("Erro ao comunicar com o backend:", error);
            return "Desculpe, não consegui me comunicar com o RegAI agora. O servidor pode estar offline. 😔";
        }
    }

    // Evento de clique do botão enviar
    sendButton.addEventListener('click', async () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            userInput.value = ''; 

           
            const thinkingMessageId = 'thinking-message';
            addMessage('RegAI está pensando...', 'bot'); 
            chatBox.lastChild.id = thinkingMessageId; 

            const botResponse = await getBotResponse(message);

            // Remove a mensagem temporária
            const thinkingMessage = document.getElementById(thinkingMessageId);
            if (thinkingMessage) {
                thinkingMessage.remove();
            }
            
            addMessage(botResponse, 'bot');
        }
    });


    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            sendButton.click(); 
        }
    });

});
