from pymongo import MongoClient
from bson import ObjectId
import gridfs

MONGO_IP = '192.168.1.105'
MONGO_PORT = 27017
DB = "ebookscollection"
COLLECTION = "library"

client = MongoClient(MONGO_IP, MONGO_PORT)
db = client[DB]
collection = db[COLLECTION]

gfs = gridfs.GridFSBucket(db, bucket_name=COLLECTION)
fs = gridfs.GridFS(db, collection=COLLECTION)


def exists(title, source):
    return collection.count({"title": title, "source": source}) > 0


def create(record):
    collection.insert_one(record)


def upload(obj):
    file_ext = obj['metadata']['contentType'].split('/')[1]
    return str(gfs.upload_from_stream(obj["filename"] + "." + file_ext, obj['content'], metadata=obj['metadata']))


def download(fileid):
    obj = fs.get(ObjectId(fileid))
    filename = obj.filename
    with open(filename, 'wb+') as file:
        gfs.download_to_stream(ObjectId(fileid), file)

