from flask import Flask, render_template, request, Response
import os
from openai import OpenAI
import dotenv
from time import sleep
import tiktoken

app = Flask(__name__)
app.secret_key = "alura"

dotenv.load_dotenv()

client = OpenAI()


def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            return arquivo.read()
    except IOError as e:
        print(f"Erro no carregamento do arquivo {nome_do_arquivo}: {e}")


def salva(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro no salvamento do arquivo {nome_do_arquivo}: {e}")


def conta_tokens(prompt):
    codificador = tiktoken.encoding_for_model("gpt-3.5-turbo")
    lista_de_tokens = codificador.encode(prompt)
    contagem = len(lista_de_tokens)
    return contagem


def limita_historico(historico, limite_maximo_de_tokens):
    total_de_tokens = 0
    historico_parcial = ""
    for linha in reversed(historico.split("\n")):
        tokens_da_linha = conta_tokens(linha)
        total_de_tokens += tokens_da_linha
        if total_de_tokens > limite_maximo_de_tokens:
            break
        historico_parcial = linha + historico_parcial
    return historico_parcial


dados_ecommerce = carrega("dados_ecommerce.txt")


def bot(prompt, historico):
    maxima_repeticao = 1
    repeticao = 0
    while True:
        try:
            model = "gpt-3.5-turbo"
            prompt_do_sistema = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            ## Dados do ecommerce:
            {dados_ecommerce}
            ## Histórico:
            {historico}
            """

            # tamanho_esperado_saida = 2000
            # total_tokens_modelo = 4000
            # if (
            #     conta_tokens(prompt_do_sistema)
            #     >= total_tokens_modelo - tamanho_esperado_saida
            # ):
            #     model = "gpt-3.5-turbo-16k"

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": prompt_do_sistema}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    },
                ],
                stream=True,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response
        except Exception as erro:
            repeticao += 1
            if repeticao >= maxima_repeticao:
                return "Erro no GPT3: %s" % erro
            print("Erro de comunicação com OpenAI:", erro)
            sleep(1)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    nome_do_arquivo = f"historico_ecomat.txt"
    historico = ""
    if os.path.exists(nome_do_arquivo):
        historico = carrega(nome_do_arquivo)
    return Response(
        trata_resposta(prompt, historico, nome_do_arquivo), mimetype="text/event-stream"
    )


def trata_resposta(prompt, historico, nome_do_arquivo):
    resposta_parcial = ""
    limite_maximo_de_tokens = 250
    historico_parcial = limita_historico(historico, limite_maximo_de_tokens)
    for resposta in bot(prompt, historico_parcial):
        if resposta.choices[0].delta.content is not None:
            pedaco_da_resposta = resposta.choices[0].delta.content
            if len(pedaco_da_resposta):
                resposta_parcial += pedaco_da_resposta
                yield pedaco_da_resposta
    conteudo = f"""
    Histórico: {historico_parcial}
    Usuário: {prompt}
    IA: {resposta_parcial}
    """
    salva(nome_do_arquivo, conteudo)


if __name__ == "__main__":
    app.run(debug=True)
