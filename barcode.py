import requests
import json
from datetime import datetime
import mongo

API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
SOURCE = "library"


def get_book(isbn):
    print('calling api', isbn)
    resp = requests.get(API_URL + isbn)
    if resp.status_code != 200:
        raise ConnectionError()
    if resp.json()['totalItems'] == 0:
        print("ITEM NOT FOUND!")
        return

    item = resp.json()['items'][0]['volumeInfo']
    obj = {}
    obj['isbn'] = isbn
    obj['title'] = item['title']
    obj['subtitle'] = item['subtitle'] if 'subtitle' in item else ''
    obj['authors'] = item['authors'] if 'authors' in item else ''
    obj['publisher'] = item['publisher'] if 'publisher' in item else ''
    obj['publishedDate'] = item['publishedDate'].split('-')[0] if 'publishedDate' in item else 0
    obj['description'] = item['description'] if 'description' in item else ''
    obj['pageCount'] = item['pageCount'] if 'pageCount' in item else 0
    obj['categories'] = item['categories'][0] if 'categories' in item else ''
    obj['thumbnail'] = item['imageLinks']['thumbnail'] if 'imageLinks' in item else ''

    json_data = json.dumps(obj)
    print(json_data)

    save(obj)


def save(obj):
    if mongo.exists(obj['title'], SOURCE):
        print('ALREADY EXIST!')
        return

    if obj['thumbnail'] != '':
        resp = requests.get(obj['thumbnail'], stream=True)
        content_type = resp.headers['Content-Type']
        image_id = mongo.upload({'filename': obj['title'],
                                 'content': resp.content,
                                 'metadata': {'contentType': content_type}})
    else:
        image_id = ""

    obj = mongo.create({"title": obj["title"], "subtitle": obj["subtitle"], "url": "",
                        "description": obj["description"],
                        "isbn": obj["isbn"], "isbn10": "", "category": obj["categories"],
                        "year": obj["publishedDate"], "author": obj["authors"],
                        "fileSize": 0, "fileFormat": "hard copy", "pages": obj["pageCount"],
                        "source": "library", "imageId": image_id, "created": datetime.now()})


def download_img(obj_id):
    mongo.download(obj_id)


def read_barcode():
    while True:
        barcode = input('Scan:')
        get_book(barcode)


def main():
    read_barcode()


if __name__ == '__main__':
    main()
