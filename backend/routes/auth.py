from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=data.get('role', 'manager')
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'message': 'Account created'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    login_user(user)
    return jsonify({'message': 'Logged in', 'data': {'name': user.name, 'email': user.email, 'role': user.role}})


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'data': {'name': current_user.name, 'email': current_user.email, 'role': current_user.role}})
