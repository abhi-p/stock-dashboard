import boto3
from botocore.config import Config
import streamlit as st

# Initialize a session using your credentials



API_KEY_FLAT_ID = st.secrets["polygon_aws_access_key_id"]
API_KEY_FLAT_ACCESS_KEY = st.secrets["aws_secret_access_key"]
session = boto3.Session(
  aws_access_key_id=API_KEY_FLAT_ID,
  aws_secret_access_key=API_KEY_FLAT_ACCESS_KEY,
)

# Create a client with your session and specify the endpoint
s3 = session.client(
  's3',
  endpoint_url='https://files.polygon.io',
  config=Config(signature_version='s3v4'),
)

# List Example
# Initialize a paginator for listing objects
paginator = s3.get_paginator('list_objects_v2')

# Choose the appropriate prefix depending on the data you need:
# - 'global_crypto' for global cryptocurrency data
# - 'global_forex' for global forex data
# - 'us_indices' for US indices data
# - 'us_options_opra' for US options (OPRA) data
# - 'us_stocks_sip' for US stocks (SIP) data
prefix = 'us_stocks_sip'  # Example: Change this prefix to match your data need
bucket_name = 'flatfiles'

# List objects using the selected prefix
for page in paginator.paginate(Bucket='flatfiles', Prefix=prefix):
  for obj in page['Contents']:
    if  'us_stocks_sip/day_aggs_v1/2025/05/' in obj['Key'] or 'us_stocks_sip/day_aggs_v1/2025/06/' in obj['Key'] or 'us_stocks_sip/day_aggs_v1/2025/04/' in obj['Key']:
      print("hello",obj['Key'])
      local_file_name = obj['Key'].split('/')[-1]

      local_file_path = './historical_data/' + local_file_name

      s3.download_file(bucket_name, obj['Key'], local_file_path)

      #  k=1
# Copy example
# print("done view")
# # Specify the bucket name

# # Specify the S3 object key name
# object_key = 'us_stocks_sip/minute_aggs_v1/2025/02/2025-02-21.csv.gz'

# files =['us_stocks_sip/day_aggs_v1/2025/05/','us_stocks_sip/day_aggs_v1/2025/06/','us_stocks_sip/day_aggs_v1/2025/04/'] 
# # Specify the local file name and path to save the downloaded file
# # This splits the object_key string by '/' and takes the last segment as the file name


# local_file_name = object_key.split('/')[-1]

# # This constructs the full local file path
# local_file_path = './historical_data/' + local_file_name

# # Download the file
# s3.download_file(bucket_name, object_key, local_file_path)