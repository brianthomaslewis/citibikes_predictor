import logging
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import src.config as config


def create_db(engine_string=config.SQLALCHEMY_DATABASE_URI):
    """
    Creates database with data models inherited from Base and places raw data into databases.
    Database configuration will depend on environment variables passed, and logic is in config.py

    Returns: database created with data models.
    """
    Base = declarative_base()
    engine = sqlalchemy.create_engine(engine_string)  # set up sqlite connection

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
            return '<Stations %r>' % self.title

    Base.metadata.create_all(engine)