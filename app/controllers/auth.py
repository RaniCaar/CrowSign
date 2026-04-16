from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Faltan datos'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400
        
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Usuario creado correctamente'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({
            'message': 'Login exitoso', 
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    return jsonify({'error': 'Credenciales inválidas'}), 401
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Sesión cerrada'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
        
    from app.models.user import Follower
    followers_count = Follower.query.filter_by(followed_id=user.id).count()
    following_count = Follower.query.filter_by(follower_id=user.id).count()
        
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'identity': user.identity,
        'country': user.country,
        'age': user.age,
        'bio': user.bio,
        'profile_pic': user.profile_pic,
        'banner_pic': user.banner_pic,
        'followers': followers_count,
        'following': following_count
    }), 200
