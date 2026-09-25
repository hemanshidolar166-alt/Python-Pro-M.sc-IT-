
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))
    priority = db.Column(db.String(20))
    is_completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)


# Create database
with app.app_context():
    db.create_all()


# Home page
@app.route('/')
def index():
    pending_tasks = Task.query.filter_by(is_completed=False).all()
    completed_tasks = Task.query.filter_by(is_completed=True).all()

    return render_template(
        'index.html',
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


# Add task
@app.route('/add', methods=['POST'])
def add_task():
    due_date = request.form['due_date']

    task = Task(
        title=request.form['title'],
        description=request.form['description'],
        priority=request.form['priority'],
        due_date=datetime.strptime(
            due_date, '%Y-%m-%d'
        ).date() if due_date else None
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for('index'))


# Complete / Uncomplete task
@app.route('/toggle/<int:id>')
def toggle_task(id):
    task = Task.query.get_or_404(id)

    task.is_completed = not task.is_completed

    db.session.commit()

    return redirect(url_for('index'))


# Update task
@app.route('/update/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)

    task.title = request.form['title']
    task.description = request.form['description']
    task.priority = request.form['priority']

    due_date = request.form['due_date']

    if due_date:
        task.due_date = datetime.strptime(
            due_date, '%Y-%m-%d'
        ).date()
    else:
        task.due_date = None

    db.session.commit()

    return "Updated Successfully"


# Delete task
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)

    db.session.delete(task)
    db.session.commit()

    return "Deleted Successfully"


# Run application
if __name__ == '__main__':
    app.run(debug=True)
