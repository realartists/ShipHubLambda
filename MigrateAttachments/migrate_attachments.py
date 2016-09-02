import os
import os.path
import binascii
import base64
import boto3
import io
import httplib
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

def migrate_attachment(organizationID, attachmentID, mimeType, filename, token):
  ucHost = "uc.realartists.com"
  path = "/content/%s/%s?auth=%s&mimeType=%s" % (organizationID, attachmentID, token, mimeType)
  
  (uploadURL, url) = presign(filename, mimeType)
  
  downloadConn = httplib.HTTPSConnection(ucHost)
  downloadConn.request("GET", path)
  download = downloadConn.getresponse()
  if (download.status != 200):
    raise Exception("Bad download code %d" % (download.status))
  contentLength = download.getheader("Content-Length")
  
  p = urlparse.urlparse(uploadURL)
  uploadConn = httplib.HTTPSConnection(p.netloc)
  headers = {"content-type": mimeType, "Content-Length": contentLength}
  uploadConn.request("PUT", ("%s?%s" % (p.path, p.query)), download, headers)
  upload = uploadConn.getresponse()
  
  if (upload.status >= 400):
    raise Exception("Bad upload code %d" % (upload.getcode()))
  
  return url
    
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
  url = migrate_attachment(event["organizationID"], event["attachmentID"], event["mimeType"], event["filename"], event["token"])
  return { "url" : url }

if __name__ == "__main__":
  if len(sys.argv) != 6:
    print "Usage: python %s organizationID attachmentID mimeType filename token" % (sys.argv[0])
    sys.exit(1)
    
  print(repr(sys.argv))
  (organizationID, attachmentID, mimeType, filename, token) = sys.argv[1:]
  print migrate_attachment(organizationID, attachmentID, mimeType, filename, token)

