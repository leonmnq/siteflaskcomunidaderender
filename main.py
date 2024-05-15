from comunidadeimpressionadora import app  # importa o app do arquivo __init__.py

if __name__ == '__main__':     # essa linha garante que o que está dentro o if só vai rodar se eu estiver executando o arquivo main.py especificamente
    app.run(debug=True)
