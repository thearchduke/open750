#!/usr/bin/env python

'''
Database models for open750. This work is distributed under the GPL, waivers, limitations etc.
Copyright J. Tynan Burke 2016 http://www.tynanburke.com

#TODO: there's a lot of session commits going on here, we can consolidate that
'''

# Standard flask/sqlalchemy imports
from sqlalchemy import Table, Column, Integer, String, DateTime, PickleType, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from passlib.hash import sha256_crypt
import sys
import os
import re
import string

# Standard database connection infrastructure (set echo=False when you're done testing)
Base = declarative_base()
db = create_engine('sqlite:///open750.db', echo=False)

# Open the session
metadata = MetaData(db)
Session = sessionmaker(bind=db)
session = Session()


## sentiment analysis
#TODO: add credit
#TODO: right now this skips punctuation stripping for unicode text; that is,
#   text that can't convert to str doesn't get stripped.
class AFINN(object):
    def analyze_sentiment(self, text):
        try:
            text = str(text).translate(string.maketrans("",""), string.punctuation)
        except:
            pass
        return sum(map(lambda word: self.sentiment_dict.get(word, 0), text.lower().split()))

    def __init__(self, corpus):
        self.sentiment_dict = corpus


class AFINN_Data(Base):
    __tablename__ = 'afinn_data'
    id = Column(Integer, primary_key=True)
    store = Column(PickleType)

    def __init__(self):
        self.store = dict(map(lambda (k,v): (k,int(v)), [ line.split('\t') for line in open("open750/static/data/AFINN-111.txt") ]))

try:
    afinn = AFINN(session.query(AFINN_Data).first().store)
except:
    afinn = None


### Tables!

## Index & association tables

# Association table for posts and hashtags many-to-many
association_table = Table('association', Base.metadata,
    Column('post_id', Integer, ForeignKey('seven_fifties.id')),
    Column('hash_id', Integer, ForeignKey('hash_tags.id'))
)


## Tables for objects

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
    sentiment = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates='posts')

    hashtags = relationship("HashTag", secondary=association_table, back_populates="posts")

    def update_hashes(self):
        current = self.hashtags
        new = []
        re_hash = re.compile(ur'(\s+|^)(#[^\s]*)\b')
        hashes = [s[1] for s in re.findall(re_hash, self.text)]
        for h in hashes:
            tag = HashTag.create_or_add(h, self)
            new.append(tag)
        to_remove = set(current) - set(new)
        for h in to_remove:
            self.hashtags.remove(h)

    def update_object(self, save=True):
        self.wordCount = len(self.text.split())
        self.update_hashes()
        self.slug = self.text[0:63]
        self.sentiment = afinn.analyze_sentiment(self.text)

        #TODO: Save just for commit, not add? Need to read session docs
        if save:
            session.add(self)
            session.commit()


    def __init__(self, text, user_id):
        self.date = datetime.datetime.now()
        self.text = text
        self.wordCount = len(self.text.split()) 
        self.slug = self.text[0:63]
        self.user_id = user_id
        self.user = session.query(User).filter(User.id == self.user_id).first()
        self.update_hashes()
        self.sentiment = afinn.analyze_sentiment(self.text)

    def __repr__(self):
        return "'%s' on %s (sentiment: %s)" % (self.slug, str(self.date), str(self.sentiment))


## hashtags are all lowercase
class HashTag(Base):
    __tablename__ = 'hash_tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024), unique=True)
    posts = relationship("SevenFifty", secondary=association_table, back_populates="hashtags")


    @classmethod
    def create_or_add(cls, name, post=None):
        name = name.lower()
        test = session.query(cls).filter(cls.name == name).first()
        entity = None
        if test:
            entity = test
        else:
            entity = cls(name=name)
        if post:
            if post in entity.posts:
                pass
            else:
                entity.posts.append(post)
        session.add(entity)
        session.commit()
        return entity

    def __repr__(self):
        return "'%s' (%s)" % (self.name, str(self.posts))


## Run models.py independently to create tables
#TODO: testing
if __name__ == "__main__":
    Base.metadata.create_all(db)
    try:
        if sys.argv[1] == 'mock':
            afinn_data = AFINN_Data()
            session.add(afinn_data)
            session.commit()

            afinn = AFINN(session.query(AFINN_Data).first().store)
            user1 = User('user1', 'password1', 'email1')
            user2 = User('user2', 'password2', 'email2')
            post1 = SevenFifty('was it a #bar or a #bat i #saw', 1)
            post2 = SevenFifty('a man, a plan, a canal: panama. i #SAW the ships, i #saw them!', 1)
            post3 = SevenFifty('gazing into the darkness, a #bat #flew #by', 2)
            post4 = SevenFifty('i saw #a #creature driven and derided #by vanity', 2)
            post5 = SevenFifty('and my eyes burned with anger and anguish, so i went to the #BAR.', 2)
            session.bulk_save_objects([user1, user2, post1, post2, post3, post4, post5, afinn_data])
            session.commit()

        if sys.argv[1] == 'test':
            print afinn.analyze_sentiment("well that went well. and good, good good, better best. enough!")
            #14
            print afinn.analyze_sentiment("that was the worst goddamned opera i ever saw, it was terrible, i hated it.")
            #-9
            print afinn.analyze_sentiment("that. was. the. worst. goddamned. opera. i. ever. saw, it. was. terrible, i hated it.")
            #-9
    except IndexError:
        pass