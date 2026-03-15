from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import Column, Integer, String
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['HOST'] = '127.0.0.1'
app.config['PORT'] = 8000

app.config['SECRET_KEY'] = 'secret_key' # !! изменить
app.config['JWT_SECRET_KEY'] = 'secret_key' # !! изменить
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2) # Длительность токена для входа
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

csrf = CSRFProtect(app)
db = SQLAlchemy()
db.init_app(app)

#Объект Пользователя
class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) #Сохраняем хэш

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    def get_token():
        return create_access_token(identity=str(self.id))
    

@app.route('/')
def main():
    return render_template('main.html')


#!Авторизация пользователя
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(login=login).first()
        
        if user and user.check_password(password):
            # Создание JWT токена
            access_token = user.get_token()
            response = redirect(url_for('main'))
            response.set_cookie('access_token_cookie', access_token, httponly=True, max_age=3600)
            
            return response
        else:
            return redirect(url_for('login'))
    
    return render_template("auth.html")

@app.route("/valid_accuracy")
def val_acc():
    html_content = open("templates/val_acc.html", "r")
    response = make_response(html_content, 200) # 200 is the status code
    response.mimetype = 'text/html'
    return response

#!Регистрация админом нового пользователя
@app.route("/register", methods=['GET', 'POST'])
@jwt_required
def admin():
    if request.method == 'POST':
        data = request.form
        login = data.get("firstname")
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            flash("Пароли не совпадают.", "danger")
        
        if not all([login, password]):
            flash("Введите все даннные", "danger")
        
        if User.query.filter_by(login=login).first():
            flash("Пользователь уже зарегистрирован", "danger")

        else:
            user = User(login=login, password=User.hash_password(password), role=data.get("role", "Student"))
            db.session.add(user)
            db.session.commit()
        
            flash("Пользователь успешно создан", "success")
    return render_template("admin.html")


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all() 
    #TODO: Добавть автосоздание 1 админа

    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
)