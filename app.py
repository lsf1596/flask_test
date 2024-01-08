# app.py
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import SearchQueryMixin
import secrets
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/test1' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_bytes(32) # 设置一个随机的密钥用于 Flask-Admin
db = SQLAlchemy(app)
admin = Admin(app)
migrate = Migrate(app, db)

class User(db.Model, SearchQueryMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    

class UserAdminView(ModelView):
    can_search = True
    column_searchable_list = ['username', 'email']

# 添加 UserAdminView 模型到 Flask-Admin
admin.add_view(UserAdminView(User, db.session))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:
            return "密码不匹配，请重新输入。"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "该用户名已被注册，请选择其他用户名。"
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return "注册成功！"
    return render_template('register.html')
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # 登录成功，可以进行进一步的处理
            return redirect(url_for("admin.index"))
        else:
            return "登录失败，请检查用户名和密码。"
if __name__ == '__main__':
    app.run(debug=True)
