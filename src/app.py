#!/usr/bin/env python3

# INFO
# - Author: Augusto Cardoso
# - E-mail: acardoso.ti@gmail.com
# - Github: github.com/aleroxac

# REFERENCES
# - https://docs.python.org/pt-br/3/howto/logging.html
# - https://www.elastic.co/guide/en/kibana/current/saved-objects-api-export.html
# - https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
# - https://cloud.google.com/storage/docs/reference/libraries#client-libraries-usage-python
# - https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
# - https://medium.com/@dmitriyvi/back-up-kibana-settings-to-s3-with-python-and-aws-lambda-21aa66a04e66



import os
import sys
import json
import boto3
import logging
import datetime
import requests
import dateutil.tz
from google.cloud import storage



## ---------- VARIABLES ---------- ##
ERROR = "Error: %s\n"
KIBANA_URL = f"https://{os.getenv('KIBANA_HOST')}:{os.getenv('KIBANA_PORT')}"
KIBANA_USERNAME = os.getenv('ELASTIC_USERNAME')
KIBANA_PASSWORD = os.getenv('ELASTIC_PASSWORD')



## ---------- FUNCTIONS ---------- ##
def logger(logger, level, message):
    '''Log all messages in console.'''

    # create logger
    logger = logging.getLogger(logger)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # logging by message level
    if level == 'error':
        logger.error(message)
    elif level == 'debug':
        logger.debug(message)
    else:
        logger.info(message)

def get_kibana_savedobjects(config):
    '''Make a POST request to get response with Kibana Saved Objects.'''
    kibana_url = config['kibana']["url"] + config['kibana']['endpoint']
    kibana_username = config['kibana']["username"]
    kibana_password = config['kibana']["password"]
    kibana_headers = config['kibana']["headers"]
    kibana_payload = json.dumps(config['kibana']["payload"])

    logger("get_kibana_savedobjects","info", "Getting Kibana Saved Objects")
    try:
        response = None
        response = requests.post(kibana_url, headers=kibana_headers, data=kibana_payload, timeout=30, auth=(kibana_username, kibana_password)).text
    except Exception as e:
        logger("get_kibana_savedobjects", "error", ERROR % str(e))
        sys.exit(1)
    return response

def set_timezone(time_zone):
    '''Set timezone timezone according to the region informed.'''
    sys_timezone = dateutil.tz.gettz(time_zone)
    date_string = datetime.datetime.now(sys_timezone).strftime("%Y-%m-%dT%H-%M-%S")
    return date_string

def save_response_on_s3_bucket(config):
    '''Get Kibana API response from get_kibana_savedobjects function and save into s3 bucket file'''
    response = get_kibana_savedobjects(config)
    date_string = set_timezone(config['time_zone'])
    s3_filename = ("kibana_saved_objects_%s.ndjson" % date_string)
    s3_bucket = config['bucket']

    logger("save_response_on_s3_bucket","info","Storing response in s3://%s/%s" % (s3_bucket, s3_filename))
    try:
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(Bucket=s3_bucket, Key=s3_filename, Body=bytes(response, encoding='utf-8'), ContentType='application/x-ndjson')
    except Exception as e:
        logger("save_response_on_s3_bucket", "error", ERROR % str(e))
        sys.exit(1)

def save_response_on_gcs_bucket(config):
    '''Get Kibana API response from get_kibanaSavedObjects function and save into s3 bucket file'''
    response = get_kibana_savedobjects(config)
    date_string = set_timezone(config['time_zone'])
    gcs_filename = ("kibana_saved_objects_%s.ndjson" % date_string)
    gcs_bucket = config['bucket']

    logger("save_response_on_gcs_bucket","info","Storing response in gcs://%s/%s" % (gcs_bucket, gcs_filename))
    try:
        storage.Client().bucket(gcs_bucket).blob(gcs_filename).upload_from_string(response, content_type='application/x-ndjson')
    except Exception as e:
        logger("save_response_on_gcs_bucket", "error", ERROR % str(e))
        sys.exit(1)

def read_config():
    '''Read configuration file'''
    logger("read_config","info","Reading configuration file")
    try:
        config = json.loads(open("config.json", "r").read())
        config["kibana"]["url"] = KIBANA_URL
        config["kibana"]["username"] = KIBANA_USERNAME
        config["kibana"]["password"] = KIBANA_PASSWORD
    except Exception as e:
        logger("read_config", "error", ERROR % str(e))
        sys.exit(1)
    return config


## ---------- MAIN ---------- ##
if __name__ == "__main__":
    '''Start the kibana savedobjects backup generation flow'''
    logger("main","info","Start flow to build kibana savedobjects backup")
    try:
        config = read_config()
        if config['cloud_provider'] == 'gcp':
            save_response_on_gcs_bucket(config)
        else:
            save_response_on_s3_bucket(config)
    except Exception as e:
        logger("main", "error", ERROR % str(e))
        sys.exit(1)