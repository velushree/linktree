from os import environ
from re import X
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
import pymongo
from datetime import timedelta, datetime
from jose import jwt
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from db import delLink, sign_up, Link, Links

ouath2_Scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

SECRETKEY = environ.get("SECRETKEY")

myclient = pymongo.MongoClient(environ.get("DBURL"))
linktree = myclient["linktree"]
register_info = linktree["registerinfo"]


def authenticate(username: str, password: str):
    a = register_info.find_one({"username": username})

    if a and check_password_hash(a["password"], password) == True:
        return True

    else:
        return False


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode: dict = data.copy()

    expires = datetime.utcnow() + expires_delta
    to_encode | {"exp": expires}

    encoded_jwt = jwt.encode(to_encode, SECRETKEY, algorithm="HS256")

    return encoded_jwt


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if authenticate(username, password):
        access_token = create_access_token(
            data={"sub": username}, expires_delta=timedelta(minutes=30)
        )

        return {"username": username, "Access_Token": access_token}

    else:
        raise HTTPException(status_code=400, detail="Not Authenticated")


@app.get("/")
def home():
    return {"info": "If you already have an account login or else sign_up"}


@app.post("/signup")
def signup(login_data: sign_up):

    if register_info.find_one({"email": login_data.email}):
        return {"error": "email already exists.Try another one"}

    if register_info.find_one({"username": login_data.username}):
        return {"error": "username already exists.Try another one"}

    else:
        login_data.password = generate_password_hash(login_data.password)

        register_info.insert_one(login_data.dict() | {'links': []})

        x = register_info.find_one({"username": login_data.username})

        del x["_id"]

        return {"Details": x}


@app.post("/postlinks")
def post_links(fetch: Links, token: str = Depends(ouath2_Scheme)):

    username: str = fetch.username

    a = register_info.find_one({"username": username})
    if a:
        copy = a.copy()
        y = [link.dict() for link in fetch.links]
        copy['links'].extend(y)
        a.update(copy)
        data = register_info.find_one_and_replace({"username": username}, a)

        return Links(**data)
    else:
        return {'error': 'username not found'}


@app.post("/editlinks")
def edit_links(fetch: Links, token: str = Depends(ouath2_Scheme)):

    username: str = fetch.username

    a = register_info.find_one({"username": username})
    if a:
        copy = a.copy()
        y = [link.dict() for link in fetch.links]
        copy['links'] = y
        a.update(copy)
        data = register_info.find_one_and_replace({"username": username}, a)

        return Links(**data)
    else:
        return {'error': 'username not found'}


@app.post("/deletelinks")
def delete_links(data: delLink, token: str = Depends(ouath2_Scheme)):

    username = data.username
    link_name = data.link_name

    a = register_info.find_one({"username": username})
    req = None
    if a:
        links: list = a['links']
        for link in links:
            l = Link(**link)
            if l.link_name == link_name:
                req = links.index(link)
            else:
                continue
        if req:
            del a['links'][req]
            register_info.find_one_and_replace({'username': username}, a)
            return Links(**a)
        else:
            return {'error': 'link_name not found'}
    else:
        return {'error': 'username not found'}


@app.get("/view/{username}")
def view(username: str):
    x = register_info.find_one({"username": username})
    if x:
        del x["_id"]
        del x["password"]
        return x
    else:
        return {"message": "invalid username "}


@app.get("/alluser")
def viewall():
    users = [sign_up(**user).username for user in register_info.find()]
    return {"all_user_names": users}
