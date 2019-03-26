#!/usr/bin/env python
'''
  backup
'''

import argparse
import logging
import os
import sys

import boto3
from boto3.s3.transfer import S3Transfer, TransferConfig

import config

def authenticate():
  """Return the authenticated client"""
  return boto3.client(
    's3',
    aws_access_key_id=config.ACCESS_KEY,
    aws_secret_access_key=config.SECRET_KEY,
    endpoint_url=config.ENDPOINT,
    use_ssl=True,
  )


def main(create_bucket):
  logging.info('starting...')
  client = authenticate()

  if create_bucket:
    client.create_bucket(Bucket=config.BUCKET_NAME)

  config=TransferConfig(
        multipart_threshold=15 * 1024 * 1024,
        max_concurrency=1
  )

  transfer = S3Transfer(client, config)

  for root, dirs, files in os.walk(config.SRC):
    for file in files:
      src = os.path.join(root, file)
      dest = os.path.join(config.DEST, src)
      if os.path.isfile(src):
        logging.info('%s -> %s...', src, dest)
        try:
          transfer.upload_file(src, config.BUCKET_NAME, dest)
        except:
          logging.warn('%s was not copied', src)
        logging.info('%s: done', src)
  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--create_bucket', action='store_true', help='create bucket')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.create_bucket)
