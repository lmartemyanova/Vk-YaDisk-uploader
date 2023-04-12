from ya_disk import YandexDisk
from vk import Vk
from tokens import ya_token
import os
from dotenv import load_dotenv, find_dotenv


if __name__ == '__main__':

    load_dotenv(find_dotenv())
    vk_user = Vk(token=os.getenv('access_token'))
    vk_id = input("Введите id профиля или короткое имя пользователя, для которого необходимо выполнить копирование: ")
    try:
        photos_count = int(input("Введите количество фото для сохранения (по умолчанию 5): "))
    except ValueError:
        photos_count = 5

    try:
        vk_id = int(vk_id)
        vk_photos = vk_user.get_links(vk_id, photos_count)
    except ValueError:
        user_id = vk_user.get_id(vk_id)
        vk_photos = vk_user.get_links(user_id, photos_count)

    # ya_token = input("Введите токен Вашего Яндекс-диска: ")
    ya_uploader = YandexDisk(ya_token)
    ya_uploader.upload(vk_photos)
    # ya_uploader.upload_json(vk_photos)
