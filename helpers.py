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
