import requests
import datetime
import time
import PySimpleGUI as sg
import json


class YandexDisk:
    """
    Class YandexDisk for uploading files to user's Yandex Disk

    attribute 'url': for requests to REST API Yandex Disk

    """

    url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token: str):
        """
        To initial the class YandexDisk object

        :param token (str): OAuth token of user's YandexDisk (collected by user input)

        """

        self.token = token

    def get_headers(self):
        """
        Method of getting headers for requests

        :return headers (dict)

        """

        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        return headers

    def create_folder(self):
        """
        Method allows to create a folder in user's Yandex Disk files
        in the format 'vk_copy_DD.MM.YYYY_HH.MM' (the current date and time)

        :return folder_name (str)

        """

        headers = self.get_headers()
        folder_name = f"vk_copy_{datetime.datetime.now().strftime('%d.%m.%Y_%H.%M')}"
        params = {'path': folder_name}
        response = requests.put(self.url, headers=headers, params=params).json()
        return folder_name

    def upload(self, vk_photos):
        """
        Method for uploading photos from vk id
        by post-request to REST API Yandex Disk;
        progress bar added to to track the progress of the program

        :param vk_photos: list of dicts with photo information:
        'likes', 'type', 'date', 'url', 'file_name'

        :return: None

        """

        folder_name = self.create_folder()
        headers = self.get_headers()
        for i, photo in enumerate(vk_photos):
            params = {'url': photo['url'],
                      'path': f'{folder_name}/{photo["file_name"]}.jpg'}
            sg.one_line_progress_meter('Your progress',
                                       i + 1,
                                       len(vk_photos),
                                       'Загрузка фото на Яндекс Диск:'
                                       )
            response = requests.post(self.url + '/upload', headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 202:
                operation_href = response.json()['href']
                operation = requests.get(url=operation_href, headers=self.get_headers())
                operation.raise_for_status()
                while operation.json()['status'] == 'in-progress':
                    operation = requests.get(url=operation_href, headers=self.get_headers())
                if operation.json()['status'] == 'success':
                    print(f'Файл {photo["file_name"]}.jpg успешно загружен')
                else:
                    print(f'Файл {photo["file_name"]}.jpg не загружен, попытайтесь загрузить его вручную, {operation.json()}')
            else:
                print(f'Ошибка {response.status_code}, попытайтесь загрузить файл {photo["file_name"]}.jpg вручную.')
        return

    def upload_json(self, vk_photos):
        """
        To upload json-file with photo information: 'file_name', 'size' (type)

        :param vk_photos: list of dicts with photo information:
        'likes', 'type', 'date', 'url', 'file_name'

        :return info about uploading the json file (str)

        """

        photos_json = []
        for photo in vk_photos:
            photos_json.append({'file_name': photo['file_name'], 'size': photo['type']})
        headers = self.get_headers()
        params = {'path': f'{folder_name}/photos.json'}
        response = requests.get(self.url + '/upload', headers=headers, params=params).json()
        href = response['href']
        response = requests.put(href, data=json.dumps(photos_json))
        response.raise_for_status()
        res = print("Json успешно загружен") if response.status_code == 201 else print("Ошибка загрузки json")
        return res
