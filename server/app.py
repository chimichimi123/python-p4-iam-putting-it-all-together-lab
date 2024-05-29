#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api, bcrypt
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        if not username or not password:
            return {'error': 'Username and password are required'}, 422

        new_user = User(
            username=username,
            bio=bio,
            image_url=image_url
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            serialized_user = new_user.serialize()
            return jsonify(serialized_user), 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists'}, 422
        except Exception as e:
            db.session.rollback()
            return {'error': 'An error occurred: {}'.format(str(e))}, 500


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'No active session'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return jsonify(user.serialize())


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify(user.serialize())
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return '', 204
        else:
            return {'error': 'No active session'}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'No active session'}, 401

        try:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            return jsonify([recipe.serialize() for recipe in recipes]), 200
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'No active session'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or len(instructions) < 50:
            return {'error': 'Title and instructions (at least 50 characters) are required'}, 422

        try:
            new_recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )

            db.session.add(new_recipe)
            db.session.commit()
            return jsonify(new_recipe.serialize()), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)