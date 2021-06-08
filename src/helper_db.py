"""Helper module to connect with databases."""
import sys
import logging.config
import logging
import sqlalchemy as sql
from sqlalchemy import exc
import src.config as config

# Logging
logger = logging.getLogger(__name__)


def get_engine_string():
    """
    Get the engine string for the database connection.
    Args:
        None
    Return:
        engine_string (str): sqlalchemy string for the connection.
        Can be RDS or local depending on inputs in config.py
    """
    # Obtain engine string from SQLALCHEMY_DATABASE_URI
    engine_string = config.SQLALCHEMY_DATABASE_URI
    logging.debug("engine string: %s", engine_string)
    return engine_string


def get_engine(engine_string=None):
    """
    Creates sqlalchemy engine
    Args:
        engine_string (str): sqlalchemy string for the connection
    Returns:
        engine (sqlalchemy.engine.base.Engine): sqlalchemy engine for database of interest
    """
    # Deduce whether RDS or Local DB is being used
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


def add_to_database(dataframe, table_name, if_exists_condition, engine_string=None):
    """
    Adds data from a pandas DataFrame to a local or RDS MySQL database
    Args:
        dataframe (pandas DataFrame): DataFrame containing data to be added
            into the database of interest
        table_name (str): Name of the table the data should be added to
        if_exists_condition (str): Argument to determine what should be
            done if data already exists in the table
        engine_string (str): sqlalchemy string for connection to desired
            database (optional input)
    Returns:
        None -- adds data to a MySQL database
    """
    engine = get_engine(engine_string)

    try:
        dataframe.to_sql(table_name, engine, if_exists=if_exists_condition, index=False)
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
        logger.error("Timeout issue with trying to read from the database. "
                     "Please try again later")
        sys.exit(1)
    except exc.SQLAlchemyError as error:
        logger.error("Unexpected error with the SQLAlchemy: %s:%s", type(error).__name__, error)
        sys.exit(1)
