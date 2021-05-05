import logging
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData, DateTime
from config.flaskconfig import SQLALCHEMY_DATABASE_URI


def create_db(SQLALCHEMY_DATABASE_URI):

    Base = declarative_base()

    class stations(Base):
        """Create a data model for the database to be set up for bike stations """
        __tablename__ = 'stations'
        station_id = Column(Integer, primary_key=True)
        name = Column(String(200), unique=True, nullable=True)
        latitude = Column(String(100), unique=False, nullable=False)
        longitude = Column(String(100), unique=False, nullable=False)
        capacity = Column(Integer)
        num_bikes = Column(Integer)
        last_reported = Column(DateTime)

        def __repr__(self):
            return '<Station %r>' % self.title

    # set up sqlite connection
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    # create the tracks table
    Base.metadata.create_all(engine)