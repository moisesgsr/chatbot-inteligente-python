#  RegAI: Chatbot Inteligente e Multifacetado com IA Gemini


## Visão Geral

O RegAI é um chatbot interativo desenvolvido em Python, alimentado pela IA Google Gemini 1.5 Flash. Sua principal força é ser um assistente multifacetado, capaz de conversar sobre diversos tópicos, adaptar-se a diferentes personas (tutor, amigo, programador, etc.) e integrar-se a APIs externas para informações em tempo real.

##  O que o RegAI Faz?

* Conversação Inteligente e Fluida: Mantém contexto e adapta a personalidade (tutor, amigo, psicólogo, etc.).
* Acesso a Ferramentas:
    * Clima: Informações meteorológicas (OpenWeatherMap).
    * Busca Web: Pesquisas na internet (Google Custom Search).
    * Data & Hora: Dados temporais.
    * Geração de Imagens (Simulada): Mostra capacidade de IA generativa.
* Gerenciador de Anotações: Salva e exibe notas persistentes.
* Design Intuitivo: Interface moderna e confortável para o usuário.

## 🛠️ Tecnologias Principais

* Python (Backend - Flask, Gemini SDK, requests)
* HTML, CSS, JavaScript (Frontend)
* APIs: Google Gemini, OpenWeatherMap, Google Custom Search.

## 🚀 Como Rodar (Passos Rápidos)

1.  Pré-requisitos: Python 3.x, **chaves de API** (Gemini, Google Custom Search, OpenWeatherMap).
2.  Clone o Repo: `git clone https://github.com/moisesgsr/chatbot-inteligente-python.git`
3.  Acesse a Pasta: `cd chatbot-inteligente-python`
4.  Crie & Ative o Ambiente Virtual: `python -m venv .venv` e ative (ex: `.venv\Scripts\Activate.ps1`).
5.  Instale Dependências: `pip install Flask requests google-generativeai google-api-python-client python-dotenv Flask-Cors`
6.  Configure o `.env`: Crie um arquivo `.env` na raiz do projeto com suas chaves:
    ```
    GEMINI_API_KEY="SUA_CHAVE_GEMINI_AQUI"
    GOOGLE_CSE_API_KEY="SUA_CHAVE_GOOGLE_CSE_API_KEY_AQUI"
    GOOGLE_CSE_CX_ID="SEU_CX_ID_DO_GOOGLE_CSE_AQUI"
    OPENWEATHER_API_KEY="SUA_CHAVE_OPENWEATHERMAP_AQUI"
    ```
7.  Execute: `python ChatBot.py`
8.  Acesse: Abra seu navegador em `http://127.0.0.1:8000`.

## 💡 Sobre o Desenvolvedor

Olá! Sou Moisés, Desenvolvedor Júnior com foco em Backend (Python/Flask) e Frontend (JavaScript). Minha paixão é criar soluções inteligentes e integradas, como o RegAI demonstra com a IA Gemini e diversas APIs. Sempre buscando aprender e crescer na área de tecnologia.

Vamos conectar!

## 📧 Contato

* **Email: richardmoisees@gmail.com
* **LinkedIn: https://www.linkedin.com/in/richardmoisees/
* **GitHub: https://github.com/moisesgsr
