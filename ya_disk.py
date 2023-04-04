import requests
import datetime
# import PySimpleGUI as sg
import time
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
        params = {'path': 'vk_copy_' + datetime.datetime.now().strftime('%d.%m.%Y_%H:%M')}
        response = requests.put(self.url, headers=headers, params=params).json()
        folder_href = response['href']
        return folder_href

    def upload(self, vk_photos):
        """Метод загрузки фото на яндекс диск"""
        folder_href = self.create_folder()
        headers = self.get_headers()
        for photo in vk_photos:
            params = {'url': photo['url'],
                      'path': f'{folder_href}/{filename}.jpg'}
            # sg.one_line_progress_meter('Your progress',
            #                            link + 1,
            #                            len(photos_links),
            #                            '-key-'
            #                            )
            response = requests.post(self.url + '/upload', headers=headers, params=params).json()
            operation = requests.get(response['href']).json()
            print(f'File {filename} uploaded successfully') if operation['status'] == 'success' \
                else print(f'File {filename} has not uploaded, try to upload it manually')
            # time.sleep(1)
        return

    def upload_json(self, vk_photos):
        photos_json = []
        for photo in vk_photos:
            photos_json.append({'file_name': photo['file_name'], 'size': photo['type']})
        headers = self.get_headers()
        params = {'path': f'{folder_href}/photos.json'}
        response = requests.get(self.url + '/upload', headers=headers, params=params).json()
        href = response['href']
        response = requests.put(href, data=json.dumps(photos_json))
        response.raise_for_status()
        print("Json uploaded successfully") if response.status_code == 201 else print("Try again")
        return

