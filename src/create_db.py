import logging
import argparse
import sqlalchemy
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import helper_db
import config as connection_config

logger = logging.getLogger(__name__)

Base = declarative_base()


class Bike_Stock(Base):
    """Create a data model for the database to be set up for bike stock data """
    __tablename__ = 'bike_stock'
    station_id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=False, nullable=True)
    hour = Column(Integer, unique=False, nullable=True)
    name = Column(String(200), unique=True, nullable=True)
    latitude = Column(String(100), unique=False, nullable=False)
    longitude = Column(String(100), unique=False, nullable=False)
    stock = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return "<Bike_Stock(station_id='%r', date='%r', hour='%r', name='%r', latitude='%r', longitude='%r', " \
               "stock='%r')>" % (self.station_id, self.date, self.hour, self.name, self.latitude,
                                 self.longitude, self.stock)


class Predictions(Base):
    """Create a data model for the database to be set up for final predictions data """
    __tablename__ = 'predictions'
    station_id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=True)
    latitude = Column(String(100), unique=False, nullable=False)
    longitude = Column(String(100), unique=False, nullable=False)
    date = Column(String(100), unique=False, nullable=True)
    hour = Column(Integer, unique=False, nullable=True)
    pred_num_bikes = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        return "<Bike_Stock(station_id='%r', date='%r', hour='%r', pred_num_bikes='%r')>" % \
               (self.station_id, self.date, self.hour, self.pred_num_bikes)


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


class BikeManager:

    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sqlalchemy.create_engine(args.engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def close(self) -> None:
        """Closes session
        Returns: None
        """
        self.session.close()


def create_db(args):
    """
    Creates database with data models inherited from Base and places raw data into databases.
    Database configuration will depend on environment variables passed

    Args:
        args: From argparse:
            engine_string: String giving the connection details to the listed database

    Returns: none (database created with data models)
    """

    # Create db at specified engine string
    engine = helper_db.get_engine(args.engine_string)
    try:
        logger.info("Attempting to initialize database on %s", args.engine_string)
        Base.metadata.create_all(engine)
        logger.info("Success! Database tables have been created at %s", args.engine_string)

    except pymysql.err.OperationalError as e:
        logger.error(e)
        logger.error("Could not connect to the specified MySQL server. "
                     "Verify your connection is on the Northwestern VPN before retrying.")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create tables citibike-predictor database")
    parser.add_argument("--engine_string", default=connection_config.SQLALCHEMY_DATABASE_URI,
                        help="Optional engine string for sqlalchemy")
    args = parser.parse_args()
    create_db(args)
