import sys
import os
import logging.config
import logging
import sqlalchemy as sql
from sqlalchemy import exc
import pandas as pd
import config

# Logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def get_engine_string():
    """
    Get the engine string for the database connection.
    Args:
        None
    Return:
        engine_string (str): sqlalchemy string for the connection. Can be RDS or local depending on inputs in config.py
    """
    engine_string = config.SQLALCHEMY_DATABASE_URI
    logging.debug("engine string: %s" % engine_string)
    return engine_string


def get_engine(engine_string=None):
    """
    Creates sqlalchemy engine
    Args:
        engine_string (str): sqlalchemy string for the connection
    Returns:
        engine (sqlalchemy.engine.base.Engine): sqlalchemy engine for database of interest
    """
    if engine_string is None:
        if config.HOST is not None:
            logger.debug("RDS is being used")
        else:
            logger.debug("Local DB is being used")

        engine_string = get_engine_string()
        engine = sql.create_engine(engine_string)

    else:
        engine = sql.create_engine(engine_string)

    return engine


def add_to_database(df, table_name, if_exists_condition, engine_string=None):
    """
    Adds data from a pandas DataFrame to a local or RDS MySQL database
    Args:
        df (pandas DataFrame): DataFrame containing data to be added into the database of interest
        table_name (str): Name of the table the data should be added to
        if_exists_condition (str): Argument to determine what should be done if data already exists in the table
        engine_string (str): sqlalchemy string for connection to desired database (optional input)
    Returns:
        None -- adds data to a MySQL database
    """
    engine = get_engine(engine_string)

    try:
        df.to_sql(table_name, engine, if_exists=if_exists_condition, index=False)
        logger.debug("Data inserted into %s", table_name)
    except exc.IntegrityError:
        logger.error("There is an issue with duplication from your request. "
                     "Try using 'append' as the argument for the if_exists_condition")
        sys.exit(1)
    except exc.OperationalError:
        logger.error("Unable to connect to the database. "
                     "Verify the connection info provided (in the config file) is accurate. "
                     "Also verify you have write access to this database.")
        sys.exit(1)
    except exc.TimeoutError:
        logger.error("Timeout issue with trying to read from the database. Please try again later")
        sys.exit(1)
    except exc.SQLAlchemyError as error:
        logger.error("Unexpected error with the SQLAlchemy: %s:%s", type(error).__name__, error)
        sys.exit(1)


def get_data_from_database(query, engine_string=None):
    """
    Retrieve data from a MySQL database on local machine or RDS
    Args:
        query (str): single string representing the query of interest
        engine_string (str): sqlalchemy string for connection to desired database (optional input)
    Returns:
        df (pandas DataFrame): DataFrame containing results from input query
    """

    if engine_string is None:
        engine_string = get_engine_string()
        engine = sql.create_engine(engine_string)
    else:
        engine = sql.create_engine(engine_string)
    try:
        df = pd.read_sql(query, con=engine)
        logger.debug("Data successfully retrieved")
    except exc.OperationalError:
        logger.error("Unable to connect to the database. "
                     "Verify the connection info provided (in the config file) is accurate. "
                     "Also verify you had read access to this database")
        sys.exit(1)
    except exc.TimeoutError:
        logger.error("Timeout issue with trying to read from the database. Please try again later")
        sys.exit(1)
    except exc.SQLAlchemyError as error:
        logger.error("Unexpected error with the SQLAlchemy: %s:%s", type(error).__name__, error)
        sys.exit(1)

    return df
