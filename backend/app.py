from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User
from routes import auth_bp, products_bp, orders_bp, contacts_bp
from populate_db import seed_db

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
)

CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

db.init_app(app)
with app.app_context():
  db.create_all()
  seed_db()

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(contacts_bp, url_prefix='/api')


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

if __name__ == '__main__':
  app.run(debug=True)
