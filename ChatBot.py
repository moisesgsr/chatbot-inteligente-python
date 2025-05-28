import json
import google.generativeai as genai

# Configuração da API do Gemini
API_KEY = "AIzaSyBwk_ov_5qAE6JMAjiPgVqNDrcboq8S13U" 
genai.configure(api_key=API_KEY)

# Configuração do Modelo Gemini e Personalidade
model = genai.GenerativeModel('gemini-1.5-flash-latest')
PROMPT_PERSONALIDADE = (
    "Você é um assistente de chatbot amigável e prestativo, especializado em conceitos "
    "de programação e temas relacionados à educação física, saúde e bem-estar. "
    "Seja conciso e direto, mas sempre educado. Se a pergunta for sobre saúde, "
    "lembre-se de enfatizar que você não é um profissional de saúde e que "
    "sempre se deve buscar um especialista.\n\n"
)

# Nome do arquivo para persistência de dados
NOME_ARQUIVO_ANOTACOES = "anotacoes_chatbot.json"

# --- Seção de Funções ---
def carregar_anotacoes():
    """Carrega as anotações de um arquivo JSON."""
    try:
        with open(NOME_ARQUIVO_ANOTACOES, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Chatbot: Atenção: O arquivo '{NOME_ARQUIVO_ANOTACOES}' "
              "está corrompido. Criando um novo.")
        return []

def salvar_anotacoes(anotacoes):
    """Salva as anotações em um arquivo JSON."""
    with open(NOME_ARQUIVO_ANOTACOES, 'w', encoding='utf-8') as f:
        json.dump(anotacoes, f, indent=4, ensure_ascii=False)

def mostrar_ajuda(nome_usuario_param):
    """Exibe a lista de comandos que o chatbot entende."""
    print(f"Chatbot: Olá, {nome_usuario_param}! Aqui estão algumas coisas que posso fazer:")
    print("- Dizer 'ajuda' ou 'comandos' (para ver esta lista)")
    print("- 'Adicionar anotação', 'ver anotações', 'remover anotação'")
    print("- Digite 'sair' para encerrar a conversa.")
    print("\nChatbot (IA): Além disso, você pode me perguntar sobre qualquer coisa!")

# --- Inicialização do Chatbot ---
print("Olá! Eu sou um chatbot simples."
      " Digite 'sair' a qualquer momento para encerrar.")

# nome do usuário
nome_usuario = input("Chatbot: Antes de começarmos, como você se chama? ")
print(f"Chatbot: Olá {nome_usuario}, um prazer conversar com você!")

# Pausa para iniciar o loop principal
input("Chatbot: Tudo pronto! Pressione ENTER para começar a conversar: ")

# Carrega as anotações ao iniciar
lista_de_anotacoes = carregar_anotacoes()

# --- Loop Principal do Chatbot (Versão Otimizada/Focada) ---
while True:
    print("\nChatbot: Estou ouvindo...")
    entrada_do_usuario = input(f"{nome_usuario}: ")

    # Comandos Essenciais (Prioridade Alta)
    if entrada_do_usuario.lower() == "sair":
        salvar_anotacoes(lista_de_anotacoes) # Salva anotações ao sair
        print(f"Chatbot: Até logo, {nome_usuario}!")
        break
    elif entrada_do_usuario.lower() == "ajuda" or entrada_do_usuario.lower() == "comandos":
        mostrar_ajuda(nome_usuario)
    # Fallback para IA (se nenhum comando/condição for reconhecido)
    else:
        try:
            prompt_para_ia = PROMPT_PERSONALIDADE + entrada_do_usuario
            print(f"Chatbot: Pensando... (usando IA)")
            response = model.generate_content(prompt_para_ia)
            if response.text:
                print(f"Chatbot (IA): {response.text}")
            else:
                print(f"Chatbot (IA): Não consegui gerar uma resposta. Tente novamente.")
        except Exception as e:
            print(f"Chatbot (ERRO IA): Houve um problema ao conectar com a IA. "
                  f"Erro: {e}. Verifique sua chave de API ou conexão com a internet.")