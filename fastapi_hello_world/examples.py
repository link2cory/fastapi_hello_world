from fastapi.routing import APIRouter

from typing import Dict, Union

router = APIRouter()


##############################################################################
# Path Parameters
##############################################################################
# use @router.REST_VERB(PATH_NAME) to tell FastApi this is a route function
@router.get("/")
async def read_root() -> Dict[str, str]:
    return {"Hello": "World"}


# create path variables like this: {path_var}
# the function will resolve it as the kwarg with the same name
# these are naturally resolved as strings unless you use type hinting
# in which case they are automatically converted
@router.get("/items/{item_id}")
def read_item(
    # path params will normally be passed into the function as strings
    # but if you use type hinting, they will automatically be converted
    # and documented appropriately
    item_id: int,
    # if you type hint the return values, they will be appropriately documented
) -> Dict[str, int]:
    return {"item_id": item_id}


# path params support enumerations as well and will document them automatically
from enum import Enum


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@router.get("/model/{model_name}")
# just be sure to type-hint the enumerated type
async def get_model(model_name: ModelName) -> Dict[str, str]:
    # you can compare the path param with the enumeration member
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    # or compare the value directly
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


##############################################################################
# Query Parameters
##############################################################################
from typing import Optional

# parameters passed into route functions that don't have corresponding path
# params will be interpreted as query params
@router.get("/query_params/")
def get_query(
    # query params get resolved as strings unless type-hinted
    # and are considered "required" unless given a default value
    # set the default value to None if truly optional
    my_query_param: int = 0,
    # you can have use boolean values which will be converted to true if passed as one
    # of the following values: 1, true, on, yes
    my_boolean_query_param: bool = False,
    # use Optional from typing for truly optional params
    my_optional_param: Optional[int] = None,
) -> Dict[str, str]:
    return {"hello": "world"}


# so if the path is
# http://domain/query_params/?my_query_param=10&myboolean_query_param=on
# then 10 will be passed in as my_query_param and True will be passed in
# as my_boolean_query_param

##############################################################################
# Body Params
##############################################################################
# to expect a request body, first create a BaseModel
from pydantic import BaseModel

class MyRequestBody(BaseModel):
    name: str
    price: float
    # you can make a member optional by giving it a default value
    optional: bool = False
    # or truly optional by setting the default to None
    truly_optional: Optional[bool] = None


# then just type-hint your param as the name of your new type
# FastAPI will implicitly interpret that as a request body
@router.post("/request_body/")
async def post_body(body: MyRequestBody) -> MyRequestBody:
    return body

# if you have a single body param, the api will expect a body that looks like:
# {
#   "name": "Foo",
#   "price": 42.0
# }

# but if you have multiple body params, the api will expect them to each be 
# embedded into a shared json object and keyed by their param name so a 
# function like this:
@router.post("/request_body_multiple/")
async def post_body_multiple(
    body_1: MyRequestBody, 
    body_2: MyRequestBody
) -> MyRequestBody:
    return body_1

# will expect a body that looks like:
# {
#   "body_1": {
#     "name": "Foo",
#     "price": 42.0"
#   },
#   "body_2": {
#     "name": "Bar",
#     "price": 0.0
#   }
# }

# use pydantic's Field method to setup validation for your request body models
from pydantic import Field
from typing import Any

class MyValidatedRequestBody(BaseModel):
    name: str = Field(None, title="The name of the item", max_length=300)
    price: float = Field(None, ge=0.0)

# you have access to all the same validation and metadata fields as shown below

# model fields can be subtypes:
from typing import List
class MySpecificSubtypeRequestBody(BaseModel):
    name: str
    price: float
    tags: List[str] = []

# you can also arbitrarily nest pydantic models:
class MyNestedType(BaseModel):
    name: str
    price: float

class MyRequestBodyWithNestedType(BaseModel):
    # of course they can still be optional
    nested_type: Optional[MyNestedType] = None
    tags: List[str] = []

# or you can use a pydantic model as the subtype of a list, set, etc
class MyRequestBodyWithNestedTypeList(BaseModel):
    nested_type_list: List[MyNestedType] = []
    tags: List[str] = []

# if you are expecting a list of your model you can specify that directly in
# the route function parameters:
@router.post("/request_body_list/")
async def post_body_list(
    *,
    bodys: List[MyRequestBody]
) -> Dict[str, str]:
    return {"hello": "world"}

# you may want to use a regular dict in lieu of a pydantic model.  The primary
# reason for this would if you need arbitrary keys:
@router.post("/request_body_dict_instead_of_model/")
async def post_body_dict_instead_of_model(
    weights: Dict[int, float]
) -> Dict[int, float]:
    return weights

# there are many more complex singular types that inherit from str
# see https://pydantic-docs.helpmanual.io/usage/types/

##############################################################################
# QUICK TIP - Since path params are detected by name, and since body params
#             are detected by type, the order in which you declare path, query
#             and body params doesn't matter.
#
#             The general rule is as follows:
#                 If the parameter X it is interpreted as Y
#                     matches a path parameter: Path param
#                     is a singular type: query param
#                     is a Pydantic model: request body
##############################################################################

##############################################################################
# Explicit Parameters
##############################################################################
# you can also use the Path(), Query(), and Body() methods to make the param
# category explicit, add validation, and add documentation
from fastapi.param_functions import Path, Query, Body

"""
@router.get("/explicit_query/")
async def get_explicit_query(
    # Set the default value of the param to be the appropriate function
    # with the parameters for whatever metadata is desired:
    my_query: str = Query(
        # default value, this is the only required value
        # if the param is required use ...
        # remember that Path params are always required
        default=None,
        # rename the param in the url
        alias=None,
        # add a title to the documentation
        title=None,
        # add a description to the documentation
        description=None,
        # numeric validator: only accepts values greater than what is passed
        gt=None,
        # numeric validator: only accepts values greater than or equal to what
        # is passed
        ge=None,
        # numeric validator: only accepts values less than what is passed
        lt=None,
        # numeric validator: only accepts values less than or equal to what
        # is passed
        le=None,
        # string validator: only accepts values with length greater than or
        # or equal to what is passed
        min_length=None,
        # string validator: only accepts values with length less than or equal
        # to what is passed
        max_length=None,
        # string validator: only accepts values that match the passed regex
        regex=None,
        # set to true to denote that this param is deprecated in the docs
        deprecated=None,
    )
) -> Dict[str, str]:
    return {"hello": "world"}
"""
# even if you aren't using any metadata, explicitly specifying the type of 
# param is sometimes necessary.  If you want to use a query param that is a 
# list:
from typing import List
@router.get("/query_list/")
async def get_query_list(
    # without explicitly stating this is a query, the param: query_list would be 
    # interpreted as a request body.
    query_list: List[str] = Query(None),
    # you can still set default values when using a multi-value query param
    query_list_with_defaults: List[str] = Query(["foo", "bar"]),
    # you can also just use list instead of List[str] but that is less precise
    # query_list_less_precise: list = Query(["foo", "bar"])
) -> Dict[str, List[str]]:
    return {"query_list": query_list} 

# you can add arbitrary fields to the Path, Query, Body, and Field methods
# these fields will be appended to the raw json schema and can be used for 
# annotation and documentation.


##############################################################################
# QUICK TIP: There is a caveat to using default values in general.  Python
#            can't handle optional params being declared before required ones
#            Fortunately the order in which values are interpreted doesn't 
#            matter as pointed out above, so you can rearrange the order 
#            of parameter declaration to suite your needs
#            Alternatively, you could just always be explicit with your params
#            Or use an * as the first parameter to the function.  This tells 
#            Python that the only parameters you are accepting will be kwargs
##############################################################################
# you can force a request body to use the embedded format even when using 
# a single body param by using an explicit body param and setting the special
# embed value to true as follows:
@router.post("/request_body_embed/")
async def post_body_embed(
    body: MyRequestBody = Body(..., embed=True)
) -> Dict[str, str]:
    return {"hello": "world"}


##############################################################################
# EXTRA DATA TYPES
##############################################################################
# out of the box FastAPI has builtin documentation support for the following 
# types in addition to the primitives:
# UUID
# datetime.datetime
# datetime.time
# datetime.timedelta
# frozenset
# bytes
# Decimal

##############################################################################
# COOKIE PARAMETERS
##############################################################################
# you can define Cookie parameters the same way you define Query and Path 
# params
from fastapi.param_functions import Cookie
@router.get("/cookies/")
async def get_cookies(*, cookie: str = Cookie(None)) -> Dict[str, str]:
    return {"cookie": cookie}

# you have all the same options as with Query and Path

##############################################################################
# HEADER PARAMETERS
##############################################################################
# you can define Header parameters the same way you define Query and Path 
# params
from fastapi.param_functions import Header
@router.get("/header/")
async def get_header(*, header: str = Header(None)) -> Dict[str, str]:
    return {"header": header}

# you have all the same options as with Query and Path

# most standard headers are seperated by hyphens, which are invalid in python
# so by default Header will convert the paremeter names characters from 
# underscores to hyphens
# also keep in mind that HTTP headers are case-insensetive so snake_case
# will work just fine
# you can disable this automatic conversion by setting the special parameter
# convert_underscores to False:
@router.get("/header_without_conversion/")
async def get_header_without_conversion(
    *, 
    header: str = Header(None, convert_underscores=False)
) -> Dict[str, str]:
    return {"header": header}

# if you need to receive duplicate headers you can define them using a list
# just like how you would with duplicate query params:
@router.get("/header_list/")
async def get_header_list(
    x_token: List[str] = Header(None)
) -> Dict[str, List[str]]:
    return {"X-Token values": x_token}

##############################################################################
# Response Model
##############################################################################
# you can declare the model to be used for responses with the response_model
# parameter in the path operation decorator
class MyResponseModel(BaseModel):
    name: str

@router.post("/response_model/", response_model=MyResponseModel)
async def post_response_model(body: MyRequestBody) -> MyResponseModel:
    response = MyResponseModel()
    response.name = body.name
    return response

# FastAPI will use the response_model to:
#  convert the output date to its type declaration
#  validate the data
#  add a json schema for the response, in the openAPI path operation
#  generate automatic documentation
#  *limit the output data to that of the model
# the return type of the function will not necessarily be the response_model, 
# it could be a regular dict, but it will be automatically converted

# we might have an input and output version of the same model for security
# purposes
class UserIn(BaseModel):
    username: str
    # we don't want to send this field to anyone ever, only receive it
    password: str
    email: str  
    full_name: Optional[str] = None

class UserOut(BaseModel):
    username: str
    # we omit the password field since we never want to output it
    email: str
    full_name: Optional[str] = None

@router.post("/user/", response_model=UserOut)
async def create_user(*, user: UserIn) -> UserIn:
    return user

# what actually gets sent out is the data following the UserOut model, that is 
# to say that even though we return exactly what we got, what the user will
# receive does not include the password field.
# the return type of the function does not dictate the final version of the 
# response

# you can manipulate what gets sent through this response_model by passing
# some special arguments to the path operation decorator

# if you have default values in your response_model and only want to send
# the data that was actually set you can use response_model_exclude_unset
@router.post(
    "/user_no_defaults_in_response/", 
    response_model=UserOut,
    response_model_exclude_unset=True
)
async def create_user_no_defaults_in_response(
    user: UserIn
) -> UserIn:
    return user

# now if the user declines to set their full name, it won't show up in the
# response.  Note that if the user sets their full name to the default value
# then it WILL show up in the response.

# you can use response_model_include and response_model_exclude to modify
# the chosen response model.  So a shortcut to the way the user password
# example above might be:
@router.post(
    "/user_shortcut/", 
    response_model=UserIn,
    response_model_exclude={"password"},
)
async def create_user_shortcut(
    user: UserIn
) -> UserIn:
    return user

# or another alternative
@router.post(
    "/user_another_shortcut/",
    response_model=UserIn,
    response_model_include={"username", "full_name", "email"}
) 
async def create_user_another_shortcut(
    user:UserIn
) -> UserIn:
    return user

##############################################################################
# QUICK TIP - Pydantic models have a method called dict() which converts the
#             values into a dictionary.  You can then send an unwrapped form
#             off this dictionary into a function as kwargs if you use the **
#             syntax: my_function(**model.dict()) 
#             there is some really good use case info and extension of this
#             idea in the docs at:
#             https://fastapi.tiangolo.com/tutorial/extra-models/
##############################################################################

# we also might want to use inheritence to keep code duplication down:

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserInNew(UserBase):
    password: str

class UserOutNew(UserBase):
    pass

# you can declare a response to be one of two types using a Union.  The docs
# will report the response type as being anyOf those two types

class BaseItem(BaseModel):
    description: str
    type: str

class CarItem(BaseItem):
    type = "car"

class PlaneItem(BaseItem):
    type = "plane"
    size: int

vehicles = {
    "vehicles1": {
        "description": "All my friends drive a low rider", 
        "type": "car"
    },
    "vehicles2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}
#@router.get("/vehicles/{vehicle_id}", response_model=Union[PlaneItem, CarItem])
#async def get_vehicle(vehicle_id: str) -> Dict[Any, Any]:
#    return vehicles[vehicle_id]

# somewhat similarly, you can declare the response_model to be a list of items
class Item(BaseModel):
    name: str
    description: str

items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]

@router.get("/items_list/", response_model=List[Item])
async def get_item_list() -> List[Dict[str, str]]:
    return items

##############################################################################
# Response Status Code
##############################################################################
# you can specify the response status code (if successful) as a parameter of 
# the routing operation decorator
from starlette.status import HTTP_201_CREATED # use for editor completion

@router.post("/create_a_thing/", status_code=HTTP_201_CREATED)
async def create_a_thing(name: str) -> Dict[str, str]:
    return {"name": name}

# TODO: Don't forget to come back here when we get to the advanced guide in 
# order to document how to change the return code dynamically

##############################################################################
# Form Data
##############################################################################
# Used similarly to Path, Query, Body, etc.  Just use if you need to accept 
# fields from a form instead of json
# you also need to pip install python-multipart to use this functionality
from fastapi.param_functions import Form

@router.post("/login_form/")
async def login(
    *, 
    username: str = Form(...), 
    password: str = Form(...)
) -> Dict[str, str]:
    return {"username": username}

# One caveat is that because form fields are just bodies encoded with the 
# media-type application/x-www-form-urlencoded, you can't have both
# form params and body params

##############################################################################
# Request Files 
##############################################################################
# you can accept a file-upload parameter using File
# make sure to run pip install python-multipart first
from fastapi.param_functions import File

@router.post("/files/")
async def create_file(file: bytes = File(...)) -> Dict[str, int]:
    return {"file_size": len(file)}

# this works fine for small files, but keep in mind that it will load the
# whole file as bytes into RAM

# use UploadFile if expecting bigger files.  This will flush the contents 
# of the file to disk if it exceeds an upper RAM limit
from fastapi.datastructures import UploadFile

@router.post("/files_that_are_big/")
async def create_big_file(file: UploadFile = File(...)) -> Dict[str, str]:
    return {"filename": file.filename}

# see the docs for what operations we can do with UploadFiles.  It seems
# pretty cool!  https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile


# just like forms, file uploads use a specially encoded request body
# of the form multipart/form-data so you can't also declare Body fields
# in the same endpoint.
# you can however use File and Form fields together

# you can upload multiple files at the same time by declaring the type to be
# a list of bytes or a list of UploadFile 
@router.post("/files_multiple/")
async def create_files(files: List[bytes] = File(...)) -> Dict[str, List[int]]:
    return {"file_sizes": [len(file) for file in files]}

@router.post("files_multiple_big/")
async def create_big_files(
    files: List[UploadFile] = File(...)
) -> Dict[str,List[str]]:
    return {"filenames": [file.filename for file in files]}

##############################################################################
# Handling Errors
##############################################################################
# to return HTTP responses with errors raise an HTTPException
from fastapi.exceptions import HTTPException

items_exception = {"foo": "The Foo Wrestlers"}

@router.get("/items_exception/{item_id}")
async def get_item_exception( item_id: str) -> Dict[str, str]:
    if item_id not in items_exception:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items_exception[item_id]}



