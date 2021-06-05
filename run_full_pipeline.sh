#!/usr/bin/env bash

# Create database
python3 src/create_db.py

# Acquire data from internet
python3 src/data_acquisition.py

# Process data for modeling
python3 src/data_processing.py

# Train model and obtain results
python3 src/model_run.py
