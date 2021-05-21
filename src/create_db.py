import logging
import sqlalchemy
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import src.config as config

logging.config.fileConfig(fname=config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Stations(Base):
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
        return "<Stations(station_id='%r', name='%r', latitude='%r', longitude='%r', capacity='%r', num_bikes='%r', " \
               "last_reported='%r')>" % (self.station_id, self.name, self.latitude, self.longitude, self.capacity,
                                         self.num_bikes, self.last_reported)


class Trips(Base):
    """Create a data model for the database to be set up for bike trips """
    __tablename__ = 'trips'
    station_id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=False, nullable=True)
    hour = Column(Integer, unique=False, nullable=True)
    inflows = Column(Integer, unique=False, nullable=True)
    outflows = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return "<Trips(station_id='%r', date='%r', hour='%r', inflows='%r', outflows='%r')>" % \
               (self.station_id, self.date, self.hour, self.inflows, self.outflows)


def create_db(engine_string=config.SQLALCHEMY_DATABASE_URI):
    """
    Creates database with data models inherited from Base and places raw data into databases.
    Database configuration will depend on environment variables passed, and logic is in config.py

    Args:
        engine_string: String giving the connection details to the listed database
    Returns: none (database created with data models).
    """

    # Create db at specified engine string
    try:
        logger.info("Attempting to initializing database on {}".format(engine_string))
        engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Success! Database tables have been created at %s", engine_string)

    except pymysql.err.OperationalError as e:
        logger.error(e)
        logger.error("Could not connect to the specified MySQL server. "
                     "Verify your connection is on the Northwestern VPN before retrying.")
        sys.exit(1)
