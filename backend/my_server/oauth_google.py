import json
import urllib.parse

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Read the oauth data from the json file from Google
def load_data():
    with open("oauth_google.json", "r") as file:
        string = file.read()
        return json.loads(string)

data = load_data()

def get_google_client_id():
    return data["web"]["client_id"]

def create_authorize_url(state):
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": get_google_client_id(),
        "redirect_uri": "http://localhost:5173/login/google/callback",
        "scope": "openid email",
        "state": state
    })
    return AUTHORIZE_URL + "?" + params