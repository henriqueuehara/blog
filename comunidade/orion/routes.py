from flask import render_template, redirect, url_for, flash, request, abort
from orion import app, database, bcrypt
from orion.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from orion.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('home.html', posts=posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        #obter usuário
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        #verifica dados de acesso
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            #faz o login efetivamento do usuário e gerencia se o usuário marcou a opção para manter-se conectado           
            login_user(usuario, remember=form_login.lembrar_dados.data) 
            #exibir mensagem fez login com sucesso
            flash(f'login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
            #redirecionar o usuário
            par_next = request.args.get('next') #pega o valor que está no parâmetro next
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
           flash('Falha no login', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        #criptografar a senha
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        #criar o usuário
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        #adicionar a seção ao banco de dados
        database.session.add(usuario)
        #commit na seção
        database.session.commit()
        #criou conta com sucesso
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        #redirecionar o usuário
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route("/contato")
def contato():
    return render_template('contato.html')

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)  

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout Feito Com Sucesso', 'alert-success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado Com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_arquivo = salvar_imagem(form.foto_perfil.data)
            #mudar o campo foto_perfil do usuário para o novo nome da imagem
            current_user.foto_perfil = nome_arquivo
        current_user.classes_ativos = atualizar_classes_ativos(form)
        database.session.commit()
        flash('Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET': #caso estaja somente carregando o formulário
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado Com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None

    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)


def salvar_imagem(imagem):
    #adicionar um código aleatório no nome da imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    #reduzir o tamanho da imagem
    tamanho = (200, 200) #define as dimensões da imagem que será salva no banco de dados
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    #retorna o nome da imagem concatenado com o código e com a extesão
    return nome_arquivo

def atualizar_classes_ativos(form):
    lista_classes_ativos = []
    for campo in form:
        if 'a_' in campo.name:
            if campo.data:
                #adicionar o texto do campo.label ('Renda Fixa Nacional') na lista de classes_ativos
                lista_classes_ativos.append(campo.label.text)
    return ';'.join(lista_classes_ativos)