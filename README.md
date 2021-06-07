# Citi Bikes Predictor App

**Project Owner: Brian Lewis**

**QA Partner: Michael Faulkner**


<!-- toc -->

- [Project Charter](#project-charter)
- [Directory structure](#directory-structure)
- [Running the model pipeline in Docker](#running-the-model-pipeline-in-Docker)
  * [1. Connect to Northwestern VPN](#1-connect-to-northwestern-vpn)
  * [2. Configure Resources in Docker](#2-configure-resources-in-docker)
  * [3. Set AWS credentials and source required environmental variables](#3-set-aws-credentials-and-source-required-environmental-variables)
  * [4. Build the Pipeline Docker Image](#4-build-the-pipeline-docker-image)
  * [5. Run the model pipeline in Docker](#5-run-the-model-pipeline-in-docker)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Connect to Northwestern VPN](#1-connect-to-northwestern-vpn)
  * [2. Configure Flask App](#2-configure-flask-app)
  * [3. Build the Image](#3-build-the-image)
  * [4. Run the Container](#4-run-the-container)
  * [5. Killing the Container](#5-killing-the-container)

<!-- tocstop -->

## Project Charter

### Background

Many tourists visiting NYC find bicycling an ideal way to do sightseeing around the city. With over 1,200 miles of bike lanes throughout the city tens of millions of visitors each year, bike-sharing has become a popular way to deal with the ebb and flow of bicycle demand. Most prominent among these is Citi Bike, the official bike-sharing system of NYC. While Citi Bike allows anyone to obtain instant access to _current, real-time_ inventory of bicycles at all stations around the city, it doesn't provide an easy way to predict which stations will have enough inventory for you and anyone you travel with on the days, times, and locations that you're planning your trip to visit the city.

Even for long-time residents seeking to use Citi Bikes as a commuter vehicle, it isn't always clear which stations will have available bicycles. As of yet, no known solution to solve this planning problem currently exists.

### Vision

To allow tourists or residents in NYC the ability to obtain reasonable predictions about Citi Bike availability at specific stations in the future so that they avoid wasting time trying to find a Citi Bike when they need it.

### Mission

To provide an app that will allow the user select from the following:

 - Citi Bike Station Name
 - Date
 - Hour of the Day

And obtain the following:

 - Predicted average number of available bicycles at each of the top 5 stations at that time interval (if future date not in existing data)

The predictions will be created after testing a variety of methods for performance, but will likely result from using Holt-Winters or ARIMA forecasting methods.

This app will enable long-time residents as well as short-term tourists the ability to make more reliable plans that involve a Citi Bike. This app should allow the user to decrease their risk of making a plan to use a Citi Bike and arrive at a station only to find no bicycles available. This will enable a more pleasant tourist experience in sightseeing around the city, and a more pleasant commuter experience for residents using Citi Bikes to get to and from work.

Citi Bike Stations Data source: [NYC Citi Bike Stations](https://feeds.citibikenyc.com/stations/stations.json)

Citi Bike Trips Data source: [NYC Citi Bike Trips](https://s3.amazonaws.com/tripdata/index.html) (2013-2021)


### Success Criteria

Model performance metric:

 - The model will succeed if it can predict the number of available bikes at a given bike station, date, and time of day with a MAPE of <= 15%. 

Business metrics:

 - Ratio of Citi Bike rental conversion between:
   - Those who only visited the Citi Bike "real-time availability" page
   - Those who visited the Citi Bike "real-time availability" page AND used the app
 - Ratio of similar bike availability levels across all Citi Bike stations (e.g. we expect to see more similar bicycle distribution across all Citi Bike stations resulting from greater use of planning app to arbitrage high-availability locations)


## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── Dockerfile_App                <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── .awsconfig                    <- Blank configurable file for sourcing AWS credentials 
│   ├── .sqlconfig                    <- Blank configurable file for sourcing MySQL variables 
│   ├── config.yaml                   <- Configurations YAML file for model pipeline 
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── notebooks/
│   ├── deliver/                      <- Notebooks shared with others / in final state
│
├── reference/                        <- Reference material relevant to the project
│
├── src/                              <- Source scripts for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── Dockerfile_Bash                   <- Dockerfile for building and running model before launching app
├── run_full_pipeline.sh              <- Shell script for running acquisition, processing, and modeling pipeline
├── requirements.txt                  <- Python package dependencies 

```
## Running the model pipeline in Docker
(NOTE: Use of this all Docker images require the use of Python 3.6 or higher. 
Versions below Python 3.6 may produce unforeseen errors and should not be used.)

### 1. Connect to Northwestern VPN
Before completing any other steps, please first connect to the Northwestern VPN. Without a connection to the Northwestern VPN, 
other steps in the pipeline process may not work as designed.

### 2. Configure Resources in Docker
Due to the nature of the model and the size of the data involved, running this pipeline succesfully
will require increasing the resources in Docker beyond their default setting. Please follow these steps in order to configure Docker properly:

- Open up Docker Dashboard
- Click the 'gear' icon
- Click "Resources"
  - Toggle "CPUs" = 5
  - Toggle "Memory" = 6.00 GB
  - Toggle "Swap" = 1 GB  
    
### 3. Set AWS credentials and source required environmental variables 

Before downloading the raw Citibikes data, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `SQLALCHEMY_DATABASE_URI` and 
`S3_BUCKET` should be environmental variables in your current terminal session. 
They can be specified by the following steps (for either **repeated use** or **one-time use**).

-  AWS Credentials (**repeated use**):
    -  Modify `config/.awsconfig` to include your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials 
    -  Run the following code from the root of this repository to source and verify your AWS credentials:
```bash
source config/.awsconfig
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
````

-  AWS Credentials (**one-time use**):
    -  Run the following code from the root of this repository to create and verify your AWS credentials:
```bash
export AWS_ACCESS_KEY_ID     = <Your AWS access key ID>
export AWS_SECRET_ACCESS_KEY = <Your AWS secret access key>

echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

-  Remote SQLAlchemy Database URI (For **repeated use**):
   -  Modify `config/.sqlconfig` to include your `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, 
       and `MYSQL_DATABASE` variables.
   -  Run the following code from the root of this repository to source and verify your MySQL environmental variables:
```bash
source config/.sqlconfig

echo $MYSQL_USER
echo $MYSQL_PASSWORD
echo $MYSQL_HOST
echo $MYSQL_PORT
echo $MYSQL_DATABASE

export SQLALCHEMY_DATABASE_URI='mysql+pymysql://'$MYSQL_USER':'$MYSQL_PASSWORD'@'$MYSQL_HOST':'$MYSQL_PORT'/'$MYSQL_DATABASE
echo $SQLALCHEMY_DATABASE_URI
```   

-  Remote SQLAlchemy Database URI (For **one-time use**): 
   -  Run the following code from the root of this repository to create and verify your MySQL environmental variables:
```bash
export MYSQL_USER     =<Your MySQL username>
export MYSQL_PASSWORD =<Your MySQL password>
export MYSQL_HOST     =<Your MySQL RDS host>
export MYSQL_PORT     =<Your MySQL port>
export MYSQL_DATABASE =<Your MySQL database name>

echo $MYSQL_USER
echo $MYSQL_PASSWORD
echo $MYSQL_HOST
echo $MYSQL_PORT
echo $MYSQL_DATABASE

export SQLALCHEMY_DATABASE_URI='mysql+pymysql://'$MYSQL_USER':'$MYSQL_PASSWORD'@'$MYSQL_HOST':'$MYSQL_PORT'/'$MYSQL_DATABASE
echo $SQLALCHEMY_DATABASE_URI
 
```

- S3 Bucket (**one-time use**):
    -  Run the following code from the root of this repository to create and verify your selected S3 bucket:
```bash
export S3_BUCKET=<The name of the S3 bucket you want to use during the model pipeline>

echo $S3_BUCKET
```    

Once these enviromental variables have been set and implemented, you should be able to run the below Docker commands to 
download, upload, process, and model the Citi Bikes data.

### 4. Build the pipeline Docker image 

The Dockerfile for running the pipeline is in the root of this directory. To build the image, 
run from the root of this repository: 

```bash
 docker build -f Dockerfile_Bash -t citibikes-predictor-bash .
```

This command builds the Docker image, with the name (tag) `citibikes-predictor-bash`. 
It uses the instructions in `Dockerfile_Bash` and relies on the files existing in this directory.
 

### 5. Run the model pipeline in Docker

In order to run the full pipeline from downloading to modeling, run the following code from the root of the repository:

**NOTE**: Due to the size of the raw data, necessary data processing, and memory requirements needed to complete the 
modeling process, expect this next command to run for about 10-15 minutes. If after running this code for several
minutes, you receive a nondescript `Killed` message, please return to Step 2 above and increase your Docker Dashboard "Resources" configurations. 
```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET -e SQLALCHEMY_DATABASE_URI citibikes-predictor-bash run_full_pipeline.sh
```

- If no `S3_BUCKET` environmental variable is defined, the files will be uploaded into 
the S3 bucket located at `s3://2021-msia423-lewis-brian/data/`.

If you would like only to create a local database created at the default path `sqlite:///data/msia423_db.db`, you can
run the following code which removes the `MYSQL_*` environmental variables and omits using the `SQLALCHEMY_DATABASE_URI` variable:

```bash
unset MYSQL_USER
unset MYSQL_PASSWORD
unset MYSQL_HOST
unset MYSQL_PORT
unset MYSQL_DATABASE

docker run --mount type=bind,source="$(pwd)"/data,target=/src/data  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET citibikes-predictor-bash run_full_pipeline.sh
```

You can also create a local/remote database at another location by defining a database path manually and running the command as follows:

```bash
export SQLALCHEMY_DATABASE_URI=<your preferred engine string>

docker run --mount type=bind,source="$(pwd)"/data,target=/src/data  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET -e SQLALCHEMY_DATABASE_URI citibikes-predictor-bash run_full_pipeline.sh
```

## Running the app in Docker
(NOTE: Use of this all Docker images require the use of Python 3.6 or higher. 
Versions below Python 3.6 may produce unforeseen errors and should not be used.)

### 1. Connect to Northwestern VPN (if not already done previously)
If you haven't already, [connect to Northwestern VPN](#1-connect-to-northwestern-vpn).

### 2. Configure Flask App
`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations.
**Please check for yourself to see if these are what you'd like to use. If so, proceed.**

```python
DEBUG = False   
LOGGING_CONFIG = "config/logging/local.conf"
HOST = "0.0.0.0" # the host that is running the app; 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile_App 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/msia423_db.db'  # URI (engine string) for database that contains predictions
APP_NAME = "citibikes-predictor"
SQLALCHEMY_ECHO = False
```

### 3. Build the Image

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run the following
commands from the root of this directory:

```bash
docker build -f app/Dockerfile_App -t citibikes-predictor .
```

This command builds the Docker image, with the tag `citibikes-predictor`, based on the instructions in 
app/Dockerfile_App, and the files existing in this directory.

### 4. Run the Container

If you created the database locally in `data/msia423_db.db`, you can run this container locally
by executing the following command from this directory:

```bash
docker run -p 5000:5000 --name citibike citibikes-predictor
```

If you created the database elsewhere (like an RDS instance) but would still like to run the app, you can run this container in your terminal
by executing the following command from this directory:

```bash
docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 --name citibike citibikes-predictor
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

### 5. Killing the Container

If you are done using the app, you can kill the container running the app with the following command:

```bash
docker kill citibike
```

# Testing

Tests have been developed for all the modules listed above and reside in `tests/`. To run these tests:

*  Navigate to the root of this repository in a terminal
*  Execute the following code:

```bash
 docker run citibikes-predictor -m pytest test/
```