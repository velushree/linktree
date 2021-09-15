from pydantic import BaseModel, EmailStr, AnyUrl
from typing import Optional


from pydantic import BaseModel,EmailStr,AnyUrl
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    metadata:Optional[str] = None

class links(BaseModel):
    email: EmailStr
    password: str
    link_name: str
    link: AnyUrl

class editlinks(BaseModel):
    email:EmailStr
    password:str
    link_name:str
    new_link:AnyUrl