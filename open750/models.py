#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Database models for open750. This work is distributed under the GPL, waivers, limitations etc.
Copyright J. Tynan Burke 2016 http://www.tynanburke.com

#TODO: there's a lot of session commits going on here, we can consolidate that
'''

# Standard flask/sqlalchemy imports
from sqlalchemy import Table, Column, Integer, String, DateTime, PickleType, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import datetime
from passlib.hash import sha256_crypt
import sys
import os
import re
import string

# Standard database connection infrastructure (set echo=False when you're done testing)
Base = declarative_base()
db = create_engine('sqlite:///750.db', echo=False)

# Open the session
metadata = MetaData(db)
session = scoped_session(sessionmaker(bind=db))

#TODO: switch to flask-sqlalchemy library
#Session = sessionmaker(bind=db)
#session = Session()


## sentiment analysis
#TODO: right now this skips punctuation stripping for unicode text; that is,
#   text that can't convert to str doesn't get stripped.
class AFINN(object):
    '''
    A sentiment analyzer. Run analyze_sentiment(t) on text t.
    Couples with AFINN_Data to load corpus into memory for web app.

    class AFINN is derived from the AFINN dataset, which has the following attribution:
    AFINN is a list of English words rated for valence with an integer
    between minus five (negative) and plus five (positive). The words have
    been manually labeled by Finn Årup Nielsen in 2009-2011. The file
    is tab-separated. There are two versions:

    AFINN-111: Newest version with 2477 words and phrases.

    AFINN-96: 1468 unique words and phrases on 1480 lines. Note that there
    are 1480 lines, as some words are listed twice. The word list in not
    entirely in alphabetic ordering.  

    An evaluation of the word list is available in:

    Finn Årup Nielsen, "A new ANEW: Evaluation of a word list for
    sentiment analysis in microblogs", http://arxiv.org/abs/1103.2903

    The list was used in: 

    Lars Kai Hansen, Adam Arvidsson, Finn Årup Nielsen, Elanor Colleoni,
    Michael Etter, "Good Friends, Bad News - Affect and Virality in
    Twitter", The 2011 International Workshop on Social Computing,
    Network, and Services (SocialComNet 2011).


    This database of words is copyright protected and distributed under
    "Open Database License (ODbL) v1.0"
    http://www.opendatacommons.org/licenses/odbl/1.0/ or a similar
    copyleft license.

    See comments on the word list here:
    http://fnielsen.posterous.com/old-anew-a-sentiment-about-sentiment-analysis
    '''
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
    try:
        if sys.argv[1] == 'init':
            Base.metadata.create_all(db)
            afinn_data = AFINN_Data()
            session.add(afinn_data)
            session.commit()

        elif sys.argv[1] == 'mock':
            afinn = AFINN(session.query(AFINN_Data).first().store)
            user1 = User('user1', 'password1', 'email1')
            user2 = User('user2', 'password2', 'email2')
            session.bulk_save_objects([user1,user2])
            post1 = SevenFifty('was it a #bar or a #bat i #saw', 1)
            post2 = SevenFifty('a man, a plan, a canal: panama. i #SAW the ships, i #saw them!', 1)
            post3 = SevenFifty('gazing into the darkness, a #bat #flew #by', 2)
            post4 = SevenFifty('i saw #a #creature driven and derided #by vanity', 2)
            post5 = SevenFifty('and my eyes burned with anger and anguish, so i went to the #BAR.', 2)
            session.bulk_save_objects([post1, post2, post3, post4, post5])
            session.commit()# is this necessary?
        else:
            print 'argument %s not found' % sys.argv[1]            

    except IndexError:
        print 'argument not provided'