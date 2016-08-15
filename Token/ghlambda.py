"""This project is used by the Ship for GitHub signup process to turn GitHub OAuth
codes into OAuth tokens. While the signup process is nearly entirely client side
JavaScript, using this server side AWS lambda function allows us to keep the
OAuth client secret actually secret
"""

import requests
import traceback

def redeem_code(client_id, client_secret, code):
  req = requests.post("https://github.com/login/oauth/access_token", params={
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code
  }, headers={
    "Accept": "application/json"
  }, timeout=50.0)
  req.raise_for_status()
  result = req.json()
  return result["access_token"]

def oauth_handler(event, context):  
  code = event["code"]
  
  client_secret = "3aeb9af555d7d2285120b133304c34e5a8058078"
  client_id = "da1cde7cfd134d837ae6"
  
  if "environment" in event:
    e = event["environment"]
    if e == "local":
      client_secret = "ef618bcb9000aef6960bed91a8becf2e33390342"
      client_id = "28ff213668a64e463c91"
    elif e == "development":
      client_secret = "c9b9355b909801547e874c7dd490f28dff1dda8e"
      client_id = "c32af1009c8dea2dbf59"

  token = redeem_code(client_id, client_secret, code)
  return {"token": token}
