import requests
import traceback
import uuid
import os
import os.path
import binascii
import base64
import boto3
import sys
try:
  from urllib import quote
except:
  from urllib.parse import quote

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

def store(token, fileData, filename, fileMime):
  if validate_user(token):
    myUUID = uuid.uuid4()
    myRand = binascii.hexlify(os.urandom(16))
    
    if filename is None:
      filename = "file"
    
    path = str(myUUID) + "/" + myRand + "/" + filename
    
    print(path)
    
    s3 = boto3.resource('s3')
    
    bucket = s3.Bucket('shiphub-attachments')
    bucket.put_object(
      ACL='public-read',
      Body=fileData,
      ContentType=fileMime,
      Key=path)
      
    urlPath = path.replace("/" + filename, "/" + quote(filename))
    return "https://s3.amazonaws.com/shiphub-attachments/" + path    

def handler(event, context):
  fileDataB64 = event["file"]
  fileData = base64.b64decode(fileDataB64)
  url = store(event["token"], fileData, event["filename"], event["fileMime"])
  return { "url": url }
 
if __name__ == "__main__":
  (token, filename, mime) = sys.argv[1:]
  fileData = open(filename, "rb").read()
  print(store(token, fileData, os.path.basename(filename), mime))

    
