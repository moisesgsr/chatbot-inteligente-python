document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Remove a chave da API do OpenWeatherMap daqui! Ela agora está no backend Python.
    // const OPENWEATHER_API_KEY = 'eadf0878340a1194001f2b18a40f2c47'; // REMOVA OU COMENTE ESTA LINHA!

    // Função para adicionar mensagem ao chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Rola para o final
    }

    // >>> MUDANÇA CRÍTICA AQUI: getBotResponse agora chama o backend <<<
    async function getBotResponse(message) {
        try {
            // URL do seu backend Flask (certifique-se de que ele está rodando na porta 8000)
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
            return data.response; // O backend deve retornar um JSON com a chave 'response'

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
            userInput.value = ''; // Limpa o input

            // Adiciona uma mensagem de "digitando..." ou "pensando..."
            // Isso melhora a experiência do usuário enquanto espera a resposta do backend.
            const thinkingMessageId = 'thinking-message';
            addMessage('RegAI está pensando...', 'bot'); // Adiciona uma mensagem temporária
            chatBox.lastChild.id = thinkingMessageId; // Dá um ID para remover depois

            const botResponse = await getBotResponse(message);

            // Remove a mensagem temporária
            const thinkingMessage = document.getElementById(thinkingMessageId);
            if (thinkingMessage) {
                thinkingMessage.remove();
            }
            
            addMessage(botResponse, 'bot');
        }
    });

    // Evento de tecla 'Enter' no input
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Impede a quebra de linha padrão do Enter
            sendButton.click(); // Simula o clique do botão enviar
        }
    });

    // Mensagem de boas-vindas inicial (esta virá do backend na primeira vez)
    // REMOVA esta linha se a primeira mensagem já estiver vindo do backend automaticamente
    // (o que deveria acontecer se o chat_history inicial do Gemini estiver configurado corretamente)
    // Se você ainda quer uma mensagem no frontend no carregamento da página,
    // pode fazer uma chamada inicial ao backend aqui:
    // async function sendInitialMessage() {
    //     const initialBotResponse = await getBotResponse("iniciar conversa"); // Envie uma mensagem dummy para iniciar
    //     addMessage(initialBotResponse, 'bot');
    // }
    // sendInitialMessage();
    // Alternativamente, se a primeira mensagem do `chat_history` no Python já aparece, você não precisa de nada aqui.
    // O mais simples é deixar o Python lidar com a primeira mensagem para manter o controle centralizado.
});