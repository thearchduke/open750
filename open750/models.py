#!/usr/bin/env python

'''
Database models for open750. This work is distributed under the GPL, waivers, limitations etc.
Copyright J. Tynan Burke 2016 http://www.tynanburke.com

#TODO: Implement users and stuff, I guess
'''

# Standard flask/sqlalchemy imports
from sqlalchemy import Table, Column, Integer, String, DateTime, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from passlib.hash import sha256_crypt
import sys

# Standard database connection infrastructure (set echo=False when you're done testing)
Base = declarative_base()
db = create_engine('sqlite:///open750.db', echo=False)

# Open the session
metadata = MetaData(db)
Session = sessionmaker(bind=db)
session = Session()


### Tables!

## Index tables
# none


## Objects we actually use

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    email = Column(String(64))
    hashed_password = Column(String(256))
    posts = relationship('SevenFifty', back_populates='user')

    def hash_password(self, password):
        hashed_password = sha256_crypt.encrypt(password)
        return hashed_password

    def verify_password(self, challenge):
        test = sha256_crypt.verify(challenge, self.hashed_password)
        return test

    def __init__(self, name, password, email=None):
        self.name = name
        self.email = email
        self.hashed_password = self.hash_password(password)


class SevenFifty(Base):
    __tablename__ = 'seven_fifties'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    wordCount = Column(Integer)
    text = Column(Text)
    slug = Column(String(64))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates='posts')

    def __init__(self, text, user_id):
        self.date = datetime.datetime.now()
        self.text = text
        self.wordCount = len(self.text.split(' ')) - 1
        self.slug = self.text[0:63]
        self.user_id = user_id

    def __repr__(self):
        return "'%s' on %s" % (self.slug, str(self.date))



## Run models.py independently to create tables
if __name__ == "__main__":
    Base.metadata.create_all(db)

    if sys.argv[1] == 'mock':
        user1 = User('user1', 'password1', 'email1')
        user2 = User('user2', 'password2', 'email2')
        post1 = SevenFifty('was it a bar or a bat i saw', 1)
        post2 = SevenFifty('a man, a plan, a canal: panama', 1)
        post3 = SevenFifty('gazing into the darkness', 2)
        post4 = SevenFifty('i saw a creature driven and derided by vanity', 2)
        post5 = SevenFifty('and my eyes burned with anger and anguish.', 2)
        session.bulk_save_objects([user1, user2, post1, post2, post3, post4, post5])
        session.commit()