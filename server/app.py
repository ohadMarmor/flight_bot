import csv
import json

import nltk
from flask import Flask, request, jsonify, current_app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from database import db, init_db
from models import User, Conversation, Message, FlightProfile

import jwt
from flask_cors import CORS

from rec_system import get_recommendation
from services import decode_jwt

from flight_bot_nlp import response_bot


app = Flask(__name__)
CORS(app)

app.config['JWT_TOKEN_LOCATION'] = ['headers']


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbproject.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
nltk.download('wordnet')


"""@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return [{"email": user.email, "password": user.password, "name": user.name}
            for user in users]
"""


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    if User.query.filter_by(email=email).first():
        return {"message": "user already exists"}, 400
    password_hash = generate_password_hash(data['password'], method='sha256')
    user = User(email=data['email'], password=password_hash, name=data['name'])
    db.session.add(user)
    db.session.commit()
    r = {"email": user.email, "password": user.password, "name": user.name}
    conversation = Conversation(email=email)
    db.session.add(conversation)
    db.session.commit()
    flight_profile = FlightProfile(conversation_id=conversation.conversation_id)
    db.session.add(flight_profile)
    db.session.commit()

    return r


@app.route('/api/users', methods=['GET'])
def get_user():
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    email = decoded.get('sub')

    if email:
        user = User.query.get(email)
        if user:
            r = {"email": user.email, "password": user.password, "name": user.name}
            return r
        else:
            return jsonify({'error': 'User not found'}), 404


@app.route('/api/users/<string:email>', methods=['DELETE'])
def delete_user(email):
    user = User.query.get(email)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User successfully deleted'})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/api/conversations', methods=['GET'])
def get_user_conversations():
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    email = decoded.get('sub')

    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            conversations = Conversation.query.filter_by(email=email).all()
            response = [
                {
                    'conversation_id': conversation.conversation_id,
                    'email': conversation.email
                }
                for conversation in conversations
            ]
            return jsonify(response), 200

    return jsonify({'error': 'User not found.'}), 404


@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    email = decoded.get('sub')
    if email:
        user = User.query.get(email)
        if user:
            conversation = Conversation(email=email)
            db.session.add(conversation)
            db.session.commit()
            # Create a flight profile for the conversation
            flight_profile = FlightProfile(conversation_id=conversation.conversation_id)
            db.session.add(flight_profile)
            db.session.commit()
            r = {"conversation_id": conversation.conversation_id, "email": conversation.email}
            return r
        else:
            return jsonify({'error': 'User not found'}), 404

    return jsonify({'error': 'User not found.'}), 404


@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    email = decoded.get('sub')
    if email:
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            r = {"conversation_id": conversation.conversation_id, "email": conversation.email}
            return r
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    return jsonify({'error': 'User not found.'}), 404


@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    if conversation:
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({'message': 'Conversation successfully deleted'})
    else:
        return jsonify({'error': 'Conversation not found'}), 404


@app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    # Retrieve the conversation
    conversation = Conversation.query.get_or_404(conversation_id)

    # Retrieve the messages for the conversation
    messages = Message.query.filter_by(conversation_id=conversation.conversation_id).all()

    # Build the response
    response = [
        {
            'message_id': message.message_id,
            'content': message.content,
            'time': message.time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_user': message.is_user,
            'conversation_id': message.conversation_id
        }
        for message in messages
    ]

    return jsonify(response), 200


@app.route('/api/messages', methods=['POST'])
def create_message():
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    data = request.json
    conversation = Conversation.query.get(data['conversation_id'])
    if conversation:
        # create a message model from the content and the other details.
        message = Message(content=data['content'], is_user=data['is_user'], conversation_id=data['conversation_id'])
        messages = conversation.messages
        flight_profile = conversation.flight_profile
        response, new_preferences = response_bot(messages, message.content, flight_profile)
        flight_profile.preferences = new_preferences
        # Save the changes in flight_profile
        db.session.commit()
        # we add the message to the DB only after the bot handled it
        db.session.add(message)
        db.session.commit()
        # now we add the response from the bot to the DB
        message = Message(content=response, is_user=False, conversation_id=data['conversation_id'])
        db.session.add(message)
        db.session.commit()
        fixed_content = message.content.replace('[', '').replace(']', '')
        # return the message from the bot as a sign to success and also so the client side would upadte it in the prompt
        r = {"message_id": message.message_id, "content": fixed_content, "time": message.time,
             "is_user": message.is_user, "conversation_id": message.conversation_id}
        return r
    else:
        return jsonify({'error': 'Conversation not found'}), 404


@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    message = Message.query.get(message_id)
    if message:
        r = {"message_id": message.message_id, "content": message.content, "time": message.time,
             "is_user": message.is_user, "conversation_id": message.conversation_id}
        return r
    else:
        return jsonify({'error': 'Message not found'}), 404


@app.route('/api/conversations/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = User.query.get(message_id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message successfully deleted'})
    else:
        return jsonify({'error': 'Message not found'}), 404


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # login successful

        # generate access token and return it:
        app.config['SECRET_KEY'] = email
        token = jwt.encode({
            'sub': user.email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, app.config.get('SECRET_KEY'), algorithm='HS256')
        return jsonify({'access_token': token})
    else:
        return {"message": "invalid credentials"}, 401


@app.route('/api/recommendation', methods=['GET'])
def get_recommendation_by_id():
    decoded = decode_jwt(app)

    if 'error' in decoded:
        return jsonify({'error': decoded['error']}), 401

    user_id = decoded.get('sub')
    if user_id:
        recommendation = get_recommendation(user_id)
        if recommendation:
            return jsonify({'recommendation': recommendation}), 200
        else:
            return jsonify({'error': 'No recommendation available'}), 404
    return jsonify({'error': 'User not found.'}), 404


if __name__ == '__main__':
    app.run(debug=True)
