import os
from pathlib import Path
import datetime as DT


import requests


def download_token(email, password):
    api_url = "https://my.farm.bot/api/tokens"
    request_body = {"user": {"email": email, "password": password}}
    response = requests.post(api_url, json=request_body)
    return response.json()


def get_token(raw_token):
    return raw_token.get("token").get("encoded")


def get_images(token):
    api_url = "https://my.farm.bot/api/images"
    headers = {'Authorization': token}
    response = requests.get(api_url, headers=headers)
    return response.json()


def batch_delete_photos(token, images_data):
    api_url = "https://my.farm.bot/api/images/"
    headers = {'Authorization': token}
    for image_data in images_data:
        img_id = image_data.get('id')
        response = requests.delete(api_url + str(img_id), headers=headers)
        if response.status_code != 200:
            print("Error deleting " + str(img_id))
            print("\n" + response.text)
        else:
            print("Deleted " + str(img_id))
    print("Batch delete finished")


def download_image(img_url, name, img_dir):
    response = requests.get(img_url)
    open(img_dir + str(name) + ".png", "wb").write(response.content)


if __name__ == '__main__':
    print("Automated download")
    email = "dummy_value"
    password = "dummy_value"
    raw_token = download_token(email, password)
    token = raw_token.get('token').get('encoded')
    images_data = get_images(token)
    today = DT.date.today()
    days = 14
    week_ago = today - DT.timedelta(days=days)
    week_days = []
    for i in range(0,days):
        week_days.append(str(today - DT.timedelta(days=i)))
    img_dir = "/var/www/html/images/"
    for week_day in week_days:
        print(f"Donwloading images for {week_day}")
        date_dir = img_dir+week_day+"/"
        Path(date_dir).mkdir(parents=True, exist_ok=True)
        for image_data in images_data:
            if week_day in image_data.get('created_at'):
                img_full_path = Path(date_dir + str(image_data.get('id')) + ".png")
                if not Path.is_file(img_full_path):
                    print(f"Downloading {img_full_path}")
                    download_image(image_data.get('attachment_url'), image_data.get('id'), date_dir)

        print(f"Donwload for {week_day} finished")
