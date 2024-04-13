import requests

from lib.organisation import Organisation

client = requests.Session()

class ItsLearning:
    @staticmethod
    def search_organisation(query):
        response = client.get('https://www.itslearning.com/restapi/sites/all/organisations/search/v1', params={'searchText': query})
        response.raise_for_status()

        matches = [{'id': match['CustomerId'], 'name': match['SiteName']} for match in response.json().get('EntityArray', [])]
        return matches

    @staticmethod
    def fetch_organisation(id):
        if isinstance(id, list):
            if id and 'id' in id[0]:
                id = id[0]['id']

        response = client.get(f'https://www.itslearning.com/restapi/sites/{id}/v1')
        response.raise_for_status()

        data = response.json()
        if data is None:
            raise ValueError('Organisation did not exist')

        organisation = Organisation(data)
        return organisation

