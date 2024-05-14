from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # permite a criação do nosso banco de dados
from flask_bcrypt import Bcrypt  # permite criptografar senhas
from flask_login import LoginManager  # para ser possível fazer o login (login passo 2, passo 1 é instalar o flask-login)

import os  # nesse caso vai nos permitir trabalhar com variáveis de ambiente (lá no Railway)


app = Flask(__name__)  # essa linha permite que o flask entenda que nosso código é um site e possibilita a interligação de várias pastas, arquivos, páginas html...



if os.getenv("DATABASE_URL"): # se existe essa variável de ambiente, DATABASE_URL...
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # então nosso app.config será essa variável de ambiente
else:  # caso contrário...
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'  # configuração do banco de dados local

app.config['SECRET_KEY'] = '0c841c3215b516595caba780abfd8d72'  # token para segurança do site

app.config["UPLOAD_FOLDER"] = "static/fotos_perfil"  # define onde as fotos serão armazenadas

database = SQLAlchemy(app)

# criando uma instância do bcrypt
bcrypt = Bcrypt(app)  # a partir desse código, só o nosso site consegue criptografar e descriptografar essa senha a partir da instância bcrypt

# login passo 3
login_manager = LoginManager(app)  # criando o gerenciador de login do nosso site

# sempre que o usuário deslogado tentar acessar uma página que tenha o decorator 'login_required'
login_manager.login_view = 'login'  # sempre que o usuário não logado tentar acessar uma página que exige login para ser exibida, ele será enviado para página de login

# configurando o alerta para exigir login
login_manager.login_message = 'Faça login para acessar essa página.'  # comente essa linha de código para exibir a mensagem padrão em inglês
login_manager.login_message_category = 'alert-info'  # alert-info = azul claro # consultar para ver as possíveis cores: https://getbootstrap.com/docs/5.2/components/alerts/

# essa importação tem que ser no final porque o arquivo routes_or_views precisa do app criado acima, para funcionar
from comunidadeimpressionadora import routes_or_views  # para colocar os links no ar assim que o __init__ rodar
