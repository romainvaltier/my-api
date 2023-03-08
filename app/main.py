from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import pandas as pd

description = """

My-API helps you do awesome stuff. 🚀

## user
blabla...

## categorie
blabla...

## equipement
blabla...

"""

api = FastAPI(title="My-API", description=description)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# list of users
users = {
    "captain": {
        "username": "captain",
        "hashed_password": pwd_context.hash("nemo"),
    },
    "ned": {
        "username": "ned",
        "hashed_password": pwd_context.hash("land"),
    },
    "pierre": {
        "username": "pierre",
        "hashed_password": pwd_context.hash("arronax"),
    },
    "jules": {
        "username": "jules",
        "hashed_password": pwd_context.hash("verne"),
    },
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("4dm1N"),
    },
}


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if not (users.get(username)) or not (
        pwd_context.verify(credentials.password,
                           users[username]["hashed_password"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@api.get("/")
async def get_index():
    return {"message": "Welcome to {} !".format(api.title)}


@api.get("/user")
async def current_user(username: str = Depends(get_current_user)):
    return "Hello {}".format(username)


class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    parent: Optional[str] = None


categories = [
    {"id": 0, "name": "Category A", "slug": "category-a",
        "description": "This is category A", "parent": "p0"},
    {"id": 1, "name": "Category B", "slug": "category-b",
        "description": "This is category B", "parent": "p1"},
    {"id": 2, "name": "Category C", "slug": "category-c",
        "description": "This is category C", "parent": "p2"},
    {"id": 7, "name": "Category D", "slug": "category-d",
        "description": "This is category D", "parent": "p7"},
]


class Equipment(BaseModel):
    id: int
    name: str
    slug: str
    categories: list[Category]
    quantity: str


equipments = [
    {"id": 0, "name": "Equipment A", "slug": "equipment-a",
        "categories": [categories[0], categories[1]], "quantity": "10"},
    {"id": 1, "name": "Equipment B", "slug": "equipment-b",
        "categories": [categories[0], categories[1], categories[2]], "quantity": "5-10"},
]


@api.get("/categories/", response_model=list[Category])
async def read_categories():
    return categories


@api.post("/categories/")
async def create_category(category: Category):
    categories.append(category)
    return category


def find_category(id) -> Optional[Category]:
    for category in categories:
        if category["id"] == id:
            return category
    return None


@api.delete("/categories/{id}", status_code=204)
def delete_category(id: int) -> None:
    category_to_remove = find_category(id)

    if category_to_remove is not None:
        categories.remove(category_to_remove)


@api.put("/categories/{id}", response_model=Category)
async def update_category(id: int, category: Category):
    update_category_encoded = jsonable_encoder(category)
    category_to_update = find_category(id)

    if category_to_update is not None:
        categories.remove(category_to_update)
        categories.append(update_category_encoded)
    return update_category_encoded


@api.get("/equipments/", response_model=list[Equipment])
async def read_equipments():
    return equipments


@api.post("/equipments/")
async def create_equipment(equipment: Equipment):
    categories.append(equipment)
    return equipment
