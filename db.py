from os import name
from pydantic import BaseModel, EmailStr, AnyUrl
from typing import Optional


class sign_up(BaseModel):
    username: str
    email: EmailStr
    password: str


class links(BaseModel):
    username: str
    link_name: str
    link: AnyUrl


class editlinks(BaseModel):
    username: str
    link_name: str
    new_link: AnyUrl


class deletelinks(BaseModel):
    username: str
    link_name: str
