import sys
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yrizk@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    # every row has a parent row in a table called todolists , the column is id.
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description} {self.completed}>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    # class name of the child object, backref is just the prefix of the child foreign key.
    todos = db.relationship('Todo', backref='list', lazy=True)

@app.route('/')
def index():
    return render_template('index.html', data=TodoList.query.order_by('id').all())

@app.route('/list/<list_id>', methods=['GET'])
def get_todos_from_list(list_id):
    return render_template('todos.html', data=Todo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/lists/create', methods=['POST'])
def create_todo_list():
    name = request.get_json()['name']
    t = TodoList(name=name)
    db.session.add(t)
    db.session.commit()
    body = {}
    body['name'] = t.name;
    body['id'] = t.id
    return jsonify(body)


@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
    body['id'] = todo.id
    body['completed'] = todo.completed
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/todos/<todo_id>/update', methods=['POST'])
def update_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        t = Todo.query.get(todo_id)
        st.completed = completed
        list_id = t.list_id
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_todos_from_list', list_id=list_id))
