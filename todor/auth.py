from flask import (
    Blueprint, render_template, request, url_for, redirect, flash, session, g 
    )
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from todor import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods= ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #creamos el objeto
        user = User(username, generate_password_hash(password))
        #buscamos en la bd un nombre que sea igual al que se esta registrando
        #si existe se asigna a la variable user_name, de lo contrario devuelve None
        
        error = None

        user_name = User.query.filter_by(username = username).first()
        #validamos si existe
        if user_name == None:
            #si no existe lo agregamos
            db.session.add(user)
            #para quye se realice los cambios en la db:
            db.session.commit()
            #una vez que te registras te redirecciona a iniciar sesion
            return redirect(url_for('auth.login'))
        else:   #si existe: 
            error = f'el usuario {username} ya esta registrado'
        #para mostrar este error diseñamos en base.html
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods= ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
                
        error = None

        user = User.query.filter_by(username = username).first()
        #validar datos
        if user == None:
            error = 'Nombre de usuario incorrecto.'
        #si tampoco existe =  elif not
        elif not check_password_hash(user.password, password):
            error = 'Contraseña incorrecta.'
            
        
        #Iniciar sesión, si no hay error:  if error is None:
        if error is None:
            #si hay una sesión iniciada lo limpia
            session.clear()
            #cuando iniciamos sesion en la clave: ['user_id'] guardamos el nombre de usuario que ha iniciado sesion 
            session['user_id'] = user.id
            return redirect(url_for('todo.index'))
        
        flash(error)
    return render_template('auth/login.html')



#MANTENER SESIÓN INICIADA

#registramos la funcion: load_loged_in_user para que se ejecute en cada peticion, si ingresamos en otras partes de la app se va a ejecutar primero: @bp.before_app_request/def load_loged_in_user():
@bp.before_app_request
def load_loged_in_user():
    #                      clave que usamos anteriormente: session['user_id'] 
    #si alguien inicio sesion, intentamos recuperar ese user_id
    #si nadie inicio sesion nos devuelve un valor nulo en session.get
    user_id = session.get('user_id')
    #si user_id es None es porque nadie ha iniciado sesión
    if user_id is None:
        #creamos un objeto y le enviamos un valor nulo porque nadie ha iniciado sesion
        g.user = None
    #si alguien inicio sesion: 
    else:
        #realizamos una consulta a la bd - si existe un usuario en la bd devuelve el usuario y lo guarda en g.user, de lo contrario devuelve un error get_or_404
        g.user = User.query.get_or_404(user_id)


#CERRAR SESION
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#PARA NO ACCEDER A UNA SECCION SIN INICIAR SESIÓN 
import functools

#creamos una funcion decoradora y en los parametros recibimos una vista . capturamos la vista
def login_required(view):
    #usamos la decoradora y le enviamos la vista
    @functools.wraps(view)
    #decoramos la funcion, recibe parametros indefinidos
    def wrapped_view(**kwargs):
        #si un usuario ha iniciado sesión: si es None
        if g.user is None:
            #redireccione a login
            return redirect(url_for('auth.login'))
        #si ha iniciado sesion devuelve la vista origianl
        return view(**kwargs)
    #devuelve la funcion 
    return wrapped_view

