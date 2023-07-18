import os.path

import requests
from pprint import pprint
import datetime
import time

# from vk_save_logger import save_logger


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

    def get_links(self, user_id):
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

        try:
            count = int(input("Введите количество фото для сохранения (по умолчанию 5): "))
        except ValueError:
            count = 5

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

    def create_album(self):
        title = str(input('Введите название альбома (минимум 2 символа): '))
        description = str(input('Введите описание альбома (необязательно): '))
        print("Конфиденциальность альбома: "
              "0 - все пользователи, "
              "1 - только друзья, "
              "2 - друзья и друзья друзей, "
              "3 - только я")
        privacy = {
            '0': 'all',
            '1': 'friends',
            '2': 'friends_of_friends',
            '3': 'only_me'
        }
        privacy_view = str(input('Введите уровень доступа (3 по умолчанию) - кто может смотреть альбом: '))
        privacy_comment = str(input('Введите уровень доступа (3 по умолчанию) - кто может комментировать фото: '))
        params = {
            'title': title,
            'description': description,
            'privacy_view': privacy[privacy_view],
            'privacy_comment': privacy[privacy_comment]
        }
        try:
            response = requests.get(
                url=self.url + 'photos.createAlbum',
                params={**self.params, **params}
            )
            if response.status_code == 200:
                album_id = response.json()['response']['id']
                print(f"Альбом с id {album_id} успешно создан")
                return album_id
        except Exception as e:
            print(f'Альбом не создан: {e}')
            return

    def get_upload_server(self):
        print('Вы хотите создать новый альбом (Y) или загрузить фото в существующий (N)?')
        command = input('Y/N? ')
        if command.lower() == 'y':
            album_id = self.create_album()
        elif command.lower() == 'n':
            album_id = int(input('Введите идентификатор альбома (он находится в адресной строке после знака _): '))
        else:
            print('неверный ввод')
            return
        params = {
            'album_id': album_id
        }
        try:
            response = requests.get(url=self.url + 'photos.getUploadServer', params={**self.params, **params})
            if response.status_code == 200:
                upload_url = response.json()['response']['upload_url']
                return upload_url
        except Exception as e:
            print(f'Доступ к загрузке отклонен: {e}')
            return

    # @save_logger
    def upload_photos(self):
        server = self.get_upload_server()
        folder = str(input("Введите путь к папке, из которой нужно загрузить фото: "))
        for root, dirs, files in os.walk(folder):
            photos_lists = [os.path.join(folder, file) for file
                            in list(sorted(files, key=lambda x: (int(''.join(filter(str.isdigit, x.split('.')[0]))), x)))
                            if file.endswith('.JPG') or file.endswith('.PNG')
                            or file.endswith('.jpg') or file.endswith('.png')]
            # need better sort?
        while photos_lists:
            if len(photos_lists) < 5:
                data = [
                    ('file1', (photos_lists[0], open(f'{photos_lists[0]}', 'rb'), 'image/png')),
                ]
                del photos_lists[0]
            else:
                data = [
                    ('file1', (photos_lists[0], open(f'{photos_lists[0]}', 'rb'), 'image/png')),
                    ('file2', (photos_lists[1], open(f'{photos_lists[1]}', 'rb'), 'image/png')),
                    ('file3', (photos_lists[2], open(f'{photos_lists[2]}', 'rb'), 'image/png')),
                    ('file4', (photos_lists[3], open(f'{photos_lists[3]}', 'rb'), 'image/png')),
                    ('file5', (photos_lists[4], open(f'{photos_lists[4]}', 'rb'), 'image/png'))
                ]
                del photos_lists[0:5]
            try:
                response = requests.post(url=server, files=data)
                if response.status_code == 200:
                    params_save = response.json()
                    params_save['album_id'] = params_save.pop('aid')
                    try:
                        response_save = requests.get(url=self.url + 'photos.save',
                                                     params={**self.params, **params_save})
                        if response_save.status_code == 200:
                            print('Фото загружены в альбом')
                            time.sleep(3)
                            # return response_save.json()
                    except Exception as e:
                        print(f'{e}')
                        return
            except Exception as e:
                print(f'{e}')
                return
