import argparse
import logging
import os
import re
import pandas as pd
import boto3
import botocore


def parse_s3(s3path):
    """Parses the inputted S3 path to output the s3 bucket and s3 "pure" path """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_to_s3(local_path, s3path):
    """Parses the inputted S3 path to output the s3 bucket and s3 "pure" path """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)
    bucket.upload_file(local_path, s3_just_path)
