#!/usr/bin/env python

'''
Database models for open750. This work is distributed under the GPL, waivers, limitations etc.
J. Tynan Burke 2016 http://www.tynanburke.com

#TODO: Implement users and stuff, I guess
'''

# Standard flask/sqlalchemy imports
from sqlalchemy import Table, Column, Integer, String, DateTime, Text, MetaData, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

# Standard database connection infrastructure
Base = declarative_base()
db = create_engine('sqlite:///open750.db', echo=True)

# Open the session
metadata = MetaData(db)
Session = sessionmaker(bind=db)
session = Session()


### Tables!

## Index tables
# none


## Objects we actually use
# Scribble()! 
class Scribble(Base):
    __tablename__ = 'scribbles'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    wordCount = Column(Integer)
    text = Column(Text)
    slug = Column(String(64))

    def __init__(self, text):
        self.date = datetime.datetime.now()
        self.text = text
        self.wordCount = len(self.text.split())
        self.slug = self.text[0:63]

    def __repr__(self):
        return "'%s' on %s" % (self.slug, str(self.date))

## Run models.py independently to create tables
if __name__ == "__main__":
    Base.metadata.create_all(db)
