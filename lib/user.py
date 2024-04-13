import requests

requests.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

BASE_URL = 'https://www.itslearning.com'

class User:
    def __init__(self, data):
        self.accessToken = data['access_token']
        self.refreshToken = data['refresh_token']
        self.tokenTimeout = data['expires_in']
        self.organisation = data['organisation']

        self.courses = None
        self.tasks = None

        self.id = None
        self.firstName = None
        self.lastName = None
        self.language = None
        self.profileImage = None
        self.calendar = None

        self.client = requests.Session()
        self.client.params.update({'access_token': self.accessToken})

    def fetch_personal_info(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch user info')

        if self.id is not None:
            return self

        response = self.client.get(f'{BASE_URL}/restapi/personal/person/v1')
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        self.id = data['PersonId']
        self.firstName = data['FirstName']
        self.lastName = data['LastName']
        self.language = data['Language']
        self.profileImage = data['ProfileImageUrl']
        self.calendar = data['iCalUrl']

        return self

    def fetch_courses(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch user info')

        if self.courses is not None:
            return self.courses

        response = self.client.get(f'{BASE_URL}/restapi/personal/courses/v1')
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        formatted_courses = [{
            'id': course['CourseId'],
            'name': course['Title'],
            'updated': course['LastUpdatedUtc'],
            'notificationCount': course['NewNotificationsCount'],
            'newsCount': course['NewBulletinsCount'],
            'url': course['Url'],
            'color': course['CourseColor']
        } for course in data['EntityArray']]

        self.courses = formatted_courses

        return self.courses

    def fetch_tasks(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch user info')

        if self.tasks is not None:
            return self.tasks

        response = self.client.get(f'{BASE_URL}/restapi/personal/tasks/v1')
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        formatted_tasks = [{
            'id': task['TaskId'],
            'name': task['Title'],
            'description': task['Description'],
            'courseName': task['LocationTitle'],
            'status': task['Status'],
            'deadline': task['Deadline'],
            'url': task['Url'],
            'content': task['ContentUrl'],
            'icon': task['IconUrl'],
            'elementId': task['ElementId'],
            'type': task['ElementType']
        } for task in data['EntityArray']]

        self.tasks = formatted_tasks

        return self.tasks

    def fetch_info(self):
        self.fetch_personal_info()
        self.fetch_courses()
        self.fetch_tasks()
        return self

    @property
    def authenticated(self):
        return self.accessToken and int(self.tokenTimeout) > 0

    def fetch_unread_messages_count(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch messages count')

        response = self.client.get(f'{BASE_URL}/restapi/personal/instantmessages/messagethreads/unread/count/v1')
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        return data

    def fetch_unread_notifications_count(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch notification count')

        response = self.client.get(f'{BASE_URL}/restapi/personal/notifications/unread/count/v1')
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        return data

    def fetch_notifications(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch notifications')

        response = self.client.get(f'{BASE_URL}/restapi/personal/notifications/v1', params={'PageIndex': 0, 'PageSize': 20})
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        notifications = [{
            'id': notification['NotificationId'],
            'text': notification['Text'],
            'date': notification['PublishedDate'],
            'author': {
                'id': notification['PublishedBy']['PersonId'],
                'firstName': notification['PublishedBy']['FirstName'],
                'lastName': notification['PublishedBy']['LastName'],
                'profile': notification['PublishedBy']['ProfileUrl'],
                'profileImage': notification['PublishedBy']['ProfileImageUrl']
            },
            'type': notification['Type'],
            'url': notification['Url'],
            'content': notification['ContentUrl'],
            'isRead': notification['IsRead']
        } for notification in data['EntityArray']]

        return notifications

    def fetch_comments(self, id):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch comments')

        response = self.client.get(f'{BASE_URL}/restapi/personal/lightbulletins/{id}/comments/v1', params={'PageIndex': 0, 'PageSize': 20})
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        return data

    def fetch_message_threads(self, options={}):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch comments')

        options = {
            'maxThreadCount': 10,
            'query': None,
            'pageIndex': 0,
            'pageSize': 20,
            **options
        }

        def format_message(message):
            formatted = {
                'id': message['MessageId'],
                'threadId': message['MessageThreadId'],
                'created': message['Created'],
                'author': {
                    'id': message['CreatedBy'],
                    'name': message['CreatedByName'],
                    'profileImage': message['CreatedByAvatar']
                },
                'text': message['Text'],
                'attachment': {
                    'url': message['AttachmentUrl'],
                    'name': message['AttachmentName']
                } if message.get('AttachmentUrl') else None
            }
            return formatted

        def format_participant(participant):
            formatted = {
                'id': participant['PersonId'],
                'firstName': participant['FirstName'],
                'lastName': participant['LastName'],
                'profile': participant['ProfileUrl'],
                'profileImage': participant['ProfileImageUrl']
            }
            return formatted

        response = self.client.get(f'{BASE_URL}/restapi/personal/instantmessages/messagethreads/v1', params={
            'maxThreadCount': options['maxThreadCount'],
            'threadPage': options['pageIndex'],
            'maxMessages': options['pageSize'],
            'searchText': options['query']
        })
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        threads = [{
            'id': thread['InstantMessageThreadId'],
            'name': thread['Name'],
            'created': thread['Created'],
            'type': thread['Type'],
            'messages': [format_message(message) for message in thread['Messages']['EntityArray']],
            'lastMessage': format_message(thread['LastMessage']),
            'matchedMessageIds': thread['MatchingMessageIds'],
            'participants': [format_participant(participant) for participant in thread['Participants']],
            'lastReadMessageId': thread['LastReadInstantMessageId']
        } for thread in data['EntityArray']]

        return threads
    
    def fetch_news(self):
        if not self.authenticated:
            raise ValueError('Must be authenticated to fetch news')

        response = self.client.get(f'{BASE_URL}/restapi/personal/notifications/stream/v1', params={'PageIndex': 0, 'PageSize': 20})
        response.raise_for_status()

        data = response.json()
        if response.status_code != 200:
            raise ValueError('Request failure')

        news = [{
            'id': news['NotificationId'],
            'location': news['LocationTitle'],
            'text': news['Text'],
            'date': news['PublishedDate'],
            'author': {
                'id': news['PublishedBy']['PersonId'],
                'firstName': news['PublishedBy']['FirstName'],
                'lastName': news['PublishedBy']['LastName'],
                'profile': news['PublishedBy']['ProfileUrl'],
                'profileImage': news['PublishedBy']['ProfileImageUrl']
            },
            'type': news['ElementType'],
            'url': news['Url'],
            'contents': {
                'id': news['LightBulletin']['LightBulletinId'] if news.get('LightBulletin') else None,
                'text': news['LightBulletin']['Text'] if news.get('LightBulletin') else None,
                'url': news['ContentUrl']
            }
        } for news in data['EntityArray']]

        return news
    
    