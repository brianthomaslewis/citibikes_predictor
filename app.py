import os
import traceback
import logging.config
from flask import Flask
from flask_wtf import FlaskForm
from wtforms.fields import SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask import render_template, request, redirect, url_for
from src.create_db import Predictions, BikeManager

# Set up secret key
SECRET_KEY = os.urandom(32)

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
bike_manager = BikeManager(app)

# Create forms for webpage

class Form(FlaskForm):
    stations = SelectField('stations', choices=[])
    dates = SelectField('dates', choices=[])
    hours = SelectField('hours', choices=[])


@app.route('/', methods=['GET', 'POST'])
def selection():
    """View that lists stations in dropdown.

    Creates selection for response page that uses data queried from predictions database.

    Returns: rendered html template

    """
    try:
        form = Form(meta={'crsf': False})
        form.stations.choices = [i[0] for i in bike_manager.session.query(Predictions.name).distinct()]
        form.dates.choices = [i[0] for i in bike_manager.session.query(Predictions.date).distinct().filter(
            Predictions.date > '2021-06-06')]
        form.hours.choices = [i[0] for i in bike_manager.session.query(Predictions.hour).distinct()]
        logger.debug("Selection page accessed")

        if request.method == 'POST':
            station = form.data['stations']
            date = form.data['dates']
            hour = form.data['hours']
            results = [i[0] for i in bike_manager.session.query(Predictions.pred_num_bikes). \
                        filter_by(name=station, date=date, hour=hour).all()][0]
            # return '<h1>{}, {}, {}, {} <h1> '.format(station, date, hour, results)
            return render_template('response.html', station=station, date=date, hour=hour, results=results)

        return render_template('selection.html', form=form)

    except:
        traceback.print_exc()
        logger.warning("Not able to display selection, error page returned")
        return render_template('error.html')


if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
