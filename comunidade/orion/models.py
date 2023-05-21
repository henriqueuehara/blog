from orion import database, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
  return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
  id = database.Column(database.Integer, primary_key=True)
  username = database.Column(database.String, nullable=False)
  email = database.Column(database.String, nullable=False, unique=True)
  senha = database.Column(database.String, nullable=False)
  foto_perfil = database.Column(database.String, default='default.jpg')
  posts = database.relationship('Post', backref='autor', lazy=True)
  classes_ativos = database.Column(database.String, nullable=False, default="Não Informado")

  def contar_posts(self):
    return len(self.posts)


class Post(database.Model):
  id = database.Column(database.Integer, primary_key=True)
  titulo = database.Column(database.String, nullable=False)
  corpo = database.Column(database.Text, nullable=False)
  data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow) #passar a função 'datetime.utcnow' como parâmetro  para o default sem os '()' para que execute toda a vez que o usuário criar um post
  id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False) #o parâmetro 'usuario.id' cujo o 'usuario' é o nome da classe deve sempre estar em letra minúscula e o database.ForeignKey('usuario.id) deve ocupar a 2ª posição nos parâmetro