from flask import Blueprint, render_template, request, redirect, url_for, g
from todor.auth import login_required

from .models import Todo, User
from todor import db


bp = Blueprint('todo', __name__, url_prefix='/todo')


@bp.route('/list')
#decorador: dice que debe iniciar sesión
@login_required
def index():
    #recuperamos todos los todos, todos los datos
    todos = Todo.query.all()
    #renderizamos la plantilla 'todo/index.html'
    return render_template('todo/index.html', todos = todos)


@bp.route('/create', methods=('GET', 'POST'))
#para esta seccion se requiere inicar seccion
@login_required
def create():
    #capturamos los datos desde la bd
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        #creamos una tarea
        todo = Todo(g.user.id, title, desc)

        #guardamos en la bd
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo.index'))
    return render_template('todo/create.html')

def get_todo(id):
    # si no esncuentra una tarea devuelve un error 
    todo = Todo.query.get_or_404(id)
    return todo

                #para recibir el id
@bp.route('/update/<int:id>', methods=('GET', 'POST'))
#para esta seccion se requiere inicar seccion
@login_required
def update(id):
    #busca en la bd el todo con ese id y lo guarda en la variable todo
    todo = get_todo(id)
    
    #modificar los valores
    if request.method == 'POST':
        
        todo.title = request.form['title']
        todo.desc = request.form['desc']    #nombre del checkbox: state
        #el todo.state = True cuando request.form.get('state') sea on, si no es asi guardamos un false
        todo.state = True if request.form.get('state') == 'on' else False

        db.session.commit()

        return redirect(url_for('todo.index'))
    return render_template('todo/update.html', todo = todo)

@bp.route('/delete/<int:id>')
#para esta seccion se requiere inicar seccion
@login_required
def delete(id):
    #
    todo = get_todo(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo.index'))