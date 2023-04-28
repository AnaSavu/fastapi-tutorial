import time
from typing import Optional, Annotated

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from enum import Enum
from pydantic import BaseModel

app = FastAPI()


items = {"foo": "The Foo Wrestlers"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    item_id: Optional[str] = None
    tags: Optional[list[str]] = []


class User(BaseModel):
    username: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.post("/items/save")
async def create_item(item: Item):
    return item

@app.post("/nested/parameters")
async def nested_parameters(user: User, item: Item):
    return {"user": user, "item": item}


@app.post("/nested/models")
async def nested_models(item: Item):
    return item


@app.post("/files")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/upload-file")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


@app.get("/item/{id}")
async def read_item(id: str):
    if id not in items:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "There goes my error"})
    return {"item": items[id]}


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]


@app.get("/items/")
async def read_items(commons: CommonsDep):
    return commons


@app.get("/users/")
async def read_users(commons: CommonsDep):
    return commons


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
