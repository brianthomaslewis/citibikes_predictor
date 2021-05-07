# MSiA423 Template Repository

**Project Owner: Brian Lewis**

**QA Partner: Michael Faulkner**


<!-- toc -->

- [Project Charter](#project-charter)
- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

(TOC will be updated through time)

<!-- tocstop -->

## Project Charter

### Background

Many tourists visiting NYC find bicycling an ideal way to do sightseeing around the city. With over 1,200 miles of bike lanes throughout the city tens of millions of visitors each year, bike-sharing has become a popular way to deal with the ebb and flow of bicycle demand. Most prominent among these is Citi Bike, the official bike-sharing system of NYC. While Citi Bike allows anyone to obtain instant access to _current, real-time_ inventory of bicycles at all stations around the city, it doesn't provide an easy way to predict which stations will have enough inventory for you and anyone you travel with on the days, times, and locations that you're planning your trip to visit the city.

Even for long-time residents seeking to use Citi Bikes as a commuter vehicle, it isn't always clear which stations will have available bicycles. As of yet, no known solution to solve this planning problem currently exists.

### Vision

To allow tourists or residents in NYC the ability to obtain reasonable predictions about Citi Bike availability at specific stations in the future so that they avoid wasting time trying to find a Citi Bike when they need it.

### Mission

To provide an app that will allow the user to input the following:

 * Date (in the past or the future)
 * Time of day
 * Location

And obtain the following:

 * Top 5 closest Citi Bike stations to the location entered
 * Actual average number of available bicycles at each of the top 5 stations at that time interval (if past date in existing data)
 * Predicted average number of available bicycles at each of the top 5 stations at that time interval (if future date not in existing data)

The predictions will be created after testing a variety of methods for performance, but will likely result from using Holt-Winters forecasting methods.

This app will enable long-time residents as well as short-term tourists the ability to make more reliable plans that involve a Citi Bike. This app should allow the user to decrease their risk of making a plan to use a Citi Bike and arrive at a station only to find no bicycles available. This will enable a more pleasant tourist experience in sightseeing around the city, and a more pleasant commuter experience for residents using Citi Bikes to get to and from work.

Citi Bike Stations Data source: [NYC Citi Bike Stations](https://console.cloud.google.com/marketplace/product/city-of-new-york/nyc-citi-bike), publicly hosted by Google BigQuery 

Citi Bike Trips Data source: [NYC Citi Bike Trips](https://s3.amazonaws.com/tripdata/index.html) (2013-2021)


### Success Criteria

Model performance metric:

 * The model will succeed if it can predict the number of available bikes at a given bike station, date, and time of day with a cross-validation R^2 of 0.7. 

Business metrics:

 * Ratio of Citi Bike rental conversion between:
   * Those who only visited the Citi Bike "real-time availability" page
   * Those who visited the Citi Bike "real-time availability" page AND used the app
 * Ratio of similar bike availability levels across all Citi Bike stations (e.g. we expect to see more similar bicycle distribution across all Citi Bike stations resulting from greater use of planning app to arbitrage high-availability locations)


## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```
## Running the app in Docker 

(NOTE: Use of this app and Docker image requires the use of Python 3. 
Versions below Python 3 may produce unforeseen errors and should not be used.)

### 1. Build the image 

The Dockerfile for running the app is in the `app/` folder. To build the image, run from the root of this repository: 

```bash
 docker build -f app/Dockerfile -t citibikes-predictor .
```

This command builds the Docker image, with the name (tag) `citibikes-predictor`. It uses the instructions in `app/Dockerfile` and relies on the files existing in this directory.
 
### 2. Set downloading/uploading credentials and source environmental variables 

Before downloading the raw Citibikes data, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `GOOGLE_APPLICATION_CREDENTIALS` 
should be environmental variables in your current terminal session. They can be specified by the following steps for 
either **repeated use** ***or*** **one-time use**.

*  AWS Credentials (**repeated use**):
    *  Modify `config/.awsconfig` to include your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials 
    *  Run the following code from the root of this repository to source and verify your AWS credentials:
```bash
source config/.awsconfig
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
````

*  AWS Credentials (**one-time use**):
    *  Run the following code from the root of this repository to create and verify your AWS credentials:
```bash
export AWS_ACCESS_KEY_ID     = <Your AWS access key ID>
export AWS_SECRET_ACCESS_KEY = <Your AWS secret access key>

echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```    

*  Google BigQuery Credentials (**repeated use**):
    *  If you have not already, create a Google Cloud service account key (in the form of a .json file) following the instructions here: https://cloud.google.com/docs/authentication/getting-started
    *  Modify `config/.bigqueryconfig` to include the full .json credentials file path as `GOOGLE_APPLICATION_CREDENTIALS`.
    *  Run the following code from the root of this repository to source and verify your Google BigQuery credentials file path:
```bash
source config/.bigqueryconfig
echo $GOOGLE_APPLICATION_CREDENTIALS
```

*  Google BigQuery Credentials (**one-time use**):
    *  If you have not already, create a Google Cloud service account key (in the form of a .json file) following the instructions here: https://cloud.google.com/docs/authentication/getting-started
    *  Run the following code from the root of this repository to create and verify your Google BigQuery credentials file path:
```bash
export GOOGLE_APPLICATION_CREDENTIALS = <file path to Google service account key .json> 
echo $GOOGLE_APPLICATION_CREDENTIALS
```

Once these enviromental variables have been set and implemented, you should be able to run the below Docker commands to 
download and upload the Citi Bikes data.

### 3. Download raw Citi Bikes data and upload to an S3 bucket

In order to acquire the `stations` and `trips` raw data and upload them to an S3 bucket, run the following code from the root of the repository:
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e GOOGLE_APPLICATION_CREDENTIALS citibikes-predictor run.py download_raw_data
```


The `download_raw_data` function also takes the following optional arguments:



```bash
--trips_only   <boolean TRUE/FALSE>
--s3_bucket    <name of bucket on S3>
--s3_directory <name of the directory within the S3 bucket to place data into>
```

If no options are specified, the `stations` and `trips` raw data will be saved to `data/stations.csv` and `data/trips.csv`, 
respectively, within the repository. Those files will be uploaded into the S3 bucket located at `s3://2021-msia423-lewis-brian/raw/stations.csv` 
and `s3://2021-msia423-lewis-brian/raw/trips.csv`, respectively.


If you wish to save the data on another S3 bucket, specifying `--s3_bucket` will allow you to do so.


**By default, `--trips_only` is set to `FALSE`, but if you specify it to `TRUE`, no Google BigQuery credentials are required, 
and you can omit the `-e GOOGLE_APPLICATION_CREDENTIALS` segment from the above `docker run` command, i.e.:*

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY citibikes-predictor run.py download_raw_data
```




### 4. Initialize the database on RDS (or locally)

Before trying to create a database on RDS, you will need to *first log in to Northwestern's VPN*.

Next, we will first need to follow a similar pattern as above for 
setting environmental variables for either **repeated use** ***or*** **one-time use**. 

*  For **repeated use**:
   *  Modify `config/.sqlconfig` to include your `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, 
       and `DATABASE_NAME` variables.
   *  Run the following code from the root of this repository to source and verify your MySQL environmental variables:
```bash
source config/.sqlconfig
echo $MYSQL_USER
echo $MYSQL_PASSWORD
echo $MYSQL_HOST
echo $MYSQL_PORT
echo $DATABASE_NAME
```   

*  For **one-time use**: 
   *  Run the following code from the root of this repository to create and verify your MySQL environmental variables:
```bash
export MYSQL_USER     = <Your MySQL username>
export MYSQL_PASSWORD = <Your MySQL password>
export MYSQL_HOST     = <Your MySQL RDS host>
export MYSQL_PORT     = <Your MySQL port>
export DATABASE_NAME  = <Your MySQL database name>

echo $MYSQL_USER
echo $MYSQL_PASSWORD
echo $MYSQL_HOST
echo $MYSQL_PORT
echo $DATABASE_NAME
```

Once these variables have been set, they can be passed in to the Docker image with the `create_db` function to create the
database as shown in the code here:

```bash
docker run -e MYSQL_HOST -e MYSQL_PORT -e MYSQL_USER -e MYSQL_PASSWORD -e DATABASE_NAME citibikes-predictor run.py create_db
```

Alternatively, the database can be placed in a different location than RDS by specifying the `--engine_string` argument:

```bash
docker run citibikes-predictor run.py create_db --engine_string=<database path>
```

Or, if you would like only to create a local database created at the default path `sqlite:///data/msia423_db.db`, you can
run the following code which omits all environmental variables:

```bash
docker run citibikes-predictor run.py create_db
```