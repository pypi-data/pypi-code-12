'''WasPosted mapping for SQLAlchemy'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

MYBASE = declarative_base()

class WasPosted(MYBASE):
    '''WasPosted mapping for SQLAlchemy'''
    __tablename__ = 'wasposted'
    twid = Column(Integer, primary_key=True)
    tweet = Column(String, unique=True)
    tweetimage = Column(String, unique=False)
    lastinsertid = Column(Integer)
    lastcircled = Column(Boolean, default=False)
