from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, ChatGroup, Message
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)

# --------------------- Flask-Admin ---------------------
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(ChatGroup, db.session))
admin.add_view(ModelView(Message, db.session))

# --------------------- Home page ---------------------
@app.route("/", methods=['GET', 'POST'])
def home():
    user_id = request.cookies.get("user_id")
    if not user_id:
        return redirect(url_for("set_username"))

    user = User.query.get(int(user_id))
    if request.method == "POST":
        content = request.form['content']
        if content.strip() != "":
            message = Message(content=content, user_id=user.id)
            db.session.add(message)
            db.session.commit()
        return redirect(url_for("home"))

    messages = Message.query.order_by(Message.id.asc()).all()
    return render_template("index.html", messages=messages, user=user)

# --------------------- Set username page ---------------------
@app.route("/set-username", methods=['GET', 'POST'])
def set_username():
    if request.method == "POST":
        username = request.form['username']
        if username.strip() == "":
            return render_template("set_username.html", error="Pseudo requis")
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        resp = make_response(redirect(url_for("home")))
        # Cookie permanent 10 ans
        resp.set_cookie("user_id", str(user.id), max_age=10*365*24*60*60)
        return resp

    return render_template("set_username.html")

# --------------------- API pour auto actualisation ---------------------
@app.route("/messages.json")
def messages_json():
    messages = Message.query.order_by(Message.id.asc()).all()
    return jsonify([
        {"username": msg.user.username, "content": msg.content} for msg in messages
    ])

# --------------------- Run ---------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)



