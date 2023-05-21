from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from orion.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email): #o método tem que começar obrigatoriamente com 'validate_' pois é o que permite a função validate_on_submit() da classe FlaskForm de chamar a função criada
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])    
    a_renda_fixa_nacional = BooleanField('Renda Fixa Nacional')
    a_renda_fixa_internacional = BooleanField('Renda Fixa Internacional')
    a_renda_variavel_nacional = BooleanField('Renda Variável Nacional')
    a_renda_variavel_internacional = BooleanField('Renda Variável Internacional')
    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email): #o método tem que começar obrigatoriamente com 'validate_' pois é o que permite a função validate_on_submit() da classe FlaskForm de chamar a função criada
        #verificar se o e-mail foi alterado
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado')

class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Digite o conteúdo...', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')