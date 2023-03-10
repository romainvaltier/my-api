from fastapi import FastAPI, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional, Union
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import pandas as pd

description = """

My-API helps you do awesome stuff. 🚀

__Source :__ [https://github.com/romainvaltier/my-api.git](https://github.com/romainvaltier/my-api.git)

__Additional information :__ [https://github.com/romainvaltier/my-api#readme](https://github.com/romainvaltier/my-api#readme)

__How to use :__

- Only authentified users can get access to the API
- Only **Captain Nemo** can access to create, update and delete endpoints
- Captain Nemo:
  - username = captain
  - password = nemo
- Ned Land:
  - username = ned
  - password = land
- Pierre Arronax
  - username = pierre
  - password = arronax

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
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@api.get("/")
async def get_index():
    return {"message": "Welcome to {} !".format(api.title)}


@api.get("/user")
async def current_user(username: str = Depends(get_current_user)):
    return {"message": "Hello {}".format(username)}


# Category

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


def find_category(id) -> Optional[Category]:
    for category in categories:
        if category["id"] == id:
            return category
    return None


def category_used(id):
    categories_used = set(
        category["id"] for equipment in equipments for category in equipment["categories"])
    if id in categories_used:
        return True
    else:
        return False


def category_name_used(name):
    category_names_used = set(category["name"] for category in categories)
    if name in category_names_used:
        return True
    else:
        return False


@api.get("/category/", response_model=list[Category])
async def list_categories(parent: str = Query(default=None), username: str = Depends(get_current_user)):
    if username not in users:
        raise HTTPException(status_code=400, detail="Invalid User")
    if parent is not None:
        results = [
            category for category in categories if category['parent'] == parent]
    else:
        results = categories
    return results


@api.get("/category/{id}", response_model=Category)
async def retrieve_category(id: int = 0, username: str = Depends(get_current_user)):
    if username not in users:
        raise HTTPException(status_code=400, detail="Invalid User")
    category_to_retrieve = find_category(id)
    if category_to_retrieve is not None:
        return category_to_retrieve
    else:
        raise HTTPException(status_code=204, detail="No Content")


@api.post("/category/")
async def create_category(category: Category, username: str = Depends(get_current_user)):
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    create_category_encoded = jsonable_encoder(category)
    if not category_name_used(create_category_encoded["name"]):
        categories.append(create_category_encoded)
        return create_category_encoded
    else:
        raise HTTPException(
            status_code=400, detail="Cannot create category : name already exists")


@api.delete("/category/{id}", status_code=204)
def delete_category(id: int, username: str = Depends(get_current_user)) -> None:
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    category_to_remove = find_category(id)
    if category_to_remove is not None:
        if not category_used(id):
            categories.remove(category_to_remove)
        else:
            raise HTTPException(
                status_code=400, detail="Cannot delete category : still in use")


@api.put("/category/{id}", response_model=Category)
async def update_category(id: int, category: Category, username: str = Depends(get_current_user)):
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    update_category_encoded = jsonable_encoder(category)
    category_to_update = find_category(id)
    if category_to_update is not None:
        categories.remove(category_to_update)
        categories.append(update_category_encoded)
    return update_category_encoded


# Equipment


class Equipment(BaseModel):
    id: int
    name: Optional[str] = None
    slug: str
    categories: Optional[list[Category]] = None
    quantity: Optional[int] = 0


equipments = [
    {"id": 0, "name": "Equipment A", "slug": "equipment-a",
        "categories": [categories[0], categories[1]], "quantity": 10},
    {"id": 1, "name": "Equipment B", "slug": "equipment-b",
        "categories": [categories[0], categories[1], categories[2]], "quantity": 5},
    {"id": 2, "name": "Equipment A", "slug": "equipment-a",
        "categories": [categories[0], categories[1]], "quantity": 0},
    {"id": 3, "name": "Equipment B", "slug": "equipment-b",
        "categories": [categories[0], categories[1], categories[2]], "quantity": 15},
]


def find_equipment(id) -> Optional[Equipment]:
    for equipment in equipments:
        if equipment["id"] == id:
            return equipment
    return None


@api.get("/equipment/", response_model=list[Equipment])
async def list_equipments(quantity_min: int = Query(default=0, ge=0), quantity_max: int = Query(default=0, ge=0), username: str = Depends(get_current_user)):
    if username not in users:
        raise HTTPException(status_code=400, detail="Invalid User")
    if quantity_max > quantity_min:
        results = [equipment for equipment in equipments if quantity_min <=
                   equipment['quantity'] <= quantity_max]
    else:
        results = [equipment for equipment in equipments if equipment['quantity']
                   >= quantity_min]
    return results


@api.get("/equipment/{id}", response_model=Equipment)
async def retrieve_equipment(id: int = 0, username: str = Depends(get_current_user)):
    if username not in users:
        raise HTTPException(status_code=400, detail="Invalid User")
    equipment_to_retrieve = find_equipment(id)
    if equipment_to_retrieve is not None:
        return equipment_to_retrieve
    else:
        raise HTTPException(status_code=204, detail="No Content")


@api.post("/equipment/")
async def create_equipment(equipment: Equipment, username: str = Depends(get_current_user)):
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    create_equipment_encoded = jsonable_encoder(equipment)
    equipments.append(create_equipment_encoded)
    return create_equipment_encoded


@api.delete("/equipment/{id}", status_code=204)
def delete_equipment(id: int, username: str = Depends(get_current_user)) -> None:
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    equipment_to_remove = find_equipment(id)
    if equipment_to_remove is not None:
        equipments.remove(equipment_to_remove)


@api.put("/equipment/{id}", response_model=Equipment)
async def update_equipment(id: int, equipment: Equipment, username: str = Depends(get_current_user)):
    if username != "captain":
        raise HTTPException(status_code=400, detail="Invalid User")
    update_equipment_encoded = jsonable_encoder(equipment)
    equipment_to_update = find_equipment(id)
    if equipment_to_update is not None:
        equipments.remove(equipment_to_update)
        equipments.append(update_equipment_encoded)
    return update_equipment_encoded
