import requests
from pprint import pprint
import datetime


class Vk:
    """
    Class Vk to get information about profile photos and links for upload

    attribute 'url': for requests to API Vk

    """

    url = 'https://api.vk.com/method/'

    def __init__(self, token, version='5.131'):
        """
        To initial the class Vk object

        :param token: token of Vk standalone app (.env variable)
        :param version: default argument (version API Vk)

        """
        self.params = {'access_token': token,
                       'v': version}

    def get_id(self, screen_name):
        """
        To get the user id by screen_name if user inputted the screen_name

        :param screen_name: str from user input

        :return: user_id (int)

        """

        params = {'screen_name': screen_name}
        response = requests.get(self.url + 'utils.resolveScreenName', params={**self.params, **params}).json()
        user_id = response['response']['object_id']
        return user_id

    def get_links(self, user_id, count=5):
        """
        To get the links for uploading profile photos to yandex disk by user id

        Get the info about profile photo by get-request.
        Select the maximum size of each photo by type symbol (a -> z, w = max), get the link.
        Get names, file_name = likes count,
        if count is equal for some photos, file_name = likes count_upload date
        Get the info for photos for upload, photos count = param count, sort by max type.

        :param user_id: id Vk (int) from user input or from def get_id if not int
        :param count: count of the photos need to upload from user input (default 5)

        :return: photos_for_upload (list of dicts) contains photo information:
        dict (photo) keys: 'likes', 'type', 'date', 'url', 'file_name'

        """

        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        response = requests.get(self.url + 'photos.get', params={**self.params, **params}).json()
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
        likes = [photo['likes'] for photo in photos]
        for photo in photos:
            photo['file_name'] = photo['likes'] if likes.count(photo['likes']) == 1 \
                else f"{photo['likes']}_{photo['date']}"

        def sort_photos(photo):
            """For sorting photos by max type, a -> z, w = max"""
            if photo['type'] == 'w':
                return 'zz'
            return photo['type']

        photos_sorted = sorted(photos, key=sort_photos)
        photos_for_upload = photos_sorted[-count:]
        return photos_for_upload
