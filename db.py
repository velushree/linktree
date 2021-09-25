from pydantic import BaseModel, EmailStr, AnyUrl


class Link(BaseModel):
    link_name: str
    link_url: AnyUrl


class Links(BaseModel):
    username: str
    links: list[Link]


class sign_up(BaseModel):
    username: str
    email: EmailStr
    password: str


class delLink(BaseModel):
    username: str
    link_name: str
