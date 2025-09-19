from flask import Flask, render_template, request, redirect, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

# --------------------- Models ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class ChatGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_group.id'), nullable=True)
    group = db.relationship('ChatGroup', backref=db.backref('messages', lazy=True))

# --------------------- Flask-Admin ---------------------
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(ChatGroup, db.session))
admin.add_view(ModelView(Message, db.session))

# --------------------- Routes ---------------------
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        author = request.form['author']
        content = request.form['content']
        msg = Message(author=author, content=content)
        db.session.add(msg)
        db.session.commit()
        return redirect('/')
    
    groups = ChatGroup.query.all()
    messages = Message.query.order_by(Message.id.asc()).all()
    return render_template("index.html", groups=groups, messages=messages)

@app.route("/messages_json")
def messages_json():
    messages = Message.query.order_by(Message.id.asc()).all()
    messages_list = [{"author": m.author, "content": m.content} for m in messages]
    return jsonify(messages_list)

# --------------------- Run ---------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


