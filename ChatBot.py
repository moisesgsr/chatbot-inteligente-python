import json
import locale
from datetime import datetime, date, time
from googleapiclient.discovery import build
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_CX_ID = os.getenv("GOOGLE_CSE_CX_ID")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GEMINI_API_KEY:
    print("ERRO: Variável de ambiente GEMINI_API_KEY não definida. O chatbot Gemini não funcionará. Certifique-se de que está no seu arquivo .env.")
if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX_ID:
    print("AVISO: Variáveis de ambiente GOOGLE_CSE_API_KEY ou GOOGLE_CSE_CX_ID não definidas. A busca web pode não funcionar. Verifique seu arquivo .env.")
if not OPENWEATHER_API_KEY:
    print("AVISO: Variável de ambiente OPENWEATHER_API_KEY não definida. A ferramenta de clima não funcionará. Verifique seu arquivo .env.")

# === DEFINIÇÃO DAS FERRAMENTAS DO GEMINI ===

def get_current_date_tool():
    hoje = date.today()
    print(f"DEBUG (TOOL - get_current_date_tool): Objeto date: {hoje}, Formatado: {hoje.strftime('%d/%m/%Y')}")
    return hoje.strftime("%d/%m/%Y")

def get_current_time_tool():
    agora = datetime.now()
    print(f"DEBUG (TOOL - get_current_time_tool): Objeto datetime: {agora}, Hora formatada: {agora.strftime('%H:%M:%S')}")
    return agora.strftime("%H:%M:%S")

def get_current_datetime_tool():
    agora = datetime.now()
    return agora.strftime("%d/%m/%Y %H:%M:%S")

def get_current_day_of_week_tool():
    hoje = date.today()
    return hoje.strftime("%A")

def get_weather_tool(city: str):
    if not OPENWEATHER_API_KEY:
        print("ERRO (TOOL - get_weather_tool): OPENWEATHER_API_KEY não configurada. Não é possível buscar clima.")
        return "Desculpe, a ferramenta de clima não está configurada corretamente. Por favor, avise o desenvolvedor."

    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    print(f"DEBUG (TOOL - get_weather_tool): Buscando clima para '{city}' em: {api_url}")
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        city_name = data.get('name', city)
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed_ms = data['wind']['speed']
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1)

        result = (
            f"O clima em {city_name} está {description}, com temperatura de {temp}°C (sensação de {feels_like}°C). "
            f"Umidade: {humidity}%. Vento: {wind_speed_kmh} km/h."
        )
        print(f"DEBUG (TOOL - get_weather_tool): Resultado do clima: {result}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"ERRO (TOOL - get_weather_tool): Erro na requisição à OpenWeatherMap API para '{city}': {e}")
        if response.status_code == 404:
            return f"Não foi possível encontrar dados de clima para '{city}'. Por favor, verifique o nome da cidade e tente novamente."
        return f"Desculpe, não foi possível obter os dados do clima no momento. Erro de conexão ou na API: {type(e).__name__}."
    except KeyError as e:
        print(f"ERRO (TOOL - get_weather_tool): Dados da API OpenWeatherMap incompletos ou inesperados para '{city}': {e}. Resposta: {data}")
        return "Desculpe, recebi dados incompletos ou inesperados da API de clima. Tente novamente."
    except Exception as e:
        print(f"ERRO (TOOL - get_weather_tool): Erro inesperado ao processar clima para '{city}': {e}")
        return f"Desculpe, ocorreu um erro inesperado ao processar os dados do clima. Erro: {type(e).__name__}."


class MockGeneratedImagePart:
    def __init__(self, content_id_val):
        self.content_id = content_id_val

class MockImageResultWrapper:
    def __init__(self, prompt):
        self.generated_images = [MockGeneratedImagePart(f"mock_image_id_{abs(hash(prompt))}")]

class MockImageGenerationUsecase:
    ALTERNATIVES = "ALTERNATIVES"

class MockAspectRatio:
    ASPECT_RATIO_1_1 = "ASPECT_RATIO_1_1"
    ASPECT_RATIO_16_9 = "ASPECT_RATIO_16_9"
    ASPECT_RATIO_9_16 = "ASPECT_RATIO_9_16"
    ASPECT_RATIO_3_4 = "ASPECT_RATIO_3_4"
    ASPECT_RATIO_4_3 = "ASPECT_RATIO_4_3"

def mock_image_generation_func(prompts: list[str], image_generation_usecase, aspect_ratio=None):
    prompt = prompts[0] if prompts else "imagem vazia"
    print(f"SIMULANDO GERAÇÃO DE IMAGEM para: '{prompt}'")
    return type('obj', (object,), {'results': [MockImageResultWrapper(prompt)]})




def execute_Google_Search_api(query: str):
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX_ID:
        print("ERRO (TOOL - execute_Google Search_api): Chaves GOOGLE_CSE não configuradas. Não é possível realizar busca web.")
        return ["Desculpe, a ferramenta de busca web não está configurada corretamente. Por favor, avise o desenvolvedor."]

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_CSE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_CX_ID, num=3).execute()

        if 'items' in res:
            formatted_results = []
            for item in res['items']:
                snippet = item.get('snippet', 'Sem snippet disponível.')
                source_title = item.get('title', 'Sem título.')
                url = item.get('link', '#')
                formatted_results.append(f"Snippet: {snippet}\nFonte: {source_title} ({url})")
            return formatted_results
        
        return ["Não encontrei informações relevantes para sua busca na internet."]

    except Exception as e:
        print(f"ERRO REAL NA BUSCA GOOGLE API: {type(e).__name__}: {e}")
        return [f"Desculpe, houve um erro ao realizar a busca na internet. Erro: {type(e).__name__}."]


def search_web_tool(query: str):
    print(f"DEBUG (TOOL - search_web_tool): Realizando busca REAL por: '{query}'")
    search_results_list = execute_Google_Search_api(query)
    
    return "\n\n".join(search_results_list)

tools = [
    FunctionDeclaration(
        name="get_current_date_tool",
        description="**Obtém** a data atual no formato DD/MM/AAAA. Use EXCLUSIVAMENTE para perguntas que **solicitam** a data atual, como 'Que data é hoje?', 'Qual a data de hoje?'."
    ),
    FunctionDeclaration(
        name="get_current_time_tool",
        description="**Obtém** a hora atual no formato HH:MM:SS. Use EXCLUSIVAMENTE para perguntas que **solicitam** a hora atual, como 'Que horas são?', 'Me diga as horas'."
    ),
    FunctionDeclaration(
        name="get_current_datetime_tool",
        description="**Obtém** a data e hora atuais no formato DD/MM/AAAA HH:MM:SS. Use EXCLUSIVAMENTE para perguntas que **solicitam** a data e hora atuais, como 'Que dia e hora é hoje?', 'Data e hora atual'."
    ),
    FunctionDeclaration(
        name="get_current_day_of_week_tool",
        description="**Obtém** o dia da semana atual em português. Use EXCLUSIVAMENTE para perguntas que **solicitam** o dia da semana atual, como 'Que dia da semana é hoje?', 'Qual o dia da semana?'."
    ),
    FunctionDeclaration(
        name="search_web_tool",
        description="Realiza uma busca na internet para encontrar informações gerais, datas futuras de eventos, fatos, notícias, definições ou quaisquer dados que não estejam no conhecimento estático do modelo. Retorna snippets e URLs das fontes. Use para 'pesquisar [algo]', 'notícias sobre [tópico]', 'qual é o significado de [palavra]', 'informações sobre [assunto]' etc.",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A consulta de busca para procurar na web."}},
            "required": ["query"],
        },
    ),
    FunctionDeclaration(
        name="image_generation.generate_images",
        description="Gera uma imagem a partir de uma descrição textual. Use quando o usuário pedir explicitamente para 'criar uma imagem', 'gerar um visual', 'desenhar' algo. Retorna um ID de imagem simulado.",
        parameters={
            "type": "object",
            "properties": {
                "prompts": {"type": "array", "items": {"type": "string"}, "description": "Uma lista de descrições textuais para as imagens a serem geradas."},
                "aspect_ratio": {"type": "string", "enum": ["ASPECT_RATIO_1_1", "ASPECT_RATIO_16_9", "ASPECT_RATIO_9_16", "ASPECT_RATIO_3_4", "ASPECT_RATIO_4_3"], "description": "A proporção da imagem (opcional, padrão 1:1)."}
            },
            "required": ["prompts"],
        },
    ),
    FunctionDeclaration(
        name="get_weather_tool",
        description="Obtém as informações climáticas atuais (temperatura, descrição, umidade, vento) para uma cidade específica. Use quando o usuário perguntar sobre 'clima em [cidade]', 'temperatura de [cidade]', 'previsão em [cidade]', 'como está o tempo em [cidade]'.",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "O nome da cidade para a qual buscar o clima."}},
            "required": ["city"],
        },
    ),
]

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest', tools=tools)
else:
    print("ERRO CRÍTICO: Não foi possível configurar a API do Gemini. Verifique GEMINI_API_KEY no seu arquivo .env")
    model = None

# === PERSONALIDADE DO CHATBOT ===
# >>> AJUSTES PARA SER CONCISO E SEM ASTERISCOS (AINDA MAIS FORTE) <<<
PROMPT_PERSONALIDADE = """
Você é o RegAI, um assistente virtual **altamente inteligente, amigável, prestativo e com um toque de bom humor**.
**Seu propósito principal é ser um companheiro de conversa e um especialista multifacetado.**
Você é capaz de ter conversas gerais sobre qualquer tópico, responder perguntas de conhecimento comum, e utilizar suas ferramentas de forma inteligente e natural apenas quando a pergunta do usuário claramente exige uma busca por dados externos ou uma ação específica.

**Sua meta é sempre ser educado, CONCISO e divertido. Resuma informações complexas em parágrafos MUITO CURTOS e diretos, com no máximo 2-3 frases por parágrafo. Utilize quebras de linha generosamente para organizar o texto e torná-lo fácil de ler.**

Você pode assumir as seguintes personas e demonstrar expertise em:
- **Tutor/Professor:** Explica conceitos complexos de forma clara e paciente, guia o aprendizado, oferece exemplos.
- **Amigo:** Conversa de forma informal e empática, oferece suporte emocional leve, faz piadas, mostra interesse genuíno.
- **Pai/Mãe (Guia):** Oferece conselhos práticos, encorajamento, e um senso de cuidado (sem ser autoritário ou paternalista demais).
- **Psicólogo (Orientador):** Escuta ativamente, faz perguntas reflexivas para ajudar o usuário a explorar sentimentos e pensamentos, oferece perspectivas (NÃO dá diagnóstico ou tratamento).
- **Médico (Informativo):** Fornece informações gerais sobre saúde, nutrição e bem-estar de forma clara, mas sempre ENFATIZA a necessidade de consultar um profissional qualificado para diagnóstico, tratamento ou aconselhamento médico.
- **Educador Físico (Motivador):** Dá dicas de exercícios, rotinas, nutrição e bem-estar físico, motiva para a atividade e hábitos saudáveis.
- **Programador:** Ajuda com código, debug, explica conceitos de programação em diversas linguagens, sugere abordagens.
- **Pro Player (Gamer):** Dá dicas de jogos específicos, estratégias, comenta sobre e-sports, entende a gíria gamer e a cultura.
- **Matemático:** Resolve problemas, explica teoremas, ajuda com lógica matemática.

**Em resumo: Você é um ser multifacetado, com uma gama enorme de conhecimentos e personas que pode assumir para se adaptar à necessidade do usuário. Sua resposta deve ser sempre contextual, inteligente e apropriada à persona solicitada ou inferida. Sua principal força é a adaptabilidade e a profundidade da conversa.**

INSTRUÇÃO CRÍTICA: QUANDO VOCÊ PRECISAR FORNECER QUALQUER CÓDIGO (HTML, CSS, JAVASCRIPT, PYTHON, OU QUALQUER OUTRA LINGUAGEM), É ABSOLUTAMENTE ESSENCIAL E OBRIGATÓRIO QUE VOCÊ SEMPRE O ENVOLVA EM BLOCOS DE CÓDIGO MARKDOWN.

**DIREÇÃO CRÍTICA DE FORMATAÇÃO:**
- **EVITE o uso de ASTERISCOS (* ou **) para formar listas ou tópicos.**
- **Para listas, use NÚMEROS (1., 2., 3.) ou TRAÇOS (-) OU SINAIS DE MAIOR QUE (>) para bullet points.**
- **Use apenas DOIS ASTERISCOS (**) para **negrito** e UM ASTERISCO (*) para *itálico*.**
- **Utilize QUEBRAS DE LINHA (dois enters para um novo parágrafo) generosamente para garantir que o texto não fique aglomerado.** Cada ponto ou ideia principal deve estar em seu próprio parágrafo ou item de lista.
- **Se precisar indentar, use espaços ou a formatação de código.**
- **DIREÇÃO CRÍTICA DE FORMATAÇÃO E ESTRUTURA DA RESPOSTA:**
- **RESPOSTAS MUITO CONCISAS:** Mantenha cada parágrafo com no máximo 2-3 frases (preferencialmente 1-2).
- **QUEBRAS DE LINHA GENEROSAS:** Sempre use duas quebras de linha (`\n\n`) para separar parágrafos distintos. Isso cria espaços em branco e melhora a legibilidade.
- **FORMATAÇÃO DE LISTAS (MUITO IMPORTANTE):**
    - **Para listas numeradas, use `1. Item 1`, `2. Item 2`, etc.**
    - **Para listas com marcadores (bullet points), use TRAÇOS (`- Item`), ou SINAIS DE MAIOR QUE (`> Item`). NUNCA use asteriscos para listas.**
    - **Cada item de lista deve estar em uma NOVA LINHA separada.**
- **USO DE NEGRITO E ITÁLICO:**
    - Use apenas `**texto**` para **negrito**.
    - Use apenas `*texto*` para *itálico*.
    - **NUNCA use asteriscos múltiplos (***, ****, etc.) para outros fins além de negrito/itálico.**
- **IDENTAÇÃO EM CÓDIGO:** Mantenha o código em blocos Markdown com a identação correta da linguagem.
VOCÊ TEM ACESSO A FERRAMENTAS PARA OBTER A DATA, A HORA, O DIA DA SEMANA ATUAIS, REALIZAR BUSCAS NA WEB, GERAR IMAGENS E OBTER O CLIMA.
- **PRIORIZE O ENTENDIMENTO DA INTENÇÃO COMPLETA DO USUÁRIO.**
- **USE AS FERRAMENTAS APENAS SE A PERGUNTA DO USUÁRIO ESTIVER CLARAMENTE SOLICITANDO A OBTENÇÃO DE UMA NOVA INFORMAÇÃO EXTERNA OU UMA AÇÃO ESPECÍFICA.**
- **NÃO USE uma ferramenta se a pergunta for para CONFIRMAR, VALIDAR ou COMENTAR sobre uma informação que a ferramenta *retornaria*. Nesses casos, responda de forma conversacional e com seu conhecimento interno.**
    - SE O USUÁRIO PEDIR PARA *OBTER* A DATA, HORA, DIA DA SEMANA (ex: 'Que data é hoje?', 'Qual a hora agora?'): Use a ferramenta correspondente e responda diretamente.
    - SE O USUÁRIO PEDIR PARA *CONFIRMAR* A DATA, HORA, DIA DA SEMANA (ex: 'A data de hoje está certa?', 'São 10 da manhã agora?', 'Hoje é segunda-feira?'): NÃO use a ferramenta. Apenas confirme ou corrija usando seu conhecimento atual e o contexto.
    - SE O USUÁRIO PEDIR SOBRE INFORMAÇÕES QUE PODEM ESTAR NA INTERNET (notícias recentes, fatos específicos complexos que exigem dados atualizados): USE A FERRAMENTA search_web_tool COM UMA QUERY CLARA E CONCISA.
    - SE O USUÁRIO PEDIR PARA CRIAR OU GERAR UMA IMAGEM: USE A FERRAMENTA image_generation.generate_images COM UM PROMPT DESCRITIVO.
    - SE O USUÁRIO PEDIR SOBRE O CLIMA (ex: "clima em [cidade]", "temperatura de [cidade]"): USE A FERRAMENTA get_weather_tool COM O NOME DA CIDADE.

- **PARA PERGUNTAS DE CONVERSA GERAL, CURIOSIDADES, OPINIÕES (neutras), OU SOBRE VOCÊ (RegAI), RESPONDA DE FORMA NATURAL, CONTEXTUAL E AMIGÁVEL, SEM NECESSIDADE DE FERRAMENTAS.** Ex: "Como você está?", "Você gosta de [algo]?", "O que você acha disso?". Nesses casos, apenas converse de forma fluida.
- **MANTENHA O CONTEXTO DA CONVERSA.** Lembre-se do que foi dito anteriormente.
- SE UMA FERRAMENTA RETORNAR "Não foi possível encontrar dados", "Não encontrei informações" ou um erro: ADMITA SINCERAMENTE QUE NÃO ENCONTROU A INFORMAÇÃO COMPLETA OU QUE HOUVE UM ERRO. Não invente! Peça para o usuário tentar reformular ou pergunte se pode ajudar com outra coisa, com a persona apropriada.
- Sempre seja bem humorado e adicione um toque de personalidade em suas respostas, mas seja conciso quando necessário.
- Para assuntos de saúde ou finanças, sempre reforce a necessidade de buscar um profissional qualificado.
- Se o usuário pedir para você ser uma persona específica, tente se adaptar a essa persona em suas respostas seguintes.
"""

# === VARIÁVEIS DE CONTROLE ===
chat_history = []
waiting_for_annotation = False
codigo = "anotacoes_chatbot.json"
gemini_chat_session = None

# === LOCALIZAÇÃO DA DATA EM PORTUGUÊS ===
for loc in ['pt_BR.utf8', 'Portuguese_Brazil.1252', 'pt_BR', 'pt_BR.UTF-8']:
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except locale.Error:
        pass

# === FUNÇÕES AUXILIARES PARA ANOTAÇÕES ===
def carregar_anotacoes():
    try:
        with open(codigo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_anotacoes(anotacoes_list):
    with open(codigo, 'w', encoding='utf-8') as f:
        json.dump(anotacoes_list, f, indent=4, ensure_ascii=False)

def search_web(query):
    print(f"DEBUG: Chamada à função 'search_web' (antiga/fallback) com query: {query}")
    if "clima em" in query.lower():
        cidade = query.lower().replace("clima em", "").strip()
        return f"Simulando (fallback): O clima em {cidade} está ensolarado e agradável hoje."
    elif "capital de" in query.lower():
        pais = query.lower().replace("capital de", "").strip()
        if "brasil" in pais:
            return "Simulando: A capital do Brasil é Brasília."
        else:
            return f"Simulando: Não tenho informações imediatas sobre a capital de {pais}."
    else:
        return f"Simulando: Sua pesquisa por '{query}' retornou alguns resultados relevantes. No momento, não consigo acessar a web para detalhes."

# === ROTA INICIAL PARA INDEX.HTML ===
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

# === CARREGAMENTO INICIAL DAS ANOTAÇÕES ===
lista_de_anotacoes = carregar_anotacoes()

# === ROTA DE CONVERSA COM O CHATBOT ===
@app.route('/chat', methods=['POST'])
def chat():
    global chat_history, waiting_for_annotation, lista_de_anotacoes, gemini_chat_session

    user_message = request.get_json().get('message', '')
    user_message_lower = user_message.lower()

    if model is None:
        return jsonify({"response": "Desculpe, o serviço de IA não está disponível no momento. Por favor, verifique a configuração da chave Gemini no servidor."})

    if gemini_chat_session is None:
        initial_history_for_gemini = [
            {"role": "user", "parts": [PROMPT_PERSONALIDADE]},
            {"role": "model", "parts": ["Olá! Sou o RegAI, seu assistente completo e multifacetado, pronto para te ajudar com o que precisar. Como posso ser útil hoje? 😊"]}
        ]
        gemini_chat_session = model.start_chat(
            history=initial_history_for_gemini,
            enable_automatic_function_calling=True,
        )
        print("DEBUG: Nova sessão de chat Gemini iniciada com PROMPT_PERSONALIDADE no histórico.")
        chat_history.append({"role": "model", "parts": ["Olá! Sou o RegAI, seu assistente completo e multifacetado, pronto para te ajudar com o que precisar. Como posso ser útil hoje? 😊"]})


    chat_history.append({"role": "user", "parts": [user_message]})
    
    _bot_response = ""

    if waiting_for_annotation:
        lista_de_anotacoes.append(user_message)
        salvar_anotacoes(lista_de_anotacoes)
        _bot_response = f"A anotação '{user_message}' foi salva com sucesso! Que legal! Posso te ajudar com mais alguma coisa? 😊"
        waiting_for_annotation = False
    elif user_message.lower() == "sair":
        chat_history.clear()
        gemini_chat_session = None
        _bot_response = "Até mais! 😉 O histórico de conversa foi limpo. Se precisar de algo, é só chamar de novo!"
    elif user_message_lower in ["ajuda", "comandos", "o que você faz", "o que consigo fazer"]:
        _bot_response = (
            "Olá! Sou o RegAI e estou aqui para tornar seu dia mais fácil e divertido! Posso:\n"
            "- Te contar a 'data', a 'hora' ou o 'dia da semana' atual. ⏰\n"
            "- Me pedir para 'pesquisar [qualquer coisa]' ou 'notícias de [tópico]'. 🌐\n"
            "- Querer saber o 'clima em [cidade]' ou a 'temperatura em [cidade]'. ☀️🌧️\n"
            "- Pedir para 'gerar imagem de [sua descrição]'. 🎨\n"
            "- E sou ótimo para gerenciar suas anotações! Basta dizer 'adicionar anotação' ou 'ver anotações'. 📝\n"
            "- Se quiser recomeçar, digite 'sair'.\n\n"
            "Qualquer outra coisa, pode perguntar! Sou bem divertido também, hehe! 😄"
        )
    elif user_message_lower == "adicionar anotação":
        waiting_for_annotation = True
        _bot_response = "Certo! Qual anotação você gostaria de adicionar? Manda a brasa! ✍️"
    elif user_message_lower == "ver anotações":
        if lista_de_anotacoes:
            anotacoes_str = "\n".join(f"- {a}" for a in lista_de_anotacoes)
            _bot_response = f"As anotações que encontrei para você são:\n{anotacoes_str}\n\nPosso ajudar com algo mais nessas anotações ou em outro assunto? 🤔"
        else:
            _bot_response = "Hmm... Não encontrei nenhuma anotação salva ainda. Que tal adicionar a primeira agora? É super fácil! 😉"
    
    if _bot_response:
        chat_history.append({"role": "model", "parts": [_bot_response]})
        return jsonify({"response": _bot_response})

    try:
        print(f"DEBUG (Mensagem enviada para Gemini): {user_message}")
        print(f"DEBUG (Histórico da sessão Gemini antes de send_message): {gemini_chat_session.history}")
        
        response = gemini_chat_session.send_message(user_message)
        
        final_bot_response = ""
        text_parts = []
        function_calls_to_execute = []

        for part in response.parts:
            if part.text:
                text_parts.append(part.text)
            elif part.function_call:
                function_calls_to_execute.append(part.function_call)
        
        if text_parts:
            final_bot_response = "".join(text_parts)
            print(f"DEBUG: Texto do modelo no Primeiro Turno: {final_bot_response}")

        if function_calls_to_execute:
            print(f"DEBUG: Modelo solicitou {len(function_calls_to_execute)} chamada(s) de função no Primeiro Turno.")
            
            for called_function in function_calls_to_execute:
                function_name = called_function.name
                function_args = called_function.args
                tool_result_value = f"Erro desconhecido ao executar ferramenta: {function_name}"
                
                print(f"DEBUG: Executando ferramenta: {function_name} com args: {function_args}")

                try:
                    if function_name == "search_web_tool":
                        tool_result_value = search_web_tool(function_args.get("query"))
                    elif function_name == "get_weather_tool":
                        tool_result_value = get_weather_tool(function_args.get("city"))
                    elif function_name == "image_generation.generate_images":
                        prompts = function_args.get("prompts", [])
                        aspect_ratio_str = function_args.get("aspect_ratio")
                        
                        if prompts:
                            image_gen_result = mock_image_generation_func(
                                prompts=prompts,
                                image_generation_usecase=MockImageGenerationUsecase.ALTERNATIVES,
                                aspect_ratio=MockAspectRatio.__dict__.get(aspect_ratio_str, None)
                            )
                            if image_gen_result and image_gen_result.results and image_gen_result.results[0].generated_images:
                                content_id = image_gen_result.results[0].content_id
                                tool_result_value = f"Aqui está a imagem que criei para você (ID simulado):\n{content_id}"
                            else:
                                tool_result_value = "Não consegui gerar a imagem (simulado). Por favor, tente descrevê-la de outra forma."
                        else:
                            tool_result_value = "Geração de imagem falhou (simulado): prompt não fornecido."
                    
                    elif function_name == "get_current_date_tool":
                        tool_result_value = get_current_date_tool()
                    elif function_name == "get_current_time_tool":
                        tool_result_value = get_current_time_tool()
                    elif function_name == "get_current_datetime_tool":
                        tool_result_value = get_current_datetime_tool()
                    elif function_name == "get_current_day_of_week_tool":
                        tool_result_value = get_current_day_of_week_tool()
                    
                    else:
                        tool_result_value = f"Ferramenta desconhecida '{function_name}' solicitada pela IA. Verifique a declaração de ferramentas."
                        print(f"AVISO: Ferramenta desconhecida '{function_name}' solicitada pela IA.")

                    print(f"DEBUG: Enviando resultado da ferramenta '{function_name}' de volta para IA (Segundo Turno da IA).")
                    response_after_tool = gemini_chat_session.send_message(
                        {"role": "tool", "parts": [
                            {"function_response": {
                                "name": function_name,
                                "response": {"result": tool_result_value}
                            }}
                        ]}
                    )
                    final_bot_response = response_after_tool.text
                    print(f"DEBUG: Resposta final da IA após ferramenta: {final_bot_response}")

                except Exception as tool_e:
                    print(f"ERRO NA EXECUÇÃO DA FERRAMENTA '{function_name}': {type(tool_e).__name__}: {tool_e}")
                    final_bot_response = f"Ops! Desculpe, houve um probleminha ao tentar usar a ferramenta {function_name}. Erro: {tool_e}. Tente de novo mais tarde, tá bom? 😅"
        
        if not final_bot_response.strip():
            final_bot_response = "Hmmm... Que pergunta interessante! Deixe-me pensar um pouco mais. Ou, se preferir, pode me perguntar outra coisa. Estou aqui para ajudar em qualquer coisa que precisar! 😊"

        bot_response = final_bot_response

    except Exception as e:
        print(f"ERRO FATAL AO CONECTAR COM A IA: {type(e).__name__}: {e}")
        bot_response = "Oh não! 😟 Houve um problema ao me comunicar com a IA. Parece que o fio desencapou! Por favor, tente novamente mais tarde. Se o problema persistir, avise o desenvolvedor para ele dar uma olhadinha no terminal. 😉"
        gemini_chat_session = None

    chat_history.append({"role": "model", "parts": [bot_response]})
    return jsonify({"response": bot_response})

# === EXECUÇÃO DO SERVIDOR ===
if __name__ == '__main__':
    print("Iniciando o servidor Flask para o Chatbot...")
    app.run(debug=True, port=8000)