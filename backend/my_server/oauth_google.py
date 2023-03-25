import json
import urllib.parse
import requests
import base64
import os

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Read the oauth data from the json file from Google
def load_data():
    if not os.path.exists("oauth_google.json"):
        print()
        print("There is no oauth_google.json present in the backend folder.")
        print("Please place the file there. It can be downloaded from the")
        print("Google Developer Portal. If you are not the developer of the website")
        print("ask the developer for the json file.")
        print()
        exit(1)
    with open("oauth_google.json", "r") as file:
        string = file.read()
        return json.loads(string)

data = load_data()

def get_google_client_id():
    global data
    return data["web"]["client_id"]

def get_google_client_secret():
    global data
    return data["web"]["client_secret"]

def create_authorize_url(state):
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": get_google_client_id(),
        "redirect_uri": "http://localhost:5173/login/google/callback",
        "scope": "openid email",
        "state": state
    })
    return AUTHORIZE_URL + "?" + params

def verify_google_token(code):
    params = {
        "grant_type": "authorization_code",
        "client_id": get_google_client_id(),
        "client_secret": get_google_client_secret(),
        "redirect_uri": "http://localhost:5173/login/google/callback",
        "code": code
    }
    result = requests.post(TOKEN_URL, data=params).json()
    if "error" in result:
        return ({
            "success": False,
            "error": "Försök igen"
        }, None, None)
    id_token = result["id_token"]
    data_string = id_token.split(".")[1]
    data_string += "==" # Avoid "Incorrect padding" errors
    data_string = base64.b64decode(data_string)
    data = json.loads(data_string)
    google_account_id = data["sub"]
    email = data["email"]
    return (None, google_account_id, email)