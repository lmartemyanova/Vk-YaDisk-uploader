import requests
import datetime
import time
import PySimpleGUI as sg
import json


class YandexDisk:
    url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        """Метод получения headers для get-запроса"""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        return headers

    def create_folder(self):
        headers = self.get_headers()
        folder_name = f"vk_copy_{datetime.datetime.now().strftime('%d.%m.%Y_%H.%M')}"
        params = {'path': folder_name}
        response = requests.put(self.url, headers=headers, params=params).json()
        # folder_href = response['href']
        return folder_name

    def upload(self, vk_photos):
        """Метод загрузки фото на яндекс диск"""
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
        photos_json = []
        for photo in vk_photos:
            photos_json.append({'file_name': photo['file_name'], 'size': photo['type']})
        headers = self.get_headers()
        params = {'path': f'{folder_name}/photos.json'}
        response = requests.get(self.url + '/upload', headers=headers, params=params).json()
        href = response['href']
        response = requests.put(href, data=json.dumps(photos_json))
        response.raise_for_status()
        print("Json успешно загружен") if response.status_code == 201 else print("Ошибка загрузки json")
        return
