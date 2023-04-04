import requests
from pprint import pprint
import datetime

class Vk:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version='5.131'):
        self.params = {'access_token': token,
                       'v': version}

    def get_id(self, screen_name):
        '''To get the user id by screen_name
        return user_id'''
        params = {'screen_name': screen_name}
        response = requests.get(self.url + 'utils.resolveScreenName', params={**self.params, **params}).json()
        user_id = response['response']['object_id']
        return user_id

    def get_links(self, user_id, count=5):
        '''
        To get the links for uploading profile photos to yandex disk by user id
        '''
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        response = requests.get(self.url + 'photos.get', params = {**self.params, **params}).json()
        pprint(response)   # delete
        photos = []
        for photo in response['response']['items']:
            photo_types = sorted([size['type'] for size in photo['sizes']])
            max_type = (photo_types[-1] if 'w' not in photo_types else 'w')
            for size in photo['sizes']:
                if size['type'] == max_type:
                    photo_params = {'likes': photo['likes']['count'],
                                    'type': max_type,
                                    'date': datetime.datetime.fromtimestamp(photo['date']).strftime('%d-%m-%Y'),
                                    'url': size['url']}
                    photos.append(photo_params)
        def sort_photos(photo):
            if photo['type'] == 'w':
                return 'zz'
            return photo['type']
        photos_sorted = sorted(photos, key=sort_photos)
        photos_for_upload = photos_sorted[-count:]
        print(photos_sorted)  # delete
        print(photos_for_upload)  # delete
        return photos_for_upload





