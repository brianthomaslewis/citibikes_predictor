# Citi Bikes Predictor App

**Project Owner: Brian Lewis**

**QA Partner: Michael Faulkner**


<!-- toc -->

- [Project Charter](#project-charter)
- [Directory structure](#directory-structure)
- [Environment setup before running commands in Docker](#environment-setup-before-running-commands-in-docker)
  * [1. Connect to Northwestern VPN](#1-connect-to-northwestern-vpn)
  * [2. Configure Resources in Docker](#2-configure-resources-in-docker)
  * [3. Set AWS credentials and source required environmental variables](#3-set-aws-credentials-and-source-required-environmental-variables)
- [Running the data acquisition and model pipelines in Docker](#running-the-data-acquisition-and-model-pipelines-in-docker)
  * [1. Build the data acquisition and model pipeline image in Docker](#1-build-the-data-acquisition-and-model-pipeline-image-in-docker)
  * [2. Run the data acquisition in Docker](#2-run-the-data-acquisition-in-docker)  
  * [3. Run the model pipeline in Docker](#3-run-the-model-pipeline-in-docker)
  * [4. A note on environmental variables in the above Docker commands](#4-a-note-on-environmental-variables-in-the-above-docker-commands)
- [Running the web app in Docker](#running-the-web-app-in-docker)
  * [1. Connect to Northwestern VPN](#1-connect-to-northwestern-vpn-if-not-already-done-previously)
  * [2. Configure Flask App](#2-configure-flask-app)
  * [3. Build the web app image](#3-build-the-web-app-image)
  * [4. Run the web app container](#4-run-the-web-app-container)
  * [5. Kill the named web app container](#5-kill-the-named-web-app-container)
- [Testing](#testing)    

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
│   ├── sample/                       <- Sample data used for testing
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── notebooks/                        <- Notebooks used in the process of understanding and working with data
│
├── reference/                        <- Reference material relevant to the project
│
├── src/                              <- Source scripts for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run_acquisition.py                <- Python wrapper for running the data acquisition pipeline 
├── run_modeling.py                   <- Python wrapper for running the modeling pipeline 
├── Dockerfile_Bash                   <- Dockerfile for building and running full pipeline before launching app
├── run_data_acquisition.sh           <- Shell script to run data acquisition pipeline
├── run_model.sh                      <- Shell script to run modeling pipeline 
├── run_tests.sh                      <- Shell script to run pytest tests on /test directory
├── requirements.txt                  <- Python package dependencies 

```

## Environment setup before running commands in Docker

### 1. Connect to Northwestern VPN
Before completing any other steps, please first connect to the Northwestern VPN. Without a connection to the Northwestern VPN, 
other steps in the pipeline process may not work as designed.

### 2. Configure resources in Docker
Due to the nature of the model and the size of the data involved, running this pipeline succesfully
will require increasing the resources in Docker beyond their default setting. Please follow these steps in order to configure Docker properly:

- Open up Docker Dashboard
- Click the 'gear' icon
- Click "Resources"
  - Toggle "CPUs" = 5
  - Toggle "Memory" = 6.00 GB
  - Toggle "Swap" = 1 GB  
    
### 3. Set AWS credentials and source required environmental variables 

Before downloading the raw Citi Bikes data, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `SQLALCHEMY_DATABASE_URI` and 
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

You can also specify a local/remote database at another location (like an RDS instance) by defining a database path 
manually (shown below) and then running the above docker commands:

```bash
export SQLALCHEMY_DATABASE_URI=<your preferred engine string>
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
You can also specify a local/remote database at another location (like an RDS instance) by defining a database path 
manually (shown below) and then running the above docker commands:

```bash
export SQLALCHEMY_DATABASE_URI=<your preferred engine string>
```

- S3 Bucket (**one-time use**):
    -  Run the following code from the root of this repository to create and verify your selected S3 bucket:
```bash
export S3_BUCKET=<The name of the S3 bucket you want to use during the model pipeline>

echo $S3_BUCKET
```    

Once these enviromental variables have been set and implemented, you should be able to run the below Docker commands to 
download, upload, process, and model the Citi Bikes data.

## Running the data acquisition and model pipelines in Docker
(NOTE: Use of this all Docker images require the use of Python 3.6 or higher. 
Versions below Python 3.6 may produce unforeseen errors and should not be used.)

### 1. Build the data acquisition and model pipeline image in Docker

The Dockerfile for running both the data acquisition and model pipeline is in the root of this directory. To build the image, 
run from the root of this repository: 

```bash
 docker build -f Dockerfile_Bash -t citibikes-predictor-bash .
```

This command builds the Docker image, with the name (tag) `citibikes-predictor-bash`. 
It uses the instructions in `Dockerfile_Bash` and relies on the files existing in this directory.

### 2. Run the data acquisition in Docker
**NOTE**: Before proceeding, it is important to know that due to the size of the raw data, necessary data processing, and memory requirements needed to complete the 
acquisition and modeling process, expect the following `docker run` commands to take up to 10-15 minutes to finish executing. If after running this code for several
minutes, you receive a nondescript `Killed` message, please return to [Step 2](#2-configure-resources-in-docker) above and increase your Docker Dashboard "Resources" configurations. 

In order to run the **data acquisition** portion of the image you just built, run the following code from the root of the repository:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET -e SQLALCHEMY_DATABASE_URI citibikes-predictor-bash run_data_acquisition.sh
``` 

### 3. Run the model pipeline in Docker

Similarly, in order to run the **modeling** portion of the image you just built above, run the following code from the root of the repository:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/src/data -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e S3_BUCKET -e SQLALCHEMY_DATABASE_URI citibikes-predictor-bash run_model.sh
```

**WARNING**: The ARIMA model will produce a long stream of output in the console, but this is to be expected. Nothing is going wrong, the model is simply working. 
There may be many lines at the end of the output that say `This problem is unconstrained`.

### 4. A note on environmental variables in the above Docker commands:

- If no `AWS` credential environmental variables are defined, the command will throw an error. If this occurs, please return to [Step 3](#3-set-aws-credentials-and-source-required-environmental-variables) 
  and follow those instructions.
- If no `S3_BUCKET` environmental variable is defined, this value will default to the S3 bucket located at`2021-msia423-lewis-brian`.
- If no `SQLALCHEMY_DATABASE_URI` environmental variable is defined as described in [Step 3](#3-set-aws-credentials-and-source-required-environmental-variables), 
  this value will default to a local database path at `sqlite://data/msia423_db.db` 
  -  Relatedly, if different `SQLALCHEMY_DATABASE_URI` strings are used between these two commands, the `citibikes-predictor-model` image will throw an error. 
     In order for the `citibikes-predictor-model` image to run correctly, it will need access to the same `SQLALCHEMY_DATABASE_URI` provided in the first command.

If you are intentionally trying to **only** create a local database created at the default path `sqlite:///data/msia423_db.db`, you can
run the following code which removes the `MYSQL_*` and `SQLALCHEMY_DATABASE_URI` environmental variables before also omitting the `-e SQLALCHEMY_DATABASE_URI` segment before running either of the docker commands:

```bash
unset MYSQL_USER
unset MYSQL_PASSWORD
unset MYSQL_HOST
unset MYSQL_PORT
unset MYSQL_DATABASE
unset SQLALCHEMY_DATABASE_URI
```

## Running the web app in Docker
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

### 3. Build the web app image

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run the following
commands from the root of this directory:

```bash
docker build -f app/Dockerfile_App -t citibikes-predictor .
```

This command builds the Docker image, with the tag `citibikes-predictor`, based on the instructions in 
app/Dockerfile_App, and the files existing in this directory.

### 4. Run the web app container

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

### 5. Kill the named web app container

If you are done using the app, you can kill the container running the app in a different terminal with the following command:

```bash
docker kill citibike
```

**NOTE**: Once you have run the web app with the name `citibike`, you will not be able to re-run the above `docker run` 
command using that same name. Each run will require a new `--name`.

# Testing

Tests have been developed for all the modules listed above and reside in `test/`. To run these tests:

-  Navigate to the root of this repository in a terminal
-  Ensure you have built the data acquisition and model pipeline image in Docker as described in 
   [Step 4](#4-build-the-data-acquisition-and-model-pipeline-image-in-docker)   
-  Execute the following code, which runs `pytest` within the `run_tests.sh` shell script:

```bash
 docker run citibikes-predictor-bash run_tests.sh
```