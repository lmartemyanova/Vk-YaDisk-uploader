import requests
import datetime
import time
import PySimpleGUI as sg
import json
import os
from dotenv import load_dotenv, find_dotenv
import convertapi


class YandexDiskFormat:
    """
    Class YandexDiskFormat to change the format of photos in user's Yandex disk/
    E.g. from .heic to .jpg or .png

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

    def get_directory(self):
        path = str(input("Введите название папки: "))
        return path

    def get_files_list(self, path):
        """

        :param link:
        :return:
        """

        headers = self.get_headers()
        params = {'path': path}
        response = requests.get(self.url, headers=headers, params=params).json()
        files = response["_embedded"]["items"]
        return files

    def get_upload_link(self, file_path):
        """Метод получения ссылки для загрузки файла на яндекс диск"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path}
        response = requests.get(url, headers=headers, params=params).json()
        href = response['href']
        return href

    def change_heic_to_jpg(self):
        """

        :return:
        """
        directory = self.get_directory()
        files = self.get_files_list(directory)
        for f in files:
            if f["mime_type"] == "image/heic":
                url = f["file"]

                load_dotenv(find_dotenv())
                convertapi.api_secret = os.getenv('api-secret')
                convertapi.convert('jpg', {
                    'File': url
                }, from_format='heic').save_files(os.path.join(os.getcwd(), "files"))

        folder = os.listdir(os.path.join(os.getcwd(), "files"))
        for i in folder:
            photo = os.path.join(os.path.join(os.getcwd(), "files"), i)
            href = self.get_upload_link(f"{directory}/{i}")
            with open(photo, 'rb') as f:
                response = requests.put(href, data=f)

        for i in folder:
            os.remove(os.path.join(os.path.join(os.getcwd(), "files"), i))

        return "Success"

    def change_heic_to_png(self):
        """

        :return:
        """


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    ya_user = YandexDiskFormat(token=os.getenv('ya_token'))
    ya_user.change_heic_to_jpg()
