from os import environ
from fastapi import FastAPI
from pydantic import EmailStr
import pymongo
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = FastAPI()

myclient = pymongo.MongoClient(environ.get('DBURL'))
linktree = myclient["linktree"]
register_info = linktree["registerinfo"]

from db import User,links,editlinks

@app.get("/")
def home():
    return {"message": "Enter login/signup"}


@app.post("/signup")
def signup(login_data: User):

    if register_info.find_one({"email":login_data.email}):
        return {"error":"email already exists.Try another one"}

    else:
        login_data.password = generate_password_hash(login_data.password)

        beta = register_info.insert_one(login_data.dict())

        if beta:
            return {"message": "Sucessfully Posted"}

        else:

            return {"message": "Something went wrong try again"}


@app.post("/login")
def login_to_userdata(login_data: User):

    email: EmailStr= login_data.email

    user = register_info.find_one({"email": email})

    if user and check_password_hash(user["password"], login_data.password) == True:
        del user["_id"]
        del user["age"]
        return user

    else:

        return {"message": "invalid credentials"}


@app.post("/postlinks")
def post_links(fetch: links):

    email: EmailStr = fetch.email

    a = register_info.find_one({"email": email})

    if a and check_password_hash(a["password"], fetch.password) == True:

        x=a|{fetch.link_name:fetch.link}

        if register_info.find_one({fetch.link_name:fetch.link}):

            return {"message":"There is already a link in this in this name.Try using other name"}

        else:    

            register_info.find_one_and_replace({"email":fetch.email},x)

            return {"message":"link sucessfully added"}

    else:
        {"message": "invalid credentials"}


@app.post("/editlinks")
def edit_links(authorization: editlinks):

    email: EmailStr = authorization.email

    a = register_info.find_one({"email": email})

    if a and check_password_hash(a["password"], authorization.password) == True:

        register_info.update_one({"email":authorization.email},{"$set":{authorization.link_name:authorization.new_link}})

        return {"message":"link_sucessfully_updated"}
    else:
        return {"error": "Invalid credentials"}


@app.post("/deletelinks")
def delete_links(fetch: links):

    email: EmailStr = fetch.email

    a = register_info.find_one({"email": email})

    if a and check_password_hash(a["password"], fetch.password) == True:

        z=register_info.update({"email":fetch.email},{"$unset":{fetch.link_name:fetch.link}})

        if register_info.find_one({fetch.link_name:fetch.link}):

            return {"message":"link sucessfully deleted"}

        else:
            return {"message":"No such link identified"}

    else:
        {"message": "Invalid credentials"}