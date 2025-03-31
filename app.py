from flask import Flask
from openai import OpenAI
import dotenv
from time import sleep
from helpers import *

app = Flask(__name__)
app.secret_key = "alura"

dotenv.load_dotenv()

client = OpenAI()

from views import *


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


if __name__ == "__main__":
    app.run(debug=True)
