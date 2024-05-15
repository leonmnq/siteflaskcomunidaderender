from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import TextAreaField  # para um texto longo (post)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadeimpressionadora.models import Usuario
from flask_login import current_user  # para verificar o usuário atual
from flask_wtf.file import FileField  # campo em que o usuário clica e abre o popup do computador para escolher o arquivo para fazer upload
from flask_wtf.file import FileAllowed  # é um validator, é nele que escolhemos as extensões de arquivo que o usuário pode fazer upload


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    # Criando uma função para verificar se o email já existe no banco de dados:
    # o FlaskForm roda qualquer função que inicie com 'validate_' da mesma maneira que roda os 'validators'
    def validate_email(self, email):  # a função precisa iniciar com 'validate_' para que o 'validate_on_submit()' possa analizá-la no routes_or_views.py
        usuario = Usuario.query.filter_by(email=email.data).first()  # 'usuario' vai receber a busca pelo usuario que tem o mesmo email do email inserido no filtro e retornar o primeiro resultado
        if usuario:  # se existe usuario, se não é vazio
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.')   # raise é como se fosse chamar um erro


class FormFazerLogin(FlaskForm):
    email_login = StringField('E-mail', validators=[DataRequired(), Email()])
    senha_login = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_fazerlogin = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil: ', validators=[FileAllowed(['jpg', 'png', 'gif'])])

    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Power BI Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_ppt = BooleanField('Apresentações Impressionadoras')
    curso_sql = BooleanField('SQL Impressionador')

    botao_submit_confirmaredicao = SubmitField('Confirmar Edição')

    # Criando uma função para verificar se o email já existe no banco de dados:
    # o FlaskForm roda qualquer função que inicie com 'validate_' da mesma maneira que roda os 'validators'
    def validate_email(self, email):  # a função precisa iniciar com 'validate_' para que o 'validate_on_submit()' possa analizá-la no routes_or_views.py
        if current_user.email != email.data:  # se o email do usuário que está logado é diferente do email que está no campo de edição de email
            usuario = Usuario.query.filter_by(email=email.data).first()  # 'usuario' vai receber a busca pelo usuario que tem o mesmo email do email inserido no filtro e retornar o primeiro resultado
            if usuario:  # se existe usuario, se não é vazio
                raise ValidationError('E-mail já cadastrado. Cadastre outro e-mail.')   # raise é como se fosse chamar um erro


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired()])
    botao_submit_enviarpost = SubmitField('Enviar Post')


# optei por criar o formulário em vez de usar o FormCriarPost, era facultativo
class FormEditarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired()])
    botao_submit_confirmaredicao = SubmitField('Confirmar Edição')

