from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    _password_hash = Column(String)
    image_url = Column(String)
    bio = Column(String)
    recipes = relationship('Recipe', backref='user')

    @hybrid_property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password_input):
        self._password_hash = bcrypt.generate_password_hash(password_input).decode('utf-8')

    def check_password(self, password_input):
        return bcrypt.check_password_hash(self._password_hash, password_input)

    @property
    def password_hash(self):
        raise AttributeError('password_hash: write-only field')

    @password_hash.setter
    def password_hash(self, password_input):
        self._password_hash = bcrypt.generate_password_hash(password_input).decode('utf-8')
        
    def set_password(self, password_input):
        self._password_hash = bcrypt.generate_password_hash(password_input).decode('utf-8')
        
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'image_url': self.image_url,
            'recipes': [recipe.serialize() for recipe in self.recipes]
        }  
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        CheckConstraint("length(instructions) >= 50", name='instructions_length'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    minutes_to_complete = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
            'user_id': self.user_id
        }