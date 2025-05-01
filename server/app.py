#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
       
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        image_url = request.get_json().get('image_url')
        bio = request.get_json().get('bio')
        if not username or not password:
            return {'error': '422 Unprocessable Entity'}, 422
        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        
        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422
class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()    
            return user.to_dict(),200
        return {},401

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()

        password = request.get_json().get('password')
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200  
        return {'error':'Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return {'error':'Unauthorized'}, 401
        session['user_id'] = None
        return {},204

class RecipeIndex(Resource):
    def get(self):
        user_id = session['user_id']
        if not user_id:
            return {'error':'Unauthorized'}, 401
        user = User.query.get(user_id)
        if not user:
            return {'error':'Unauthorized'}, 401
        recipe = [recipe.to_dict() for recipe in user.recipes]
        return recipe, 200
    
    def post(self):
        user_id = session['user_id']
        if not user_id:
            return {'error':'Unauthorized'}, 401
        user = User.query.get(user_id)
        if not user:
            return {'error':'User not found'}, 401
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')
        if not title or not instructions or not minutes_to_complete:
            return {'error': '422 Unprocessable Entity'}, 422
        
        try:
            recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user=user
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except Exception as e:

            return {'error': 'Unprocessable Entity', 'message': str(e)}, 422
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)