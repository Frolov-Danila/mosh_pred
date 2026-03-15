from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request, JWTManager
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
jwt = JWTManager(app)

#Объект Пользователя
class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(String, nullable=False) #Сохраняем хэш
    role = Column(String, default='User')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    def get_token(self):
        return create_access_token(identity=str(self.id))
    

@app.route('/')
def main():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # if user.role == 'Admin':
        #     return redirect(url_for('admin'))
            
    except Exception:
        return redirect(url_for('auth'))

    return render_template('main.html', user=user)


#!Авторизация пользователя
@app.route("/login", methods=['GET', 'POST'])
def auth():
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
            return redirect(url_for('auth'))
    
    return render_template("auth.html")


#!Регистрация админом нового пользователя
@app.route("/admin", methods=['GET', 'POST'])
@jwt_required()
def admin():
    user = User.query.get_or_404(get_jwt_identity())

    if user.role != 'Admin':
        abort(403)

    if request.method == 'POST':
        data = request.form
        login = data.get("login")
        firstname = data.get("firstname")
        lastname = data.get('lastname')
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            abort(400)
        
        if not all([login, password]):
            abort(400)
        
        if User.query.filter_by(login=login).first():
            abort(400)

        else:
            user = User(login=login, password=User.hash_password(password), firstname=firstname, lastname=lastname)
            db.session.add(user)
            db.session.commit()
    return render_template("admin.html")


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all() 
        
        #! Автосоздание суперадмина
        admin = User(login='admin', password=User.hash_password('1234'), role='Admin', firstname='Данил', lastname='Колбасенко')
        db.session.add(admin)
        db.session.commit()

    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
)