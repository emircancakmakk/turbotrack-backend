import requests
from requests.structures import CaseInsensitiveDict
from urllib.parse import urlencode
from lib.user import User

requests.headers = CaseInsensitiveDict()
requests.headers['Content-Type'] = 'application/x-www-form-urlencoded'

CLIENT_ID = '10ae9d30-1853-48ff-81cb-47b58a325685'

class Organisation:
    def __init__(self, data):
        self.id = data['CustomerId']
        self.name = data['Title']
        self.short_name = data['ShortName']
        self.url = data['BaseUrl']

        self.client = requests.Session()
        self.client.cookies.update({'login': f'CustomerId={self.id}'})

    def authenticate(self, username, password):
        data = {
            'client_id': CLIENT_ID,
            'grant_type': 'password',
            'password': password,
            'username': username
        }

        response = self.client.post(f'{self.url}/restapi/oauth2/token', data=data)
        response.raise_for_status()

        data = response.json()

        data.update({'organisation': self})

        if response.status_code != 200:
            raise ValueError('Request failure')

        user = User(data)
        return user
