from google.cloud import storage
import os

from . import meta_utils


def upload_blob(bucket_name, source_file_name, destination_blob_name):
  ''' Uploads a file/folder to the bucket '''
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)

  blob.upload_from_filename(source_file_name)


def blob_exists(bucket_name, filename):
  client = storage.Client()
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(filename)
  return blob.exists()


def register_credentials():
  cred_file = str(meta_utils.get_project_root() / 'speech_key.json')
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file