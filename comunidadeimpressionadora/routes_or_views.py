from flask import render_template  # renderiza as páginas html
from flask import redirect  # redireciona o usuário
from flask import url_for  # para fazer o redirecionamento baseado no nome da função, evitando que o link quebre caso a rota seja alterada
from flask import flash  # para exibir mensagens de alerta
from flask import request  # é utilizado para verificar requisições de GET e POST
from comunidadeimpressionadora import app  # importa o aplicativo do arquivo __init__.py
from comunidadeimpressionadora import database
from comunidadeimpressionadora import bcrypt
from comunidadeimpressionadora.forms import FormFazerLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, FormEditarPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user  # para poder fazer o login do usuário (login passo 7)
from flask_login import logout_user  # para fazer logout
from flask_login import current_user  # verifica quem é o usuário atual # será usado no arquivo navbar.html
from flask_login import login_required  # decorator que define que aquela página só será exibida se o usuário estiver logado
import secrets  # biblioteca para gerar chaves aleatórias
import os  # vamos usar para separar o nome da imagem da extensão
from PIL import Image  # para compactar imagem
from flask import abort  # no caso, trava a tentativa de excluir post se não for dono do post


@app.route('/')
def homepage():
    # todos_posts = Post.query.all()  # pega todos os posts do banco e armazena na variável
    todos_posts = Post.query.order_by(Post.id.desc())  # para pegar todos os posts e ordená-los para mostrar o mais recente primeiro
    return render_template('homepage.html', todos_posts=todos_posts)  # renderiza a página homepage.html e passa pra página, todos_posts como parâmetro


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required  # o usuário tem que estar logado para conseguir acessar
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_fazerlogin = FormFazerLogin()
    form_criarconta = FormCriarConta()

    # login passo 8
    if form_fazerlogin.validate_on_submit() and 'botao_submit_fazerlogin' in request.form:  # se todos os campos de fazer login foram preenchidos e o botão fazer login foi apertado, ('botao_submit_fazerlogin' in request.form) verifica se o texto do botão (nome dele) está contido no formulário (form_fazerlogin) em que a requisição foi feita
        usuario = Usuario.query.filter_by(email=form_fazerlogin.email_login.data).first()  # retorna o primeiro resultado da tabela Usuario que tenha um email igual ao que o usuário acabou de digitar
        if usuario:  # se esse usuário existe
            if bcrypt.check_password_hash(usuario.senha.encode('utf-8'), form_fazerlogin.senha_login.data):  # se a senha que está no banco de dados é igual a senha que o usuário acabou de digitar
                # faz o login
                login_user(usuario, remember=form_fazerlogin.lembrar_dados.data)  # remember=True permite lembrar os dados de conexão # 'form_fazerlogin.lembrar_dados.data' vai retornar True ou False dependendo se o usuário marcou ou não a caixinha de lembrar dados
                # exibe mensagem de sucesso
                flash(f'Login feito com sucesso no e-mail: {form_fazerlogin.email_login.data}', 'alert-success')  # para escolher a cor do botão: https://getbootstrap.com/docs/5.2/components/buttons/

                # verifica a página que o usuário está tentando acessar
                parametro_next = request.args.get('next')  # 'request.args.get' pega todos os argumentos que estão no link que o usuário quer acessar, no link que está sendo requisitado, o parâmetro 'next'
                if parametro_next: # se existe valor nessa variável
                    return redirect(parametro_next)  # redireciona o usuário para a página específica
                else:  # caso contrário
                    return redirect(url_for('homepage'))  # redireciona para a homepage

            else:
                # senha falhou, exibe mensagem de falha
                flash('Falha no Login. E-mail ou Senha Incorretos.', 'alert-danger')  # para escolher a cor do botão: https://getbootstrap.com/docs/5.2/components/buttons/
        else:
            # email falhou, exibe mensagem de falha
            flash('Falha no Login. E-mail ou Senha Incorretos.', 'alert-danger')  # para escolher a cor do botão: https://getbootstrap.com/docs/5.2/components/buttons/

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:  # se todos os campos de criar conta foram preenchidos e o botão criar conta foi apertado, ('botao_submit_criarconta' in request.form) verifica se o texto do botão (nome dele) está contido no formulário (form_criarconta) em que a requisição foi feita
        # criptografando senha:
        senha_criptografada = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')  # criptografa a senha e decodifica (evita problema no banco de dados postgresql)

        # criar o Usuario:
        usuario = Usuario(
            username=form_criarconta.username.data,
            email=form_criarconta.email.data,
            senha=senha_criptografada
        )  # variável usuario vai ser uma instância da minha classe Usuario

        # adicionar a sessão
        database.session.add(usuario)
        # commit na sessão
        database.session.commit()

        flash(f'Conta criada com sucesso para o e-mail: {form_criarconta.email.data}', 'alert-success')

        # ACRESCENTEI ESSA LINHA
        # FAZ o login do usuário logo após o cadastro
        login_user(usuario)

        return redirect(url_for('homepage'))
    return render_template('login.html', form_fazerlogin=form_fazerlogin, form_criarconta=form_criarconta)


# fazer logout
@app.route('/sair')
@login_required  # o usuário tem que estar logado para conseguir acessar
def sair():
    logout_user()
    flash('Logout Feito com Sucesso.', 'alert-success')
    return redirect(url_for('homepage'))


# entrar no perfil
@app.route('/perfil')
@login_required  # o usuário tem que estar logado para conseguir acessar
def perfil():
    # definindo a lógica de atualização da foto do perfil do usuário:
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


# criar post
@app.route('/post/criar', methods=['GET', 'POST']) # obrigatório o método POST sempre que quiser enviar dados para o banco
@login_required  # o usuário tem que estar logado para conseguir acessar
def criar_post():
    form_criarpost = FormCriarPost()
    if form_criarpost.validate_on_submit():  # se os campos foram preenchidos corretamente e o usuário clicou em enviar post
        post = Post(
            titulo=form_criarpost.titulo.data,
            corpo=form_criarpost.corpo.data,
            autor=current_user
        )  # post recebe uma instância da classe Post
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso.', 'alert-success')
        return redirect(url_for('homepage'))
    return render_template('criarpost.html', form_criarpost=form_criarpost) # form_criarpost=form_criarpost parâmetro foi enviado para página criarpost.html


# função para tratar e salvar a imagem
def salvar_imagem(imagem):
    # adicionar um código aleatório no nome da imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)  # vai separar o nome e a extensão, e armazenar nas suas respectivas variáveis
    nome_arquivo = nome + codigo + extensao

    # reduzir o tamanho da imagem
    tamanho = (200, 200)  # 200 pixels
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    # configurar o caminho
    caminho_completo = os.path.join(
        app.root_path,
        'static/fotos_perfil',
        nome_arquivo
    )  # app.root_path = caminho raiz do nosso aplicativo

    # salvar a imagem na pasta fotos_perfil
    imagem_reduzida.save(caminho_completo)

    return nome_arquivo


def atualizar_cursos(form_editarperfil):
    lista_cursos = []  # lista auxiliar vazia
    for campo in form_editarperfil:
        if 'curso_' in campo.name:  # se 'curso_' está contido no nome do campo
            if campo.data:  # se o check box do campo foi selecionado # campo.data retorna True se tiver marcado e False se não tiver marcado
                # adicionar o texto do campo.label (Excel Impressionador) na lista de cursos
                lista_cursos.append(campo.label.text)  # adiciona na lista o texto do campo.label
    return ';'.join(lista_cursos)  # join vai percorrer toda lista_cursos e juntar cada item com ';', criando uma única string


@app.route('/perfil/editar', methods=['GET', 'POST'])  # methods=['GET', 'POST'] para permitir postar/enviar informações para o banco
@login_required
def editar_perfil():
    form_editarperfil = FormEditarPerfil()
    if form_editarperfil.validate_on_submit():  # se todos os campos foram preenchidos e o botão de confirmar edição foi apertado
        # if current_user.email != form_editarperfil.email.data:  # já existe essa verificação no forms.py
        current_user.email = form_editarperfil.email.data  # email do usuário logado muda para o email que o usuário digitou no campo de edição
        current_user.username = form_editarperfil.username.data  # username do usuário logado muda para o username que o usuário digitou no campo de edição

        # imagem
        if form_editarperfil.foto_perfil.data:
            # chamando a função
            nome_imagem = salvar_imagem(form_editarperfil.foto_perfil.data)
            # mudar o campo foto_perfil do usuário para o novo nome da imagem
            current_user.foto_perfil = nome_imagem

        # cursos
        current_user.cursos = atualizar_cursos(form_editarperfil)

        """ TRECHO DE CÓDIGO ESCRITO POR MIM """
        # condição que escreve o padrão 'Não Informado' na coluna cursos caso o usuário desmarque todos os seus cursos
        usuario_atual = Usuario.query.filter_by(email=current_user.email).first()  # retornar o usuário dono do email que está logado no momento
        if usuario_atual.cursos == '':
            usuario_atual.cursos = 'Não Informado'

        database.session.commit()  # registra as alterações no banco de dados
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))  # redirecionado para página de perfil

    # verificar se a requisição é do tipo GET, ou seja, apenas leitura
    elif request.method == 'GET':  # se a página de edição tiver sido só carregada, então:
        form_editarperfil.username.data = current_user.username
        form_editarperfil.email.data = current_user.email

        """ TRECHO DE CÓDIGO ESCRITO POR MIM """
        # minha lógica - PRECISO REFAZER!!!
        usuario_atual = Usuario.query.filter_by(email=current_user.email).first()  # retornar o usuário dono do email que está logado no momento
        cursos_banco = usuario_atual.cursos  # cursos_banco recebe a string de cursos do usuário
        cursos_selecionados = cursos_banco.split(';')  # separa a string cursos_banco e armazena na variável cursos_selecionados
        for curso in cursos_selecionados:
            if 'Excel' in curso:
                form_editarperfil.curso_excel.data = True
            if 'VBA' in curso:
                form_editarperfil.curso_vba.data = True
            if 'Power' in curso:
                form_editarperfil.curso_powerbi.data = True
            if 'Python' in curso:
                form_editarperfil.curso_python.data = True
            if 'Apres' in curso:
                form_editarperfil.curso_ppt.data = True
            if 'SQL' in curso:
                form_editarperfil.curso_sql.data = True

    # definindo a lógica de atualização da foto do perfil do usuário:
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form_editarperfil=form_editarperfil)


@app.route('/post/<post_id>', methods=['GET', 'POST'])  # <post_id> é uma variável passada dentro da rota
@login_required
def exibir_post(post_id):  # nossa função terá que receber obrigatóriamente essa variável como parâmetro
    # assim podemos exibir o post pelo id, ex: exiba o post que tem id=2, exiba o post que tem id=3...

    # o post que será exibido será o mesmo post do id que aparece lá na rota, na url
    post = Post.query.get(post_id)  # usamos o get porque queremos o id do post, chave primária

    if current_user == post.autor:  # se o usuário atual é o autor do post
        form_editarpost = FormEditarPost()

        # preenchendo os campos de edição com o título e corpo atual do post ao carregar a página
        if request.method == 'GET':  # se a página de edição tiver sido só carregada, então:
            form_editarpost.titulo.data = post.titulo  # campo título recebe o conteúdo do título no db
            form_editarpost.corpo.data = post.corpo

        elif form_editarpost.validate_on_submit():  # se os campos de edição estão preenchidos e o usuário clicou em confirmar edição
            post.titulo = form_editarpost.titulo.data  # a edição do campo de título é armazenada na variável, aguardando commit
            post.corpo = form_editarpost.corpo.data

            database.session.commit()
            flash('Post Atualizado com Sucesso.', 'alert-success')
            return redirect(url_for('homepage'))  # e o usuário é redirecionado para homepage

        # lógica de editar post
    else:
        form_editarpost = None
    return render_template('post.html', post=post, form_editarpost=form_editarpost)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)  # a variável post recebe o id daquele post
    if current_user == post.autor: # se o usuário atual é dono do post
        database.session.delete(post)
        database.session.commit()
        flash('Seu post foi excluído.', 'alert-warning')
        return redirect(url_for('homepage'))
    else:
        abort(403)  # erro de proibido, não tem permissão para requisitar a ação
