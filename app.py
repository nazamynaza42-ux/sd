from flask import Flask, render_template, redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

# --------------------- App ---------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

# --------------------- Models ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class ChatGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    messages = db.relationship('Message', backref='group', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_group.id'), nullable=True)

# --------------------- Flask-Admin ---------------------
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(ChatGroup, db.session))
admin.add_view(ModelView(Message, db.session))

# --------------------- Routes ---------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        author = request.form.get("author")
        content = request.form.get("content")
        group_id = request.form.get("group_id")  # optionnel
        if author and content:
            new_msg = Message(author=author, content=content, group_id=group_id)
            db.session.add(new_msg)
            db.session.commit()
        return redirect(url_for("home"))

    groups = ChatGroup.query.all()
    messages = Message.query.all()
    return render_template("index.html", groups=groups, messages=messages)

@app.route("/admin/dashboard")
def admin_dashboard():
    groups = ChatGroup.query.all()
    messages = Message.query.all()
    return render_template("admin_dashboard.html", groups=groups, messages=messages)

@app.route("/admin/groups")
def admin_groups():
    groups = ChatGroup.query.all()
    return render_template("admin_groups.html", groups=groups)

@app.route("/admin/messages")
def admin_messages():
    messages = Message.query.all()
    return render_template("admin_messages.html", messages=messages)

# --------------------- Run ---------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


