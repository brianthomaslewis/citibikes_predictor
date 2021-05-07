import logging
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import src.config as config

logging.config.fileConfig(fname=config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


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
        capacity = Column(Integer, unique=False, nullable=True)
        num_bikes = Column(Integer, unique=False, nullable=True)
        last_reported = Column(DateTime, unique=False, nullable=True)

        def __repr__(self):
            return '<Stations %r>' % self.title

    class trips(Base):
        """Create a data model for the database to be set up for bike trips """
        __tablename__ = 'trips'
        station_id = Column(Integer, primary_key=True)
        date = Column(DateTime, unique=False, nullable=True)
        hour = Column(Integer, unique=False, nullable=True)
        inflows = Column(Integer, unique=False, nullable=True)
        outflows = Column(Integer, unique=False, nullable=True)

        def __repr__(self):
            return '<Trips %r>' % self.title

<<<<<<< HEAD
    logger.info("Creating databases using {}.".format(engine_string))
    Base.metadata.create_all(engine)
=======
    Base.metadata.create_all(engine)
>>>>>>> 4a2bd48ceb1f24c561cb1a9fa927319bb97db7e8
