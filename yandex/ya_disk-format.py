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
        load_dotenv(find_dotenv())
        load_dotenv(find_dotenv())
        secret = os.getenv('api-secret')
        if not secret:
            raise ValueError("❌ Переменная 'api-secret' не найдена в .env")
        convertapi.api_credentials = secret

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
        """
        To get the folder in user's Yandex disk where are the .heic files situated.
        :return: folder name (str)
        """
        path = str(input("Введите название папки на Яндекс диске: "))
        return path

    def get_files_list(self, path):
        headers = self.get_headers()
        params = {'path': path}
        
        # НЕ вызываем .json() сразу
        response = requests.get(self.url, headers=headers, params=params)
        
        if response.status_code != 200:
            print("❌ Ошибка запроса к Яндекс.Диску:")
            print(f"Status: {response.status_code}")
            print("Response:", response.text)
            response.raise_for_status()

        # Только теперь вызываем .json()
        data = response.json()

        if '_embedded' not in data:
            print("⚠️ В ответе нет '_embedded'. Возможно, указан путь к файлу или папка пуста.")
            print("Ответ:", json.dumps(data, indent=2, ensure_ascii=False))
            return []

        return data["_embedded"]["items"]

    def get_upload_link(self, file_path):
        """
        Method to get the link to upload file to Yandex disk
        :param file_path: file name in folder (str)
        :return: upload link (str)
        """

        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path}
        response = requests.get(url, headers=headers, params=params).json()
        href = response['href']
        return href

    def change_heic_to_jpg(self):
        directory = self.get_directory()
        files = self.get_files_list(directory)
        
        save_dir = os.path.join(os.getcwd(), "files")
        os.makedirs(save_dir, exist_ok=True)

        for f in files:
            if f["mime_type"] == "image/heic":
                url = f["file"]
                result = convertapi.convert('jpg', {
                    'File': url
                }, from_format='heic')
                result.save_files(save_dir)

        folder = os.listdir(save_dir)
        for i in folder:
            photo = os.path.join(save_dir, i)
            href = self.get_upload_link(f"{directory}/{i}")
            with open(photo, 'rb') as f:
                response = requests.put(href, data=f)

        # Очистка
        for i in folder:
            os.remove(os.path.join(save_dir, i))

        return "Success"


    def change_heic_to_png(self):
        """
        If files in folder has the format .heic this method allows to change the format to .png.
        The result is the double files in user's folder: in .heic and in .png.
        :return:
        """
        directory = self.get_directory()
        files = self.get_files_list(directory)

        save_dir = os.path.join(os.getcwd(), "files")
        os.makedirs(save_dir, exist_ok=True)

        for f in files:
            if f["mime_type"] == "image/heic":
                url = f["file"]

                convertapi.convert('png', {
                    'File': url
                }, from_format='heic').save_files(save_dir)

        folder = os.listdir(save_dir)
        for i in folder:
            photo = os.path.join(save_dir, i)
            href = self.get_upload_link(f"{directory}/{i}")
            with open(photo, 'rb') as f:
                response = requests.put(href, data=f)

        for i in folder:
            os.remove(os.path.join(save_dir, i))

        return "Success"


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    ya_user = YandexDiskFormat(token=os.getenv('ya_token'))
    choice = int(input("В какой формат Вы хотите сконвертировать фото, .jpg (1) или .png (2)? "))
    if choice == 1:
        ya_user.change_heic_to_jpg()
    elif choice == 2:
        ya_user.change_heic_to_png()
    else:
        "Какая-то ошибка :( Попробуйте запустить файл снова!"
