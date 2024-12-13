import os
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///community_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    marketplace_items = db.relationship('MarketplaceItem', backref='seller', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)


class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ChatGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    messages = db.relationship('ChatMessage', backref='group', lazy=True)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_group.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


# Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

    # Create new user
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'success': True, 'message': 'Login successful'}), 200

    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


# Community Post Routes
@app.route('/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({'success': False, 'message': 'Post content required'}), 400

    new_post = Post(content=content, user_id=session['user_id'])

    try:
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Post created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    post_list = []

    for post in posts:
        post_list.append({
            'id': post.id,
            'content': post.content,
            'author': post.author.username,
            'likes': post.likes,
            'dislikes': post.dislikes
        })

    return jsonify(post_list), 200


# Marketplace Routes
@app.route('/marketplace/items', methods=['POST'])
def list_marketplace_item():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')

    if not all([name, price, category]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400

    new_item = MarketplaceItem(
        name=name,
        price=float(price),
        category=category,
        user_id=session['user_id']
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item listed successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/marketplace/items', methods=['GET'])
def get_marketplace_items():
    items = MarketplaceItem.query.all()
    item_list = []

    for item in items:
        item_list.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'category': item.category,
            'seller': item.seller.username
        })

    return jsonify(item_list), 200


# Chat Group Routes
@app.route('/chat/groups', methods=['POST'])
def create_chat_group():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'success': False, 'message': 'Group name required'}), 400

    new_group = ChatGroup(name=name)

    try:
        db.session.add(new_group)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Chat group created successfully',
            'group_id': new_group.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/chat/messages', methods=['POST'])
def send_chat_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    content = data.get('content')
    group_id = data.get('group_id')

    if not all([content, group_id]):
        return jsonify({'success': False, 'message': 'Content and group ID required'}), 400

    new_message = ChatMessage(
        content=content,
        user_id=session['user_id'],
        group_id=group_id
    )

    try:
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


# Initialize Database
@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':

    app.run(debug=True)