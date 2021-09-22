from os import environ
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
import pymongo, ssl
from datetime import timedelta, datetime
from jose import jwt
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from db import links, editlinks, sign_up, deletelinks

ouath2_Scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

SECRETKEY = "668101015464f3c7d0fbaee20bd44cb999437d7d817480613105611a0b2a6f24"

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

        register_info.insert_one(login_data.dict())

        x = register_info.find_one({"username": login_data.username})

        del x["_id"]

        return {"Details": x}


@app.post("/postlinks")
def post_links(fetch: links, token: str = Depends(ouath2_Scheme)):

    username: str = fetch.username

    a = register_info.find_one({"username": username})
    x = a | {fetch.link_name: fetch.link}

    if register_info.find_one({fetch.link_name: fetch.link}):

        return {
            "message": "There is already a link in this in this name.Try using other name"
        }

    else:

        register_info.find_one_and_replace({"username": username}, x)

    return {"message": f"link:{fetch.link_name} sucessfully added"}


@app.post("/editlinks")
def edit_links(authorization: editlinks, token: str = Depends(ouath2_Scheme)):

    if register_info.find_one({authorization.link_name: authorization.new_link}):
        register_info.update_one(
            {"username": authorization.username},
            {"$set": {authorization.link_name: authorization.new_link}},
        )
        return {"message": f"link:{authorization.link_name} sucessfully_updated"}
    else:
        return {
            "error": f"No such link is identified in the name of {authorization.link_name} ..."
        }


@app.post("/deletelinks")
def delete_links(fetch: deletelinks, token: str = Depends(ouath2_Scheme)):

    if register_info.find_one({"username": fetch.username}):
        if register_info.update(
            {"username": fetch.username}, {"$unset": {fetch.link_name: "Default"}}
        ):
            return {"message": f" link {fetch.link_name} sucessfully deleted"}
        else:
            return {
                "error": f"No such link is identifide in the name of {fetch.link_name}"
            }
    else:
        return {"error": f"invali username:{fetch.username}"}


@app.get("/view/{username}")
def view(username: str, token: str = Depends(ouath2_Scheme)):
    x = register_info.find_one({"username": username})
    if x:
        del x["_id"]
        del x["password"]
        return x
    else:
        return {"message": "invalid username "}


@app.get("/alluser")
def viewall(token: str = Depends(ouath2_Scheme)):
    users = [sign_up(**user).username for user in register_info.find()]
    return {"all_user_names": users}
