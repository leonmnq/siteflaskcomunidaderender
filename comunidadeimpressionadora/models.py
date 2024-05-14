from comunidadeimpressionadora import database  # importando o banco de dados do arquivo __init__.py
from datetime import datetime
from comunidadeimpressionadora import login_manager  # importando o gerenciador de login do nosso site (login passo 4)
from flask_login import UserMixin  # UserMixin é um parâmetro que vamos passar para nossa classe que já vai atribuir a essa classe todas as características que o login_manager precisa para conseguir controlar o login, manter conectado (login passo 6)


# o login_manager precisa de uma função que encontre o usuário pelo id dele
# Criando função para fazer o login do usuário: (login passo 5)
@login_manager.user_loader  # esse decorator diz que essa função é a que carrega o usuário
def load_usuario(id_usario):
    # retorna id do usuário, garantia: caso não seja inteiro, transforam em inteiro
    return Usuario.query.get(int(id_usario))  # o método get encontra um item na tabela conforme a primary key da tabela, que no caso, é exatamente o que procuramos


class Usuario(database.Model, UserMixin):  # a subclasse Usuario recebe como herança de uma outra classe padrão de banco de dados do sql alchemy que é a database.Model
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)  # nullable=False, nunca pode ser nulo
    email = database.Column(database.String, nullable=False, unique=True)  # unique=True, tem que ser o único no site
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')  # qualquer usuário terá por padrão uma foto default
    cursos = database.Column(database.String, nullable=False, default='Não Informado')

    # como um usuário pode ter vários posts, relação de 1 para muitos, então:
    # criamos a variável posts, como uma lista de posts, que não é uma lista, é o relacionamento onde a tabela Usuario pode receber várias informações da tabela Post
    posts = database.relationship('Post', backref='autor', lazy=True)  # post.autor vai retornar o autor daquele post, lazy=True puxa todas as informações daquele usuário

    # Método responsável por contar os posts dos usuários
    def contar_posts(self):  # método da classe Usuario
        return len(self.posts)


class Post(database.Model):  # a subclasse Post também é uma extensão do database.Model
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    # data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())  #datetime.utcnow() é obsoleto. O correto agora é datetime.now(timezone.utc)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)  # ForeignKey é a chave que cria a relação entre o post e o usuário
