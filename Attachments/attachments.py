import requests
import traceback
import os
import os.path
import binascii
import base64
import boto3
from botocore.client import Config
import sys
try:
  from urllib import quote
except:
  from urllib.parse import quote
  
try:
  import urllib.parse as urlparse
except:
  import urlparse

def validate_user(token, server="api.github.com"):
  r = requests.get("https://%s/user" % (server), headers={
    "Accept": "application/json",
    "Authorization": "token %s" % (token)
  })
  try:
    r.raise_for_status()
    result = r.json()
    return ("login" in result)
  except:
    return False
    
def s3_path(filename):
  myRand = str(binascii.hexlify(os.urandom(16)).decode("ASCII"))
  path = myRand + "/" + filename
  return path
  
def s3_url(s3Path, filename):
  urlPath = s3Path.replace("/" + filename, "/" + quote(filename))
  url = "https://s3.amazonaws.com/shiphub-attachments/" + urlPath
  return url

def store(fileData, filename, fileMime):
  if filename is None:
      filename = "file"
  s3 = boto3.resource('s3')
  path = s3_path(filename)
  bucket = s3.Bucket('shiphub-attachments')
  bucket.put_object(
    ACL='public-read',
    Body=fileData,
    ContentType=fileMime,
    Key=path)
  return s3_url(path, filename)

def presign(filename, fileMime):
  if filename is None:
      filename = "file"
  path = s3_path(filename)
  s3 = boto3.client('s3', region_name="us-east-1")
  uploadURL = s3.generate_presigned_url(
      ClientMethod='put_object',
      Params={
          'Bucket': 'shiphub-attachments',
          'Key': path,
          'ACL': 'public-read',
          'ContentType': fileMime
      }
  )
  url = s3_url(path, filename)
  return (uploadURL, url)

def handler(event, context):
  if not validate_user(event["token"]):
    raise Exception("Invalid GitHub token")
    
  if "presign" in event:
    (uploadURL, url) = presign(event["filename"], event["fileMime"])
    return { "upload": uploadURL, "url": url }
  else:
    fileDataB64 = event["file"]
    fileData = base64.b64decode(fileDataB64)
    url = store(fileData, event["filename"], event["fileMime"])
    return { "url": url }

if __name__ == "__main__":
  (token, filename, mime) = sys.argv[1:]
  fileData = open(filename, "rb").read()
  if not validate_user(token):
    print("Invalid GitHub token")
    sys.exit(1)
  if 'PRESIGN' in os.environ:
    (uploadURL, URL) = presign(os.path.basename(filename), mime)
    r = requests.put(uploadURL, fileData, headers={"Content-Type": mime})
    print(r.text)
    print("Uploaded to %s. Now available at %s" % (uploadURL, URL))
  else:
    fileData = open(filename, "rb").read()
    print(store(fileData, os.path.basename(filename), mime))

    
