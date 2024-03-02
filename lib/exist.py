import requests
from getpass import getpass
import datetime
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import webbrowser
import json

class Exist:
    @staticmethod
    def get_oauth_tokens(client_id=None, client_secret=None):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                # parse the path of this request into its parts
                parts = urlparse(self.path)
                # then parse the query parameters into a dict
                query = parse_qs(parts.query)
                # and then get the code we need out of the dict
                code = query['code'][0]

                # tell the browser it worked
                self.send_response(200)
                self.wfile.write(b'OK!\n')
                # then get our access token
                self.server.result = self.get_token(code)

            def get_token(self, code):
                response = requests.post('https://exist.io/oauth2/access_token', {
                    'grant_type':'authorization_code',
                    'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': 'http://localhost:8000/', # TODO: make this configurable
                })
                data = response.json()
                return {
                    'access_token': data['access_token'],
                    'refresh_token': data['refresh_token']
                }
            
        # Kick open a browser window to get authorization
        params = {
            'client_id': client_id, 
            'response_type':'code', 
            'redirect_uri':'http://localhost:8000/',
            'scope':'productivity_write productivity_read', # TODO: this should probably be a config
        }
        querystring = urlencode(params)
        url = f"https://exist.io/oauth2/authorize?{querystring}"
        print(f"Opening {url}")
        webbrowser.open(url, new=0, autoraise=True)
    
        #  create a http server and listen for one request only
        server_address = ('127.0.0.1', 8000)
        httpd = HTTPServer(server_address, Handler)
        httpd.handle_request()
        tokens = httpd.result
        httpd.server_close()
        return tokens
    
    @staticmethod
    def exchange_refresh_token(client_id=None, client_secret=None, refresh_token=None):
        response = requests.post('https://exist.io/oauth2/access_token', {
            'grant_type':'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
        })
        # parse the response into json
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token']
        }

    def __init__(self, access_token=None):
        self.access_token=access_token

    def get_values(self):
        url = 'https://exist.io/api/2/attributes/with-values/'

        # make sure to authenticate ourselves with our token
        response = requests.get(url, headers={'Authorization': f'Bearer {self.access_token}'})

        attributes = {}

        if response.status_code == 200:

            # parse the response body as json
            data = response.json()

            # collect the data we want into a dict
            for attribute in data['results']:
                # grab the fields we want from the json
                label = attribute['label']
                value = attribute['values'][0]['value']
                # and store them as key/value
                attributes[label] = value

            # print today's date
            print(datetime.date.today().strftime("%A %d %B").upper())
            # now print our attribute labels and values
            for label, value in attributes.items():
                print(f"{label}: {value}")

        else:
            print("Error!", response.content)


    def acquire_attribute(self, attribute):
        # make the json string to send to Exist
        body = json.dumps([{'template': attribute, 'manual': False}])

        # make the POST request, sending the json as the POST body
        # we need a content-type header so Exist knows it's json
        response = requests.post("https://exist.io/api/2/attributes/acquire/", 
            data=body,
            headers={'Authorization':f'Bearer {self.access_token}',
                    'Content-type':'application/json'})

        if response.status_code == 200:
            # a 200 status code indicates a successful outcome
            print(f"Exist attribute {attribute} acquired")
        else:
            # print the error if something went wrong
            data = response.json()
            print("Error:", data)

        
    def set_value(self, attribute, value, date=None):
        if not date:
            date = datetime.date.today()

        iso_date = date.isoformat()
        payload = {'name': attribute, 'date': iso_date, 'value': value}
        body = json.dumps(payload)

        # make the POST request, sending the json as the POST body
        # we need a content-type header so Exist knows it's json
        requests.post("https://exist.io/api/2/attributes/update/", 
            data=body,
            headers={'Authorization':f'Bearer {self.access_token}',
                    'Content-type':'application/json'})


