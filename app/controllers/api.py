import os
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from app.models.user import User, Follower
from app.models.comment import Comment
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

UPLOAD_FOLDER = os.path.join('app', 'static', 'img', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload_image', methods=['POST'])
def upload_image():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'No autorizado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Archivo no seleccionado'}), 400
        
    image_type = request.form.get('type') # 'avatar' or 'banner'
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{user_id}_{image_type}_{file.filename}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Act DB
        user = User.query.get(user_id)
        img_url = f"/static/img/uploads/{filename}"
        if image_type == 'avatar':
            user.profile_pic = img_url
        elif image_type == 'banner':
            user.banner_pic = img_url
            
        db.session.commit()
        return jsonify({'message': 'Imagen actualizada', 'url': img_url}), 200

    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@api_bp.route('/profile', methods=['PUT'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
        
    data = request.json
    user = User.query.get(user_id)
    
    if 'identity' in data: user.identity = data['identity']
    if 'age' in data: user.age = data['age']
    if 'bio' in data: user.bio = data['bio']
    if 'country' in data: user.country = data['country']
        
    db.session.commit()
    return jsonify({'message': 'Perfil actualizado'}), 200

@api_bp.route('/profile/<int:target_id>/comments', methods=['POST', 'GET'])
def profile_comments(target_id):
    if request.method == 'GET':
        comments = Comment.query.filter_by(profile_id=target_id).order_by(Comment.created_at.desc()).all()
        result = []
        for c in comments:
            author = User.query.get(c.author_id)
            # Count reactions for this comment
            from app.models.comment import CommentReaction
            reaction_count = CommentReaction.query.filter_by(comment_id=c.id).count()
            
            # Did the current user react?
            user_id = session.get('user_id')
            user_reacted = False
            if user_id:
                user_reacted = CommentReaction.query.filter_by(comment_id=c.id, user_id=user_id).first() is not None

            result.append({
                'id': c.id,
                'content': c.content,
                'author': author.username if author else 'Anonimo',
                'author_id': author.id if author else None,
                'created_at': c.created_at.isoformat(),
                'reactions': reaction_count,
                'user_reacted': user_reacted
            })
        return jsonify(result), 200
        
    # POST
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401
        
    if user_id == target_id:
        return jsonify({'error': 'No puedes comentar en tu propio muro'}), 403
        
    data = request.json
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'El contenido no puede estar vacío'}), 400
        
    new_comment = Comment(content=content, author_id=user_id, profile_id=target_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comentario publicado'}), 201

@api_bp.route('/comments/<int:comment_id>/react', methods=['POST'])
def react_comment(comment_id):
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'No autorizado'}), 401
    
    from app.models.comment import CommentReaction
    reaction = CommentReaction.query.filter_by(comment_id=comment_id, user_id=user_id).first()
    
    if reaction:
        db.session.delete(reaction) # Toggle off
        db.session.commit()
        return jsonify({'message': 'Reacción eliminada', 'reacted': False}), 200
    else:
        new_react = CommentReaction(comment_id=comment_id, user_id=user_id)
        db.session.add(new_react)
        db.session.commit()
        return jsonify({'message': 'Reacción agregada', 'reacted': True}), 200

@api_bp.route('/users/search', methods=['GET'])
def search_users():
    q = request.args.get('q', '').strip()
    if not q: return jsonify([])
    
    users = User.query.filter(User.username.ilike(f'%{q}%')).all()
    res = [{'id': u.id, 'username': u.username, 'profile_pic': u.profile_pic} for u in users]
    return jsonify(res), 200

@api_bp.route('/profile/<int:user_id>/details', methods=['GET'])
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    followers_count = Follower.query.filter_by(followed_id=user_id).count()
    following_count = Follower.query.filter_by(follower_id=user_id).count()
    
    current_user_id = session.get('user_id')
    is_following = False
    if current_user_id:
        is_following = Follower.query.filter_by(follower_id=current_user_id, followed_id=user_id).first() is not None
        
    return jsonify({
        'id': user.id,
        'username': user.username,
        'identity': user.identity,
        'age': user.age,
        'country': user.country,
        'bio': user.bio,
        'profile_pic': user.profile_pic,
        'banner_pic': user.banner_pic,
        'followers': followers_count,
        'following': following_count,
        'is_following': is_following,
        'is_me': user.id == current_user_id
    }), 200

@api_bp.route('/profile/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    current_uid = session.get('user_id')
    if not current_uid: return jsonify({'error': 'No autorizado'}), 401
    if current_uid == user_id: return jsonify({'error': 'No puedes seguirte a ti mismo'}), 400
    
    existing = Follower.query.filter_by(follower_id=current_uid, followed_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'message': 'Dejaste de seguir', 'is_following': False}), 200
    else:
        new_follow = Follower(follower_id=current_uid, followed_id=user_id)
        db.session.add(new_follow)
        db.session.commit()
        return jsonify({'message': 'Siguiendo', 'is_following': True}), 200

