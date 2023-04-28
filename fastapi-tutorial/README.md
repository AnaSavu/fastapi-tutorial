# FastAPITutorial
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.\
The key features are: \
Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). One of the fastest Python frameworks available.\
Fast to code: Increase the speed to develop features by about 200% to 300%.\
Fewer bugs: Reduce about 40% of human (developer) induced errors.\
Intuitive: Great editor support. Completion everywhere. Less time debugging.\
Easy: Designed to be easy to use and learn. Less time reading docs.\
Short: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs.\
Robust: Get production-ready code. With automatic interactive documentation.\
Standards-based: Based on (and fully compatible with) the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.

## Install FastAPI

Run `pip install fastapi[all]`. Navigate to `http://localhost:8000/`. The application will automatically reload if you change any of the source files.

## Run the live server

Run `uvicorn main:app --reload`

## Interactive API docs

Go to http://127.0.0.1:8000/docs and automatically you will see an interactive API documentation which can work as a test playground as well

## Create a FastAPI instance
```
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
```
This ```app``` instance is the same referred in the ```uvicorn``` command

## Create paths
### Named also endpoints or routes

For example, a URL like: https://example.com/items/foo -> the path is: /items/foo

## Operations
* POST: to Create data
* GET: to Read data
* PUT: to Update data
* DELETE: to Delete data
* OPTIONS
* HEAD
* PATCH
* TRACE

To define the operation is wanted the use, use the ```app``` instance as in the following example: ```@app.get(<path>)```

## Path Parameters
You can declare or not the type of a path parameter in the function, using standard Python type annotations
```
    @app.get("/hello/{name}")
    async def say_hello(name: str):
        return {"message": f"Hello {name}"}
```

If the type of the parameter is declared, but not respected, the request will fail and in the browser it can be seen the HTTP error

## Request Body
First, you need to import ```BaseModel``` from ```pydantic```.\
Then you declare your data model as a class that inherits from ```BaseModel```.
```
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.post("/items/")
async def create_item(item: Item):
    return item
```
In the model above, it declares a JSON object like:\
```
{
    "name": "Foo",
    "description": "An optional description",
    "price": 45.2,
    "tax": 3.5
}
```
But because description and tax were declared as optional, they can not appear in the JSON object.\
Moreover, it works similar to path parameters

## Nested Models
You can define an attribute to be a subtype, for example, a list:\
```
class Item(BaseModel):
    item_id: Optional[str] = None
    tags: Optional[list[str]] = []
```

## Request Files
You can define files to be uploaded by the client using ```File```.\
First, it is needed to install python-multipart by running ```pip install python-multipart```.\
```
from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
```


## Handling Errors
There are many situations in where you need to notify an error to a client that is using your API.\
You could need to tell the client that:\

* The client doesn't have enough privileges for that operation.
* The client doesn't have access to that resource.
* The item the client was trying to access doesn't exist.

For this, it is used ```HTTPException```.\
Because it is a Python exception, it is raise. \
The benefit of raising an exception over returning a value will be more evident in the section about Dependencies and Security.

### Add custom headers
There are some situations in where it's useful to be able to add custom headers to the HTTP error. For example, for some types of security.\
```
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}

@app.get("/item/{id}")
async def read_item(id: str):
    if id not in items:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "There goes my error"})
    return {"item": items[id]}
```

## Dependencies
The framework has a very powerful but intuitive Dependency Injection system.\
Dependency Injection means that there is a way for your code to declare things that it requires to work and use: "dependencies".\
And then, that system (in this case FastAPI) will take care of doing whatever is needed to provide your code with those needed dependencies.

### First steps
1. Import ```Depends```
   ```
    from typing import Annotated

    from fastapi import Depends, FastAPI
   
    app = FastAPI()
    ```
2. Create a dependency
    - It is just a function that can take all the same parameters that a path operation function can take
    - It returns anything
    ```
    async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
        return {"q": q, "skip": skip, "limit": limit}
   ```
   - in the above case, the dependency expects:
     * an optional query parameter ```q``` that is a ```str```
     * an optional query parameter ```skip``` that is an ```int```, and by default is 0.
     * An optional query parameter ```limit``` that is an ```int```, and by default is 100

3. Declare the dependency in the dependant
   ```
    @app.get("/items/")
    async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
        return commons


    @app.get("/users/")
    async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
        return commons
   ```
   
Whenever a new request arrives, FastAPI will take care of:\

* Calling your dependency ("dependable") function with the correct parameters.
* Get the result from your function.
* Assign that result to the parameter in your path operation function.
![Screenshot 2023-04-28 at 1.05.12 PM.png](..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fvar%2Ffolders%2Fd0%2Fyr03mqbj24v_lqftgn_0q2l80000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_LLvkBs%2FScreenshot%202023-04-28%20at%201.05.12%20PM.png)


## Middleware

A "middleware" is a function that works with every request before it is processed by any specific path operation. And also with every response before returning it.\
* It takes each request that comes to your application.
* It can then do something to that request or run any needed code.
* Then it passes the request to be processed by the rest of the application (by some path operation).
* It then takes the response generated by the application (by some path operation).
* It can do something to that response or run any needed code.
* Then it returns the response.
\
To create a middleware, use the decorator ```@app.middleware("http")``` on top of a function.\
The middleware function receives:
* the request
* a function ```call_next``` that will receive the ```request``` as parameter
* you can then further modify the ```response``` before returning it

## Concurrency and async
If you are using third party libraries that tell you to call them with await, like:
```results = await some_library()```
Then, declare your path operation functions with async def like:
```
@app.get('/')
async def read_results():
    results = await some_library()
    return results
```
You can only use await inside of functions created with async def.

## CORS (Cross-Origin Resource Sharing)