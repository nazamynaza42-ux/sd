from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------
# MODELES
# ------------------
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    messages = db.relationship("Message", backref="group", lazy=True)

class TeacherGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    messages = db.relationship("TeacherMessage", backref="teacher_group", lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)

class TeacherMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    teacher_group_id = db.Column(db.Integer, db.ForeignKey("teacher_group.id"), nullable=False)

class PublicMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

# ------------------
# CREATION DB
# ------------------
with app.app_context():
    if not os.path.exists("chat.db"):
        db.create_all()

# ------------------
# ROUTES
# ------------------

@app.route("/")
def index():
    return render_template("index.html")

# Chat public
@app.route("/public", methods=["GET", "POST"])
def public_chat():
    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            db.session.add(PublicMessage(content=msg))
            db.session.commit()
        return redirect(url_for("public_chat"))
    messages = PublicMessage.query.all()
    return render_template("public_chat.html", messages=messages)

# Groupes normaux
@app.route("/groups", methods=["GET", "POST"])
def groups():
    groups = Group.query.all()
    if request.method == "POST":
        group_id = request.form.get("group_id")
        password = request.form.get("password")
        group = Group.query.get(group_id)
        if group and group.password == password:
            session["group_id"] = group.id
            return redirect(url_for("group_chat", group_id=group.id))
    return render_template("groups.html", groups=groups)

@app.route("/group/<int:group_id>", methods=["GET", "POST"])
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)
    if "group_id" not in session or session["group_id"] != group.id:
        return redirect(url_for("groups"))

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            db.session.add(Message(content=msg, group_id=group.id))
            db.session.commit()
        return redirect(url_for("group_chat", group_id=group.id))

    messages = Message.query.filter_by(group_id=group.id).all()
    return render_template("group_chat.html", group=group, messages=messages)

# Enseignants
@app.route("/teachers", methods=["GET", "POST"])
def teachers():
    groups = TeacherGroup.query.all()
    if request.method == "POST":
        group_id = request.form.get("group_id")
        password = request.form.get("password")
        group = TeacherGroup.query.get(group_id)
        if group and group.password == password:
            session["teacher_group_id"] = group.id
            return redirect(url_for("teacher_chat", group_id=group.id))
    return render_template("teachers.html", groups=groups)

@app.route("/teacher/<int:group_id>", methods=["GET", "POST"])
def teacher_chat(group_id):
    group = TeacherGroup.query.get_or_404(group_id)
    if "teacher_group_id" not in session or session["teacher_group_id"] != group.id:
        return redirect(url_for("teachers"))

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            db.session.add(TeacherMessage(content=msg, teacher_group_id=group.id))
            db.session.commit()
        return redirect(url_for("teacher_chat", group_id=group.id))

    messages = TeacherMessage.query.filter_by(teacher_group_id=group.id).all()
    return render_template("teacher_chat.html", group=group, messages=messages)

# Admin direct via URL
@app.route("/admin2013520", methods=["GET", "POST"])
def admin_dashboard():
    groups = Group.query.all()
    teachers = TeacherGroup.query.all()

    if request.method == "POST":
        if "group_name" in request.form:  # Ajout groupe normal
            name = request.form.get("group_name")
            password = request.form.get("group_password")
            size = request.form.get("group_size")
            db.session.add(Group(name=name, password=password, size=int(size)))
            db.session.commit()
        elif "teacher_name" in request.form:  # Ajout groupe enseignant
            name = request.form.get("teacher_name")
            password = request.form.get("teacher_password")
            db.session.add(TeacherGroup(name=name, password=password))
            db.session.commit()
        return redirect(url_for("admin_dashboard"))

    return render_template("admin.html", groups=groups, teachers=teachers)

if __name__ == "__main__":
    app.run(debug=True)











