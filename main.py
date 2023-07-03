from ya_disk import YandexDisk
from vk import Vk
import os
from dotenv import load_dotenv, find_dotenv


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    vk_user = Vk(token=os.getenv('access_token'))

    # vk_id = input("Введите id профиля или короткое имя пользователя, для которого необходимо выполнить копирование: ")

    # try:
    #     vk_id = int(vk_id)
    #     vk_photos = vk_user.get_links(vk_id)
    # except ValueError:
    #     user_id = vk_user.get_id(vk_id)

    # vk_user.create_album()
    # vk_user.get_upload_server()
    vk_user.upload_photos()
