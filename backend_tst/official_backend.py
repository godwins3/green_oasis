import json
import urllib.request

# URL = ""
URL = "http://127.0.0.1:5004"

token_home = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODI0ODAyMDAsImlhdCI6MTY3OTg4ODIwMCwic3ViIjoxMCwic3RyaW5nIjoiNklOR1cyOTQ2In0.6_Difxq32enRBhEBcOFlE9bg21k8LKJBa_6PMLWVhWo"
token_google = ""
reg_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODAwNjA3MjMsImlhdCI6MTY3OTg4NzkyMywiZm9ybSI6ImVtYWlsIiwia2V5IjoiaGFzc2FuLmsuYXRodW1hbmlAZ21haWwuY29tIiwicGFzc3dvcmQiOiIxMjM0NTY3In0.cDF_7dbbY_RefNnn1nA49vNd_IBbc5TXWJmA32SMGX4"
req = urllib.request.Request(URL)
req.add_header("Content-Type", "application/json; charset=utf-8")
req.add_header("Authorization", token_home)
req.add_header("User-Agent", "Mozilla/5.0")


def send_email_verification():
    x = {
        "subject": "sendVerification",
        "form": "email",
        "key": "hassan.k.athumani@gmail.com",
        "password": "1234567",
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def verify_email():
    x = {
        "subject": "verify",
        "code": "2365",
        "form": "email",
        "key": "hassan.k.athumani@gmail.com",
        # "password": "1234567",
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def register_user():
    x = {
        "subject": "register_normal",
        "displayName": "displayName",
        "about": "whatIdo",
        # "form": "form",
        # "key": "key",
        "password": "password",
        "location": [32.09, 29.09],
        "country": "KE",
        "gender": "male",
        "birthday": -5730144000,
        "over18": "1",
        "interestedIn": "female",
        "interest": ['running', 'swimming', 'dancing'],
        "profile_image": "male_1.png"
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def login():
    x = {
        "subject": "login_normal",
        "key": "hassan.k.athumani@gmail.com",
        "password": "password",
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def get_country():
    x = {
        "subject": "getCountry"
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def add_media():
    x = {
        "subject": "addMedia",
        "fileType": "jpg",
        "createdOn": 1678979803000
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def upload_smileid():
    x = {
        "subject": "uploadSmileID",
        "fileType": "jpg",
        "createdOn": 1678979803000
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())

def confirm_upload():
    x = {
        "subject": "confirmUpload",
        "mediaId": 5,
        "confirmation": 204
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def delete_media():
    x = {
        "subject": "deleteMedia",
        "mediaId": 5
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def get_personal_info():
    x = {
        "subject": "getPersonalInfo"
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def upload_id_image():
    x = {
        "subject": "uploadPhoto",
        'file_type': 'jpg',
        'media_type': 'id'
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def upload_selfie_image():
    x = {
        "subject": "uploadPhoto",
        'file_type': 'jpg',
        'media_type': 'selfie'
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def confirm_verification_upload():
    x = {
        "subject": "confirmVerificationUpload",
        'verification_id': 1,
        'confirmation': 204
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def request_verification():
    x = {
        "subject": "compareFaces"
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def add_story():
    x = {
        "subject": "addStory",
        "fileType": "jpg",
        "createdOn": 1678979803000
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def confirm_story_upload():
    x = {
        "subject": "confirmStoryUpload",
        "mediaId": 3,
        "confirmation": 204
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def get_stories():
    x = {
        "subject": "getStories",

    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


def delete_story():
    x = {
        "subject": "deleteStory",
        "mediaId": 3
    }
    body2 = json.dumps(x)
    jsondata = body2.encode("utf-8")
    r = urllib.request.urlopen(req, jsondata)
    print(r.read().decode())


# TEST FUNCTIONS
# send_email_verification()
# verify_email()
# register_user()
# login()
# get_country()
# add_media()
# confirm_upload()
# delete_media()
# get_personal_info()
# upload_id_image()
# upload_selfie_image()
# confirm_verification_upload()
# request_verification()
# add_story()
# confirm_story_upload()
# get_stories()
# delete_story()
