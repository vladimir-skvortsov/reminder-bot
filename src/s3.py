import os
import boto3
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
aws_bucket = os.getenv('AWS_BUCKET')

client = boto3.client(
  's3',
  aws_access_key_id=aws_access_key,
  aws_secret_access_key=aws_secret_key,
)
