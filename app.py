from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret-key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "chat.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, default=10)

class TeacherGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, default=10)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=True)
    teacher_group_id = db.Column(db.Integer, db.ForeignKey("teacher_group.id"), nullable=True)

with app.app_context():
    db.create_all()

# ------------------ ROUTES ------------------

# ----------- REGISTER / ACCUEIL -----------
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if User.query.filter_by(username=username).first():
            return "Ce pseudo existe déjà, choisis-en un autre."
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/index")
def index():
    if "username" not in session:
        return redirect(url_for("register"))
    return render_template("index.html", username=session["username"])

# ----------- PUBLIC CHAT -----------
@app.route("/public_chat", methods=["GET", "POST"])
def public_chat():
    if "username" not in session:
        return redirect(url_for("register"))

    if request.method == "POST":
        content = request.form["message"]
        new_message = Message(content=content, username=session["username"], group_id=None, teacher_group_id=None)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("public_chat"))

    messages = Message.query.filter_by(group_id=None, teacher_group_id=None).all()
    return render_template("public_chat.html", messages=messages, username=session["username"])

# ----------- GROUPS -----------
@app.route("/groups")
def groups():
    groups = Group.query.all()
    return render_template("groups.html", groups=groups)

@app.route("/groups/create", methods=["GET", "POST"])
def create_group():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        size = request.form.get("size", 10)

        group = Group(name=name, password=password, size=size)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for("groups"))

    return render_template("create_group.html")

@app.route("/groups/<int:group_id>", methods=["GET", "POST"])
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)
    if request.method == "POST":
        msg = Message(content=request.form["content"], username=session["username"], group_id=group.id)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("group_chat", group_id=group.id))
    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp).all()
    return render_template("group_chat.html", group=group, messages=messages)

@app.route("/messages/<int:group_id>")
def get_messages(group_id):
    messages = Message.query.filter_by(group_id=group_id).order_by(Message.timestamp).all()
    return jsonify([{"user": m.username, "content": m.content, "time": m.timestamp.strftime("%H:%M")} for m in messages])

# ----------- TEACHERS -----------
@app.route("/teachers")
def teachers():
    groups = TeacherGroup.query.all()
    return render_template("teachers.html", groups=groups)

@app.route("/teachers/create", methods=["GET", "POST"])
def create_teacher_group():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        size = request.form.get("size", 10)

        group = TeacherGroup(name=name, password=password, size=size)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for("teachers"))

    return render_template("create_teacher_group.html")

@app.route("/teachers/<int:group_id>", methods=["GET", "POST"])
def teacher_chat(group_id):
    group = TeacherGroup.query.get_or_404(group_id)
    if request.method == "POST":
        msg = Message(content=request.form["content"], username=session["username"], teacher_group_id=group.id)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("teacher_chat", group_id=group.id))
    messages = Message.query.filter_by(teacher_group_id=group.id).order_by(Message.timestamp).all()
    return render_template("teacher_chat.html", group=group, messages=messages)

@app.route("/teacher_messages/<int:group_id>")
def get_teacher_messages(group_id):
    messages = Message.query.filter_by(teacher_group_id=group_id).order_by(Message.timestamp).all()
    return jsonify([{"user": m.username, "content": m.content, "time": m.timestamp.strftime("%H:%M")} for m in messages])

# ----------- ADMIN (accès secret) -----------
@app.route("/admin2013520")
def admin():
    groups = Group.query.all()
    teachers = TeacherGroup.query.all()
    return render_template("admin.html", groups=groups, teachers=teachers)

if __name__ == "__main__":
    app.run(debug=True)













